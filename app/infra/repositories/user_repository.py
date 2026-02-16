from abc import ABC, abstractmethod

from app.domain.entities.user import User
from app.infra.repositories.abstract_repository import AbstractRepository


class UserRepository(AbstractRepository[User], ABC):

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    def find_by_cpf(self, cpf: str) -> User:
        pass

    # @abstractmethod
    # def find_me(self, user_id: int) -> User:
    #     pass