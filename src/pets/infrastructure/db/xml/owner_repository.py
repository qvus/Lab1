import xml.etree.ElementTree as ET
from pathlib import Path

from domain.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    StorageError,
    ValidationError,
)
from domain.owner.owner import Owner
from domain.owner.owner_name import OwnerName
from infrastructure.db.xml.storage import (
    read_records,
    read_text,
    write_records,
)

ROOT = "owners"


# Хранит владельцев в XML-файле: корень <owners>, внутри элементы <owner>.
class XmlOwnerRepository:
    def __init__(self, file_path: str | Path) -> None:
        self.__file_path = Path(file_path)

    def add(self, owner: Owner) -> None:
        records = read_records(self.__file_path, ROOT)

        if self.__find_index(records, owner.id) is not None:
            raise AlreadyExistsError(f"Владелец {owner.id} уже существует")

        records.append(self.__to_element(owner))
        write_records(self.__file_path, ROOT, records)

    def get_by_id(self, owner_id: int) -> Owner | None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, owner_id)

        if index is None:
            return None

        return self.__to_owner(records[index])

    def get_all(self) -> list[Owner]:
        return [
            self.__to_owner(element)
            for element in read_records(self.__file_path, ROOT)
        ]

    def update(self, owner: Owner) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, owner.id)

        if index is None:
            raise NotFoundError(f"Владелец {owner.id} не найден")

        records[index] = self.__to_element(owner)
        write_records(self.__file_path, ROOT, records)

    def delete(self, owner_id: int) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, owner_id)

        if index is None:
            raise NotFoundError(f"Владелец {owner_id} не найден")

        del records[index]
        write_records(self.__file_path, ROOT, records)

    @staticmethod
    def __find_index(
            records: list[ET.Element], owner_id: int
    ) -> int | None:
        for index, element in enumerate(records):
            if element.findtext("id") == str(owner_id):
                return index

        return None

    @staticmethod
    def __to_element(owner: Owner) -> ET.Element:
        element = ET.Element("owner")

        ET.SubElement(element, "id").text = str(owner.id)
        ET.SubElement(element, "name").text = owner.name.value

        return element

    def __to_owner(self, element: ET.Element) -> Owner:
        try:
            return Owner(
                owner_id=int(read_text(element, "id")),
                name=OwnerName(read_text(element, "name")),
            )
        except (ValueError, ValidationError) as error:
            raise StorageError(
                f"В файле {self.__file_path} повреждена запись владельца"
            ) from error
