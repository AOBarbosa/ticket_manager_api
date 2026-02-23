from fastapi import Depends
from sqlmodel import Session

from app.application.services.ticket_service import TicketService
from app.application.validators.ticket_validator import TicketValidator
from app.core.db.session import get_session
from app.domain.mappers.ticket_mapper import TicketMapper
from app.infra.repositories.ticket_audit_repository_impl import TicketAuditRepositoryImpl
from app.infra.repositories.ticket_repository_impl import TicketRepositoryImpl


def get_ticket_service(session: Session = Depends(get_session)) -> TicketService:
    repo = TicketRepositoryImpl(session)
    audit_repo = TicketAuditRepositoryImpl(session)
    mapper = TicketMapper()
    validator = TicketValidator()
    return TicketService(repo, mapper, validator, audit_repo)
