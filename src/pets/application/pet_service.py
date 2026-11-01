from domain.exceptions import NotFoundError, ValidationError
from domain.owner.repository import OwnerRepository
from domain.pet.nickname import Nickname
from domain.pet.pet import Pet
from domain.pet.repository import PetRepository
from domain.pet.weight import Weight


# Сценарии работы с животными.
class PetService:
    def __init__(
            self,
            pet_repository: PetRepository,
            owner_repository: OwnerRepository
    ) -> None:
        self.__pet_repository = pet_repository
        self.__owner_repository = owner_repository

    # Новый id на единицу больше самого большого из сохраненных.
    def next_id(self) -> int:
        ids = [pet.id for pet in self.get_all_pets()]
        return max(ids, default=0) + 1

    def add_pet(self, pet: Pet) -> None:
        if self.__owner_repository.get_by_id(pet.owner_id) is None:
            raise NotFoundError(f"Владелец {pet.owner_id} не найден")

        self.__check_nickname_free(pet.owner_id, pet.nickname)
        self.__pet_repository.add(pet)

    def get_pet(self, pet_id: int) -> Pet:
        pet = self.__pet_repository.get_by_id(pet_id)

        if pet is None:
            raise NotFoundError(f"Животное {pet_id} не найдено")

        return pet

    def get_all_pets(self) -> list[Pet]:
        return self.__pet_repository.get_all()

    def find_pets_by_nickname(self, text: str) -> list[Pet]:
        needle = text.strip().casefold()

        return [
            pet
            for pet in self.get_all_pets()
            if needle in pet.nickname.value.casefold()
        ]

    def change_pet(
            self, pet_id: int, nickname: Nickname, weight: Weight
    ) -> None:
        pet = self.get_pet(pet_id)

        if nickname.value.casefold() != pet.nickname.value.casefold():
            self.__check_nickname_free(pet.owner_id, nickname)

        pet.change(nickname, weight)
        self.__pet_repository.update(pet)

    def delete_pet(self, pet_id: int) -> None:
        self.get_pet(pet_id)
        self.__pet_repository.delete(pet_id)

    # У одного владельца не может быть двух животных с одинаковой кличкой.
    def __check_nickname_free(
            self, owner_id: int, nickname: Nickname
    ) -> None:
        if any(
            pet.owner_id == owner_id
            and pet.nickname.value.casefold() == nickname.value.casefold()
            for pet in self.get_all_pets()
        ):
            raise ValidationError(
                f"У владельца уже есть животное по кличке «{nickname.value}»"
            )
