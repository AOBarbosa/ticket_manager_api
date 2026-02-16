from typing import List, Optional
from sqlmodel import Session, select

from app.domain.entities.user import User
from app.infra.repositories.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def update(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()

    def get_all(self) -> List[User]:
        user = select(User)
        return list(self.session.exec(user).all())

    def find_by_email(self, email: str) -> Optional[User]:
        user = select(User).where(User.email == email).limit(1)
        return self.session.exec(user).first()

    def find_by_cpf(self, cpf_digits: str) -> Optional[User]:
        user = select(User).where(User.cpf == cpf_digits).limit(1)
        return self.session.exec(user).first()
