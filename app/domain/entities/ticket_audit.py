from sqlalchemy import Column, String, Text
from sqlmodel import Field

from app.domain.entities.abstract_entity import AbstractEntity


class TicketAudit(AbstractEntity, table=True):
    __tablename__ = "ticket_audits"

    ticket_id: int = Field(foreign_key="tickets.id", nullable=False, index=True)
    actor_user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    action: str = Field(sa_column=Column(String(64), nullable=False))
    from_value: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    to_value: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
