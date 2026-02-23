from datetime import datetime

from sqlalchemy import Column, Enum, JSON, Text
from sqlalchemy import DateTime
from sqlmodel import Field

from app.domain.entities.abstract_entity import AbstractEntity
from app.domain.enums.priority_enum import PriorityEnum
from app.domain.enums.ticket_status_enum import TicketStatusEnum


class Ticket(AbstractEntity, table=True):
    __tablename__ = "tickets"

    title: str = Field(nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=False))
    status: TicketStatusEnum = Field(
        sa_column=Column(
            Enum(TicketStatusEnum, name="ticket_status"),
            nullable=False,
            server_default=TicketStatusEnum.OPEN.value,
        )
    )
    priority: PriorityEnum = Field(
        sa_column=Column(
            Enum(PriorityEnum, name="ticket_priority"),
            nullable=False,
            server_default=PriorityEnum.MEDIUM.value,
        )
    )

    created_by_id: int = Field(foreign_key="users.id", nullable=False)
    assigned_to_id: int | None = Field(default=None, foreign_key="users.id", nullable=True)
    team_leader_id: int | None = Field(default=None, foreign_key="users.id", nullable=True)

    watchers: list[int] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    closed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
