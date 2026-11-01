from pathlib import Path
from typing import Any
from uuid import UUID

from domain.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    StorageError,
    ValidationError,
)
from domain.owner.owner import Owner
from domain.owner.owner_name import OwnerName
from infrastructure.db.json.storage import read_records, write_records

ROOT = "owners"


# Хранит владельцев в JSON-файле вида {"owners": [...]}.
# Каждая операция заново читает файл и сразу записывает изменения.
class JsonOwnerRepository:
    def __init__(self, file_path: str | Path) -> None:
        self.__file_path = Path(file_path)

    def add(self, owner: Owner) -> None:
        records = read_records(self.__file_path, ROOT)

        if self.__find_index(records, owner.id) is not None:
            raise AlreadyExistsError(f"Владелец {owner.id} уже существует")

        records.append(self.__to_dict(owner))
        write_records(self.__file_path, ROOT, records)

    def get_by_id(self, owner_id: UUID) -> Owner | None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, owner_id)

        if index is None:
            return None

        return self.__to_owner(records[index])

    def get_all(self) -> list[Owner]:
        return [
            self.__to_owner(record)
            for record in read_records(self.__file_path, ROOT)
        ]

    def update(self, owner: Owner) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, owner.id)

        if index is None:
            raise NotFoundError(f"Владелец {owner.id} не найден")

        records[index] = self.__to_dict(owner)
        write_records(self.__file_path, ROOT, records)

    def delete(self, owner_id: UUID) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, owner_id)

        if index is None:
            raise NotFoundError(f"Владелец {owner_id} не найден")

        del records[index]
        write_records(self.__file_path, ROOT, records)

    @staticmethod
    def __find_index(
            records: list[dict[str, Any]], owner_id: UUID
    ) -> int | None:
        for index, record in enumerate(records):
            if record.get("id") == str(owner_id):
                return index

        return None

    @staticmethod
    def __to_dict(owner: Owner) -> dict[str, Any]:
        return {"id": str(owner.id), "name": owner.name.value}

    # Любая ошибка разбора превращается в StorageError
    # с понятным сообщением вместо KeyError или ValueError.
    def __to_owner(self, record: dict[str, Any]) -> Owner:
        try:
            return Owner(
                owner_id=UUID(record["id"]),
                name=OwnerName(record["name"]),
            )
        except (KeyError, TypeError, ValueError, ValidationError) as error:
            raise StorageError(
                f"В файле {self.__file_path} повреждена запись владельца"
            ) from error
