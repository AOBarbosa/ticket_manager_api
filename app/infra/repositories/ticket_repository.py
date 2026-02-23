from abc import ABC

from app.domain.entities.ticket import Ticket
from app.infra.repositories.abstract_repository import AbstractRepository


class TicketRepository(AbstractRepository[Ticket], ABC):
    pass
