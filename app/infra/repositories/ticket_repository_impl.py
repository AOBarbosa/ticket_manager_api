from typing import List, Optional

from sqlmodel import Session, select

from app.domain.entities.ticket import Ticket
from app.infra.repositories.ticket_repository import TicketRepository


class TicketRepositoryImpl(TicketRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, entity: Ticket) -> Ticket:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[Ticket]:
        return self.session.get(Ticket, entity_id)

    def update(self, entity: Ticket) -> Ticket:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> None:
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()

    def get_all(self) -> List[Ticket]:
        query = select(Ticket)
        return list(self.session.exec(query).all())
