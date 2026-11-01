from typing import Protocol
from uuid import UUID

from domain.pet.pet import Pet


# Интерфейс хранилища животных. Его реализуют репозитории JSON и XML.
class PetRepository(Protocol):
    def add(self, pet: Pet) -> None:
        raise NotImplementedError

    def get_by_id(self, pet_id: UUID) -> Pet | None:
        raise NotImplementedError

    def get_all(self) -> list[Pet]:
        raise NotImplementedError

    def update(self, pet: Pet) -> None:
        raise NotImplementedError

    def delete(self, pet_id: UUID) -> None:
        raise NotImplementedError
