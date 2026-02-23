from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.services.ticket_service import TicketService
from app.domain.dtos.ticket_dto import (
    CreateTicketRequestDTO,
    TicketResponseDTO,
    UpdateTicketRequestDTO,
)
from app.domain.dtos.user_dto import UserResponseDTO
from app.presentation.api.deps.auth_deps import get_current_user
from app.presentation.api.deps.ticket_deps import get_ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponseDTO, status_code=status.HTTP_201_CREATED)
def create_ticket(
    body: CreateTicketRequestDTO,
    service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: Annotated[UserResponseDTO, Depends(get_current_user)],
):
    return service.create(body, actor=current_user)


@router.get("", response_model=list[TicketResponseDTO], status_code=status.HTTP_200_OK)
def list_tickets(
    service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: Annotated[UserResponseDTO, Depends(get_current_user)],
):
    return service.get_all(actor=current_user)


@router.get("/{ticket_id}", response_model=TicketResponseDTO)
def get_ticket_by_id(
    ticket_id: int,
    service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: Annotated[UserResponseDTO, Depends(get_current_user)],
):
    return service.get_by_id(ticket_id, actor=current_user)


@router.put("/{ticket_id}", response_model=TicketResponseDTO)
def update_ticket(
    ticket_id: int,
    body: UpdateTicketRequestDTO,
    service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: Annotated[UserResponseDTO, Depends(get_current_user)],
):
    return service.update(ticket_id, body, actor=current_user)


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: int,
    service: Annotated[TicketService, Depends(get_ticket_service)],
    current_user: Annotated[UserResponseDTO, Depends(get_current_user)],
):
    service.delete(ticket_id, actor=current_user)
