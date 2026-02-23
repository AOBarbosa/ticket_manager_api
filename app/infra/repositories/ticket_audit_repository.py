from abc import ABC, abstractmethod

from app.domain.entities.ticket_audit import TicketAudit
from app.infra.repositories.abstract_repository import AbstractRepository


class TicketAuditRepository(AbstractRepository[TicketAudit], ABC):
    @abstractmethod
    def create_many(self, entities: list[TicketAudit]) -> list[TicketAudit]:
        raise NotImplementedError
