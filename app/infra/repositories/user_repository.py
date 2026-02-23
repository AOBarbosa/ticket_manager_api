from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User
from app.infra.repositories.abstract_repository import AbstractRepository


class UserRepository(AbstractRepository[User], ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_cpf(self, cpf: str) -> Optional[User]:
        pass
