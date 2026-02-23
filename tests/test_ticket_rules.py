from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.application.services.ticket_service import TicketService
from app.application.validators.ticket_validator import TicketValidator
from app.domain.dtos.ticket_dto import CreateTicketRequestDTO, UpdateTicketRequestDTO
from app.domain.entities.ticket import Ticket
from app.domain.entities.ticket_audit import TicketAudit
from app.domain.enums.priority_enum import PriorityEnum
from app.domain.enums.roles_enum import UserRole
from app.domain.enums.ticket_status_enum import TicketStatusEnum
from app.domain.mappers.ticket_mapper import TicketMapper


class FakeTicketRepository:
    def __init__(self):
        self._items: dict[int, Ticket] = {}
        self._next_id = 1

    def create(self, entity: Ticket) -> Ticket:
        now = datetime.now(timezone.utc)
        entity.id = self._next_id
        self._next_id += 1
        entity.created_at = now
        entity.updated_at = now
        if entity.status is None:
            entity.status = TicketStatusEnum.OPEN
        if entity.priority is None:
            entity.priority = PriorityEnum.MEDIUM
        self._items[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: int) -> Ticket | None:
        return self._items.get(entity_id)

    def update(self, entity: Ticket) -> Ticket:
        entity.updated_at = datetime.now(timezone.utc)
        self._items[entity.id] = entity
        return entity

    def delete(self, entity_id: int) -> None:
        self._items.pop(entity_id, None)

    def get_all(self) -> list[Ticket]:
        return list(self._items.values())


class FakeTicketAuditRepository:
    def __init__(self):
        self.events: list[TicketAudit] = []
        self._next_id = 1

    def create(self, entity: TicketAudit) -> TicketAudit:
        entity.id = self._next_id
        self._next_id += 1
        entity.created_at = datetime.now(timezone.utc)
        entity.updated_at = entity.created_at
        self.events.append(entity)
        return entity

    def create_many(self, entities: list[TicketAudit]) -> list[TicketAudit]:
        return [self.create(entity) for entity in entities]

    def get_by_id(self, entity_id: int) -> TicketAudit | None:
        for event in self.events:
            if event.id == entity_id:
                return event
        return None

    def update(self, entity: TicketAudit) -> TicketAudit:
        return entity

    def delete(self, entity_id: int) -> None:
        self.events = [event for event in self.events if event.id != entity_id]

    def get_all(self) -> list[TicketAudit]:
        return list(self.events)


def _actor(user_id: int, role: UserRole):
    return SimpleNamespace(id=user_id, role=role)


@pytest.fixture
def service():
    repo = FakeTicketRepository()
    audit_repo = FakeTicketAuditRepository()
    return TicketService(
        repository=repo,
        mapper=TicketMapper(),
        validator=TicketValidator(),
        audit_repository=audit_repo,
    )


def _create_ticket(service: TicketService, *, actor_id: int = 1):
    dto = CreateTicketRequestDTO(
        title="Falha no login",
        description="Cliente não consegue autenticar",
        priority=PriorityEnum.HIGH,
        assigned_to_id=2,
        team_leader_id=3,
        watchers=[3, 2],
    )
    return service.create(dto, actor=_actor(actor_id, UserRole.CUSTOMER))


def test_customer_only_lists_own_tickets(service: TicketService):
    own = _create_ticket(service, actor_id=10)
    _create_ticket(service, actor_id=11)

    tickets = service.get_all(actor=_actor(10, UserRole.CUSTOMER))

    assert len(tickets) == 1
    assert tickets[0].id == own.id


def test_agent_cannot_change_priority(service: TicketService):
    created = _create_ticket(service, actor_id=10)

    with pytest.raises(Exception) as exc:
        service.update(
            created.id,
            UpdateTicketRequestDTO(priority=PriorityEnum.URGENT),
            actor=_actor(2, UserRole.AGENT),
        )

    assert "Forbidden" in str(exc.value)


def test_team_leader_can_assign_and_change_priority(service: TicketService):
    created = _create_ticket(service, actor_id=10)

    updated = service.update(
        created.id,
        UpdateTicketRequestDTO(assigned_to_id=20, priority=PriorityEnum.URGENT),
        actor=_actor(3, UserRole.TEAM_LEADER),
    )

    assert updated.assigned_to_id == 20
    assert updated.priority == PriorityEnum.URGENT


def test_close_requires_resolved_status(service: TicketService):
    created = _create_ticket(service, actor_id=10)

    with pytest.raises(Exception) as exc:
        service.update(
            created.id,
            UpdateTicketRequestDTO(status=TicketStatusEnum.CLOSED),
            actor=_actor(3, UserRole.TEAM_LEADER),
        )

    assert "RESOLVED" in str(exc.value)


def test_customer_can_close_own_ticket_when_resolved(service: TicketService):
    created = _create_ticket(service, actor_id=10)

    service.update(
        created.id,
        UpdateTicketRequestDTO(status=TicketStatusEnum.RESOLVED),
        actor=_actor(2, UserRole.AGENT),
    )
    closed = service.update(
        created.id,
        UpdateTicketRequestDTO(status=TicketStatusEnum.CLOSED),
        actor=_actor(10, UserRole.CUSTOMER),
    )

    assert closed.status == TicketStatusEnum.CLOSED
    assert closed.closed_at is not None


def test_delete_is_soft_and_admin_only(service: TicketService):
    created = _create_ticket(service, actor_id=10)

    with pytest.raises(Exception):
        service.delete(created.id, actor=_actor(3, UserRole.TEAM_LEADER))

    service.delete(created.id, actor=_actor(99, UserRole.ADMIN))
    with pytest.raises(Exception):
        service.get_by_id(created.id, actor=_actor(99, UserRole.ADMIN))
