from pathlib import Path
from typing import Any

from domain.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    StorageError,
    ValidationError,
)
from domain.pet.cat import Cat
from domain.pet.dog import Dog
from domain.pet.nickname import Nickname
from domain.pet.pet import Pet
from domain.pet.weight import Weight
from infrastructure.db.json.storage import read_records, write_records

ROOT = "pets"


# Хранит животных в JSON-файле вида {"pets": [...]}.
# Поле kind показывает, это кошка или собака.
class JsonPetRepository:
    def __init__(self, file_path: str | Path) -> None:
        self.__file_path = Path(file_path)

    def add(self, pet: Pet) -> None:
        records = read_records(self.__file_path, ROOT)

        if self.__find_index(records, pet.id) is not None:
            raise AlreadyExistsError(f"Животное {pet.id} уже существует")

        records.append(self.__to_dict(pet))
        write_records(self.__file_path, ROOT, records)

    def get_by_id(self, pet_id: int) -> Pet | None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, pet_id)

        if index is None:
            return None

        return self.__to_pet(records[index])

    def get_all(self) -> list[Pet]:
        return [
            self.__to_pet(record)
            for record in read_records(self.__file_path, ROOT)
        ]

    def update(self, pet: Pet) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, pet.id)

        if index is None:
            raise NotFoundError(f"Животное {pet.id} не найдено")

        records[index] = self.__to_dict(pet)
        write_records(self.__file_path, ROOT, records)

    def delete(self, pet_id: int) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, pet_id)

        if index is None:
            raise NotFoundError(f"Животное {pet_id} не найдено")

        del records[index]
        write_records(self.__file_path, ROOT, records)

    @staticmethod
    def __find_index(
            records: list[dict[str, Any]], pet_id: int
    ) -> int | None:
        for index, record in enumerate(records):
            if record.get("id") == pet_id:
                return index

        return None

    @staticmethod
    def __to_dict(pet: Pet) -> dict[str, Any]:
        record: dict[str, Any] = {
            "id": pet.id,
            "kind": pet.kind,
            "owner_id": pet.owner_id,
            "nickname": pet.nickname.value,
            "weight": pet.weight.kilograms,
        }

        if isinstance(pet, Cat):
            record["lives_indoor"] = pet.lives_indoor
        elif isinstance(pet, Dog):
            record["walks_per_day"] = pet.walks_per_day

        return record

    # Любая ошибка разбора превращается в StorageError.
    def __to_pet(self, record: dict[str, Any]) -> Pet:
        try:
            if record["kind"] == Cat.kind:
                return Cat(
                    pet_id=int(record["id"]),
                    owner_id=int(record["owner_id"]),
                    nickname=Nickname(record["nickname"]),
                    weight=Weight(record["weight"]),
                    lives_indoor=record["lives_indoor"],
                )

            if record["kind"] == Dog.kind:
                return Dog(
                    pet_id=int(record["id"]),
                    owner_id=int(record["owner_id"]),
                    nickname=Nickname(record["nickname"]),
                    weight=Weight(record["weight"]),
                    walks_per_day=record["walks_per_day"],
                )
        except (KeyError, TypeError, ValueError, ValidationError) as error:
            raise StorageError(
                f"В файле {self.__file_path} повреждена запись животного"
            ) from error

        raise StorageError(
            f"В файле {self.__file_path} неизвестный вид животного"
        )
