from typing import Protocol

from domain.pet.pet import Pet


# Интерфейс хранилища животных. Его реализуют репозитории JSON и XML.
class PetRepository(Protocol):
    def add(self, pet: Pet) -> None:
        raise NotImplementedError

    def get_by_id(self, pet_id: int) -> Pet | None:
        raise NotImplementedError

    def get_all(self) -> list[Pet]:
        raise NotImplementedError

    def update(self, pet: Pet) -> None:
        raise NotImplementedError

    def delete(self, pet_id: int) -> None:
        raise NotImplementedError
