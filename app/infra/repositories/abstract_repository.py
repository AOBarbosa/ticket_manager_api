from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):

    @abstractmethod
    def create(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: int) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        raise NotImplementedError
