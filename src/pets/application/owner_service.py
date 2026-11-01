from uuid import UUID

from domain.exceptions import NotFoundError, ValidationError
from domain.owner.owner import Owner
from domain.owner.owner_name import OwnerName
from domain.owner.repository import OwnerRepository
from domain.pet.repository import PetRepository


# Сценарии работы с владельцами.
class OwnerService:
    def __init__(
            self,
            owner_repository: OwnerRepository,
            pet_repository: PetRepository
    ) -> None:
        self.__owner_repository = owner_repository
        self.__pet_repository = pet_repository

    def add_owner(self, owner: Owner) -> None:
        self.__owner_repository.add(owner)

    def get_owner(self, owner_id: UUID) -> Owner:
        owner = self.__owner_repository.get_by_id(owner_id)

        if owner is None:
            raise NotFoundError(f"Владелец {owner_id} не найден")

        return owner

    def get_all_owners(self) -> list[Owner]:
        return self.__owner_repository.get_all()

    def rename_owner(self, owner_id: UUID, name: OwnerName) -> None:
        owner = self.get_owner(owner_id)
        owner.rename(name)
        self.__owner_repository.update(owner)

    # Владельца с животными удалять нельзя: у животных останется
    # ссылка на несуществующего владельца.
    def delete_owner(self, owner_id: UUID) -> None:
        self.get_owner(owner_id)

        pets = self.__pet_repository.get_all()

        if any(pet.owner_id == owner_id for pet in pets):
            raise ValidationError(
                "Нельзя удалить владельца: у него есть животные"
            )

        self.__owner_repository.delete(owner_id)
