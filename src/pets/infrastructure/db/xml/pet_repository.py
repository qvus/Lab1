import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import UUID

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
from infrastructure.db.xml.storage import (
    read_records,
    read_text,
    write_records,
)

ROOT = "pets"


# Хранит животных в XML-файле: корень <pets>, внутри элементы <pet>.
# Поле kind показывает, это кошка или собака.
class XmlPetRepository:
    def __init__(self, file_path: str | Path) -> None:
        self.__file_path = Path(file_path)

    def add(self, pet: Pet) -> None:
        records = read_records(self.__file_path, ROOT)

        if self.__find_index(records, pet.id) is not None:
            raise AlreadyExistsError(f"Животное {pet.id} уже существует")

        records.append(self.__to_element(pet))
        write_records(self.__file_path, ROOT, records)

    def get_by_id(self, pet_id: UUID) -> Pet | None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, pet_id)

        if index is None:
            return None

        return self.__to_pet(records[index])

    def get_all(self) -> list[Pet]:
        return [
            self.__to_pet(element)
            for element in read_records(self.__file_path, ROOT)
        ]

    def update(self, pet: Pet) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, pet.id)

        if index is None:
            raise NotFoundError(f"Животное {pet.id} не найдено")

        records[index] = self.__to_element(pet)
        write_records(self.__file_path, ROOT, records)

    def delete(self, pet_id: UUID) -> None:
        records = read_records(self.__file_path, ROOT)
        index = self.__find_index(records, pet_id)

        if index is None:
            raise NotFoundError(f"Животное {pet_id} не найдено")

        del records[index]
        write_records(self.__file_path, ROOT, records)

    @staticmethod
    def __find_index(
            records: list[ET.Element], pet_id: UUID
    ) -> int | None:
        for index, element in enumerate(records):
            if element.findtext("id") == str(pet_id):
                return index

        return None

    @staticmethod
    def __to_element(pet: Pet) -> ET.Element:
        element = ET.Element("pet")

        ET.SubElement(element, "id").text = str(pet.id)
        ET.SubElement(element, "kind").text = pet.kind
        ET.SubElement(element, "owner_id").text = str(pet.owner_id)
        ET.SubElement(element, "nickname").text = pet.nickname.value
        ET.SubElement(element, "weight").text = str(pet.weight.kilograms)

        if isinstance(pet, Cat):
            ET.SubElement(element, "lives_indoor").text = str(
                pet.lives_indoor
            ).lower()
        elif isinstance(pet, Dog):
            ET.SubElement(element, "walks_per_day").text = str(
                pet.walks_per_day
            )

        return element

    # Любая ошибка разбора превращается в StorageError.
    def __to_pet(self, element: ET.Element) -> Pet:
        try:
            kind = read_text(element, "kind")
            pet_id = UUID(read_text(element, "id"))
            owner_id = UUID(read_text(element, "owner_id"))
            nickname = Nickname(read_text(element, "nickname"))
            weight = Weight(float(read_text(element, "weight")))

            if kind == Cat.kind:
                return Cat(
                    pet_id=pet_id,
                    owner_id=owner_id,
                    nickname=nickname,
                    weight=weight,
                    lives_indoor=read_text(element, "lives_indoor") == "true",
                )

            if kind == Dog.kind:
                return Dog(
                    pet_id=pet_id,
                    owner_id=owner_id,
                    nickname=nickname,
                    weight=weight,
                    walks_per_day=int(read_text(element, "walks_per_day")),
                )
        except (ValueError, ValidationError) as error:
            raise StorageError(
                f"В файле {self.__file_path} повреждена запись животного"
            ) from error

        raise StorageError(
            f"В файле {self.__file_path} неизвестный вид животного"
        )
