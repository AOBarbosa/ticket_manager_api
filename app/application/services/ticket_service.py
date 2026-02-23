from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.application.validators.ticket_validator import TicketValidator
from app.domain.dtos.ticket_dto import CreateTicketRequestDTO, TicketResponseDTO, UpdateTicketRequestDTO
from app.domain.dtos.user_dto import UserResponseDTO
from app.domain.entities.ticket import Ticket
from app.domain.entities.ticket_audit import TicketAudit
from app.domain.enums.roles_enum import UserRole
from app.domain.enums.ticket_status_enum import TicketStatusEnum
from app.domain.mappers.ticket_mapper import TicketMapper
from app.infra.repositories.ticket_audit_repository import TicketAuditRepository
from app.infra.repositories.ticket_repository import TicketRepository


class TicketService:
    REOPEN_WINDOW_DAYS = 7

    def __init__(
        self,
        repository: TicketRepository,
        mapper: TicketMapper,
        validator: TicketValidator,
        audit_repository: TicketAuditRepository,
    ) -> None:
        self.repository = repository
        self.mapper = mapper
        self.validator = validator
        self.audit_repository = audit_repository

    def create(self, dto: CreateTicketRequestDTO, *, actor: UserResponseDTO) -> TicketResponseDTO:
        ticket = self.mapper.to_entity(dto, created_by_id=actor.id)
        ticket.watchers = self._normalize_watchers(ticket.watchers)

        self.validator.validate_create(ticket)
        saved = self.repository.create(ticket)
        self._audit(
            ticket_id=saved.id,
            actor_user_id=actor.id,
            action="CREATE",
            to_value=f"status={saved.status.value},priority={saved.priority.value}",
        )
        return self.mapper.to_dto(saved)

    def get_all(self, *, actor: UserResponseDTO) -> list[TicketResponseDTO]:
        tickets = [ticket for ticket in self.repository.get_all() if ticket.is_active]

        if actor.role in (UserRole.ADMIN, UserRole.TEAM_LEADER):
            visible = tickets
        elif actor.role == UserRole.CUSTOMER:
            visible = [ticket for ticket in tickets if ticket.created_by_id == actor.id]
        elif actor.role == UserRole.AGENT:
            visible = [ticket for ticket in tickets if ticket.assigned_to_id == actor.id]
        else:
            visible = []

        return [self.mapper.to_dto(ticket) for ticket in visible]

    def get_by_id(self, ticket_id: int, *, actor: UserResponseDTO) -> TicketResponseDTO:
        ticket = self.repository.get_by_id(ticket_id)
        self.validator.validate_found(ticket, not_found_detail="Ticket not found")
        self._ensure_active(ticket)
        self._ensure_can_view_ticket(actor=actor, ticket=ticket)
        return self.mapper.to_dto(ticket)

    def update(self, ticket_id: int, dto: UpdateTicketRequestDTO, *, actor: UserResponseDTO) -> TicketResponseDTO:
        ticket = self.repository.get_by_id(ticket_id)
        self.validator.validate_found(ticket, not_found_detail="Ticket not found")
        self._ensure_active(ticket)

        self._ensure_can_update_ticket(actor=actor, ticket=ticket, dto=dto)
        audits: list[TicketAudit] = []

        if dto.title is not None:
            ticket.title = dto.title.strip()
        if dto.description is not None:
            ticket.description = dto.description.strip()

        if dto.status is not None:
            self._ensure_status_transition_allowed(actor=actor, ticket=ticket, next_status=dto.status)
            previous_status = ticket.status
            ticket.status = dto.status

            if dto.status == TicketStatusEnum.CLOSED:
                ticket.closed_at = datetime.now(timezone.utc)
            elif previous_status == TicketStatusEnum.CLOSED and dto.status != TicketStatusEnum.CLOSED:
                ticket.closed_at = None

            if previous_status != dto.status:
                audits.append(
                    self._build_audit(
                        ticket_id=ticket.id,
                        actor_user_id=actor.id,
                        action="CHANGE_STATUS",
                        from_value=previous_status.value,
                        to_value=dto.status.value,
                    )
                )

        if dto.priority is not None:
            previous_priority = ticket.priority
            ticket.priority = dto.priority
            if previous_priority != dto.priority:
                audits.append(
                    self._build_audit(
                        ticket_id=ticket.id,
                        actor_user_id=actor.id,
                        action="CHANGE_PRIORITY",
                        from_value=previous_priority.value,
                        to_value=dto.priority.value,
                    )
                )

        if dto.assigned_to_id is not None:
            previous_assigned = ticket.assigned_to_id
            ticket.assigned_to_id = dto.assigned_to_id
            if previous_assigned != dto.assigned_to_id:
                audits.append(
                    self._build_audit(
                        ticket_id=ticket.id,
                        actor_user_id=actor.id,
                        action="ASSIGN_AGENT",
                        from_value=str(previous_assigned) if previous_assigned is not None else None,
                        to_value=str(dto.assigned_to_id),
                    )
                )

        if dto.team_leader_id is not None:
            previous_leader = ticket.team_leader_id
            ticket.team_leader_id = dto.team_leader_id
            if previous_leader != dto.team_leader_id:
                audits.append(
                    self._build_audit(
                        ticket_id=ticket.id,
                        actor_user_id=actor.id,
                        action="ASSIGN_TEAM_LEADER",
                        from_value=str(previous_leader) if previous_leader is not None else None,
                        to_value=str(dto.team_leader_id),
                    )
                )

        if dto.watchers is not None:
            ticket.watchers = self._normalize_watchers(dto.watchers)

        self.validator.validate_update(ticket)
        updated = self.repository.update(ticket)

        if audits:
            self.audit_repository.create_many(audits)

        return self.mapper.to_dto(updated)

    def delete(self, ticket_id: int, *, actor: UserResponseDTO) -> None:
        ticket = self.repository.get_by_id(ticket_id)
        self.validator.validate_found(ticket, not_found_detail="Ticket not found")
        self._ensure_active(ticket)

        if actor.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        ticket.is_active = False
        self.repository.update(ticket)
        self._audit(
            ticket_id=ticket.id,
            actor_user_id=actor.id,
            action="SOFT_DELETE",
            from_value="is_active=True",
            to_value="is_active=False",
        )

    def _ensure_active(self, ticket: Ticket) -> None:
        if not ticket.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    def _ensure_can_view_ticket(self, *, actor: UserResponseDTO, ticket: Ticket) -> None:
        if actor.role in (UserRole.ADMIN, UserRole.TEAM_LEADER):
            return
        if actor.role == UserRole.CUSTOMER and ticket.created_by_id == actor.id:
            return
        if actor.role == UserRole.AGENT and ticket.assigned_to_id == actor.id:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def _ensure_can_update_ticket(
        self, *, actor: UserResponseDTO, ticket: Ticket, dto: UpdateTicketRequestDTO
    ) -> None:
        if actor.role == UserRole.ADMIN:
            return

        is_assignment_change = dto.assigned_to_id is not None or dto.team_leader_id is not None
        is_priority_change = dto.priority is not None
        is_status_change = dto.status is not None
        has_non_status_update = any(value is not None for value in (dto.title, dto.description, dto.watchers))

        if actor.role == UserRole.TEAM_LEADER:
            return

        if actor.role == UserRole.AGENT:
            if ticket.assigned_to_id != actor.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            if is_assignment_change or is_priority_change:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            if has_non_status_update and not is_status_change:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            return

        if actor.role == UserRole.CUSTOMER:
            if ticket.created_by_id != actor.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            if is_assignment_change or is_priority_change or has_non_status_update:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            if dto.status is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            return

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def _ensure_status_transition_allowed(
        self, *, actor: UserResponseDTO, ticket: Ticket, next_status: TicketStatusEnum
    ) -> None:
        current_status = ticket.status

        if actor.role == UserRole.ADMIN:
            return

        if next_status == TicketStatusEnum.CLOSED:
            if current_status != TicketStatusEnum.RESOLVED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ticket must be RESOLVED before CLOSED",
                )
            if actor.role == UserRole.TEAM_LEADER:
                return
            if actor.role == UserRole.CUSTOMER and ticket.created_by_id == actor.id:
                return
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        if current_status == TicketStatusEnum.CLOSED and next_status != TicketStatusEnum.CLOSED:
            if actor.role not in (UserRole.TEAM_LEADER, UserRole.CUSTOMER):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            if actor.role == UserRole.CUSTOMER and ticket.created_by_id != actor.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            if not ticket.closed_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ticket has no close timestamp",
                )
            if datetime.now(timezone.utc) - ticket.closed_at > timedelta(days=self.REOPEN_WINDOW_DAYS):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reopen window expired",
                )

        if actor.role == UserRole.AGENT and ticket.assigned_to_id != actor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    @staticmethod
    def _normalize_watchers(watchers: list[int]) -> list[int]:
        return list(dict.fromkeys(watchers))

    def _audit(
        self,
        *,
        ticket_id: int,
        actor_user_id: int,
        action: str,
        from_value: str | None = None,
        to_value: str | None = None,
    ) -> None:
        self.audit_repository.create(
            self._build_audit(
                ticket_id=ticket_id,
                actor_user_id=actor_user_id,
                action=action,
                from_value=from_value,
                to_value=to_value,
            )
        )

    @staticmethod
    def _build_audit(
        *,
        ticket_id: int,
        actor_user_id: int,
        action: str,
        from_value: str | None = None,
        to_value: str | None = None,
    ) -> TicketAudit:
        return TicketAudit(
            ticket_id=ticket_id,
            actor_user_id=actor_user_id,
            action=action,
            from_value=from_value,
            to_value=to_value,
        )
