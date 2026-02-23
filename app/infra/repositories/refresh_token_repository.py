from abc import ABC, abstractmethod
from typing import Optional


class RefreshTokenRepository(ABC):
    @abstractmethod
    def upsert_for_user(self, user_id: int, token_hash: str) -> None:
        pass

    @abstractmethod
    def get_hash_for_user(self, user_id: int) -> Optional[str]:
        pass

    @abstractmethod
    def revoke_for_user(self, user_id: int) -> None:
        pass
