from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status

from app.domain.entities.ticket import Ticket


class TicketValidator:
    def validate_found(
        self, ticket: Optional[Ticket], *, not_found_detail: str = "Resource not found"
    ) -> None:
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)

    def validate_create(self, ticket: Ticket) -> None:
        if not ticket.title or not ticket.title.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title is required")
        if not ticket.description or not ticket.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description is required",
            )

        self._validate_user_ids(ticket)
        self._validate_watchers(ticket.watchers)

    def validate_update(self, ticket: Ticket) -> None:
        if not ticket.title or not ticket.title.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title is required")
        if not ticket.description or not ticket.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description is required",
            )

        self._validate_user_ids(ticket)
        self._validate_watchers(ticket.watchers)

    def _validate_user_ids(self, ticket: Ticket) -> None:
        if ticket.created_by_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="created_by_id must be positive"
            )

        if ticket.assigned_to_id is not None and ticket.assigned_to_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="assigned_to_id must be positive"
            )

        if ticket.team_leader_id is not None and ticket.team_leader_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="team_leader_id must be positive"
            )

    def _validate_watchers(self, watchers: list[int]) -> None:
        if any(watcher_id <= 0 for watcher_id in watchers):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="watchers must contain positive user ids",
            )
