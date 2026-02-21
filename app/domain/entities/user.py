from pydantic import EmailStr
from sqlalchemy import Column, String, Enum
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
