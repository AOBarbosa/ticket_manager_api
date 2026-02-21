from pydantic import EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field

from app.domain.entities.person import Person


class User(Person, table=True):
    __tablename__ = "users"
    email: EmailStr = Field(sa_column=Column(String(140), nullable=False, unique=True))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
