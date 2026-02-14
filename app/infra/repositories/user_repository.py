from abc import ABC

from app.domain.entities.user import User
from app.infra.repositories.abstract_repository import AbstractRepository


class UserRepository(AbstractRepository[User], ABC):
    """
    Contrato específico para User.
    Pode receber métodos adicionais no futuro.
    """
    pass
