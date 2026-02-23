from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.priority_enum import PriorityEnum
from app.domain.enums.ticket_status_enum import TicketStatusEnum


class CreateTicketRequestDTO(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Customer cannot login",
                "description": "Customer reports invalid credentials after password reset.",
                "priority": "HIGH",
                "assigned_to_id": 12,
                "team_leader_id": 3,
                "watchers": [3, 12],
            }
        }
    )

    title: str = Field(min_length=1, max_length=160, description="Ticket title.")
    description: str = Field(min_length=1, description="Detailed ticket description.")
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        description="Ticket priority.",
    )
    assigned_to_id: int | None = Field(
        default=None,
        ge=1,
        description="Assigned agent user id.",
    )
    team_leader_id: int | None = Field(
        default=None,
        ge=1,
        description="Team leader responsible for the ticket queue.",
    )
    watchers: list[int] = Field(
        default_factory=list,
        description="Optional list of user ids watching the ticket.",
    )


class UpdateTicketRequestDTO(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Customer cannot login (updated)",
                "description": "Issue reproduced in staging and assigned for fix.",
                "status": "IN_PROGRESS",
                "priority": "URGENT",
                "assigned_to_id": 18,
                "team_leader_id": 3,
                "watchers": [3, 12, 18],
            }
        }
    )

    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, min_length=1)
    status: TicketStatusEnum | None = Field(default=None)
    priority: PriorityEnum | None = Field(default=None)
    assigned_to_id: int | None = Field(default=None, ge=1)
    team_leader_id: int | None = Field(default=None, ge=1)
    watchers: list[int] | None = Field(default=None)


class TicketResponseDTO(BaseModel):
    id: int = Field(description="Ticket unique identifier.", examples=[101])
    title: str = Field(description="Ticket title.")
    description: str = Field(description="Detailed ticket description.")
    status: TicketStatusEnum = Field(description="Current ticket status.")
    priority: PriorityEnum = Field(description="Current ticket priority.")
    created_by_id: int = Field(description="User id who created the ticket.", examples=[7])
    assigned_to_id: int | None = Field(default=None, description="Assigned agent user id.")
    team_leader_id: int | None = Field(default=None, description="Team leader user id.", examples=[3])
    watchers: list[int] = Field(
        default_factory=list,
        description="User ids following the ticket.",
    )
    is_active: bool = Field(description="Ticket active status.")
    created_at: datetime = Field(
        description="Timestamp when the ticket was created.",
        examples=["2026-02-23T10:45:00Z"],
    )
    updated_at: datetime = Field(
        description="Timestamp when the ticket was last updated.",
        examples=["2026-02-23T11:15:00Z"],
    )
    closed_at: datetime | None = Field(
        default=None,
        description="Timestamp when the ticket was closed.",
        examples=["2026-02-24T09:00:00Z"],
    )
