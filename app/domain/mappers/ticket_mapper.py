from __future__ import annotations

from app.domain.dtos.ticket_dto import CreateTicketRequestDTO, TicketResponseDTO
from app.domain.entities.ticket import Ticket


class TicketMapper:
    def to_entity(self, dto: CreateTicketRequestDTO, *, created_by_id: int) -> Ticket:
        return Ticket(
            title=dto.title.strip(),
            description=dto.description.strip(),
            priority=dto.priority,
            created_by_id=created_by_id,
            assigned_to_id=dto.assigned_to_id,
            team_leader_id=dto.team_leader_id,
            watchers=dto.watchers,
        )

    def to_dto(self, entity: Ticket) -> TicketResponseDTO:
        return TicketResponseDTO(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
            priority=entity.priority,
            created_by_id=entity.created_by_id,
            assigned_to_id=entity.assigned_to_id,
            team_leader_id=entity.team_leader_id,
            watchers=entity.watchers,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            closed_at=entity.closed_at,
        )
