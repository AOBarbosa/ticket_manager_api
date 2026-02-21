from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.domain.enums.roles_enum import UserRole


class CreateUserRequestDTO(BaseModel):
    """
    Data Transfer Object for creating a User.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "2000-01-15",
                "cpf": "12345678901",
                "email": "john.doe@email.com",
                "password": "StrongPass#123",
                "role": "CUSTOMER",
            }
        }
    )

    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's first name.",
        examples=["John"],
    )
    last_name: str = Field(
        min_length=1,
        max_length=140,
        description="User's last name.",
        examples=["Doe"],
    )
    date_of_birth: date = Field(
        description="User's date of birth (ISO format).",
        examples=["2000-01-15"],
    )
    cpf: str = Field(
        min_length=11,
        max_length=14,
        description="Brazilian CPF identifier (may include punctuation depending on formatting).",
        examples=["12345678901", "123.456.789-01"],
    )
    email: EmailStr = Field(
        description="User's email address.",
        examples=["andre.barbosa@email.com"],
    )
    role: UserRole = Field(default="CUSTOMER", description="User's role.")


class UserResponseDTO(BaseModel):
    """
    Data Transfer Object for returning a User.
    """

    id: int = Field(
        description="The unique identifier of the user.",
        examples=[1],
    )
    first_name: str = Field(
        description="User's first name.",
        examples=["John"],
    )
    last_name: str = Field(
        description="User's last name.",
        examples=["Doe"],
    )
    date_of_birth: date = Field(
        description="User's date of birth (ISO format).",
        examples=["2000-01-15"],
    )
    cpf: str = Field(
        description="Brazilian CPF identifier.",
        examples=["12345678901"],
    )
    email: EmailStr = Field(
        description="User's email address.",
        examples=["john.doe@email.com"],
    )
    role: UserRole = Field(description="User's role.", examples=["CUSTOMER"])
    is_active: bool = Field(description="User's active status.")
    created_at: datetime = Field(
        description="Timestamp when the user was created (server-generated).",
        examples=["2026-02-13T12:34:56Z"],
    )
    updated_at: datetime = Field(
        description="Timestamp when the user was last updated (server-managed).",
        examples=["2026-02-13T12:34:56Z"],
    )
