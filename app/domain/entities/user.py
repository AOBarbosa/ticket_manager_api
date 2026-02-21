from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column, String, Enum, DateTime
from sqlmodel import Field

from app.domain.entities.person import Person
from app.domain.enums.roles_enum import UserRole


class User(Person, table=True):
    __tablename__ = "users"
    email: EmailStr = Field(sa_column=Column(String(140), nullable=False, unique=True))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    role: UserRole = Field(
        sa_column=Column(
            Enum(UserRole, name="user_role"),
            nullable=False,
            server_default="CUSTOMER",
        )
    )
    first_access: bool = Field(default=True, nullable=False)
    password_changed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
