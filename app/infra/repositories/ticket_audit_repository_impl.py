from typing import List, Optional

from sqlmodel import Session, select

from app.domain.entities.ticket_audit import TicketAudit
from app.infra.repositories.ticket_audit_repository import TicketAuditRepository


class TicketAuditRepositoryImpl(TicketAuditRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, entity: TicketAudit) -> TicketAudit:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def create_many(self, entities: list[TicketAudit]) -> list[TicketAudit]:
        if not entities:
            return []
        self.session.add_all(entities)
        self.session.commit()
        for entity in entities:
            self.session.refresh(entity)
        return entities

    def get_by_id(self, entity_id: int) -> Optional[TicketAudit]:
        return self.session.get(TicketAudit, entity_id)

    def update(self, entity: TicketAudit) -> TicketAudit:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> None:
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()

    def get_all(self) -> List[TicketAudit]:
        query = select(TicketAudit)
        return list(self.session.exec(query).all())
