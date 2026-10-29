"""Классы предметной области «Домашние животные»."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Type

from exceptions import (
    DuplicateOwnerError,
    InvalidAgeError,
    InvalidNameError,
    InvalidPhoneError,
    InvalidVaccinationError,
    InvalidWeightError,
    OwnerNotFoundError,
    PetNotFoundError,
    ValidationError,
)

PHONE_RE = re.compile(r"^\+?\d{10,15}$")


def to_bool(value: Any) -> bool:
    """Преобразует bool или строку ('true'/'false') в bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in ("true", "1", "yes"):
            return True
        if text in ("false", "0", "no"):
            return False
    raise ValidationError(f"Не удалось преобразовать в bool: {value!r}")


class Vaccination:
    """Запись о прививке."""

    def __init__(self, name: str, when: date) -> None:
        if not name.strip():
            raise InvalidVaccinationError("Название прививки пусто")
        if when > date.today():
            raise InvalidVaccinationError("Дата прививки в будущем")
        self.name = name.strip()
        self.when = when

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "date": self.when.isoformat()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vaccination":
        return cls(str(data["name"]), date.fromisoformat(str(data["date"])))


class Pet(ABC):
    """Базовый класс домашнего животного."""

    def __init__(self, name: str, age: int, weight: float) -> None:
        self._name = ""
        self._age = 0
        self._weight = 0.0
        self.name = name
        self.age = age
        self.weight = weight
        self._vaccinations: List[Vaccination] = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise InvalidNameError("Имя животного не может быть пустым")
        self._name = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidAgeError("Возраст должен быть целым числом")
        if not 0 <= value <= 40:
            raise InvalidAgeError("Возраст должен быть от 0 до 40 лет")
        self._age = value

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidWeightError("Вес должен быть числом")
        if not 0 < value <= 200:
            raise InvalidWeightError("Вес должен быть от 0 до 200 кг")
        self._weight = float(value)

    @property
    def vaccinations(self) -> List[Vaccination]:
        return list(self._vaccinations)

    def add_vaccination(self, vaccination: Vaccination) -> None:
        self._vaccinations.append(vaccination)

    def feed(self, grams: int) -> str:
        """Кормит животное."""
        if grams <= 0:
            raise ValidationError("Порция корма должна быть больше нуля")
        return f"{self.name} съел(а) {grams} г корма"

    @abstractmethod
    def sound(self) -> str:
        """Звук, который издаёт животное."""

    @abstractmethod
    def _extra(self) -> Dict[str, Any]:
        """Дополнительные поля конкретного вида."""

    @classmethod
    @abstractmethod
    def _create(cls, data: Dict[str, Any]) -> "Pet":
        """Создаёт животное конкретного вида из словаря."""

    def describe(self) -> str:
        return (f"{type(self).__name__} {self.name}, "
                f"возраст {self.age}, вес {self.weight} кг")

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "type": type(self).__name__,
            "name": self.name,
            "age": self.age,
            "weight": self.weight,
        }
        data.update(self._extra())
        data["vaccinations"] = [v.to_dict() for v in self._vaccinations]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        pet = cls._create(data)
        for item in data.get("vaccinations", []):
            pet.add_vaccination(Vaccination.from_dict(item))
        return pet


class Dog(Pet):
    def __init__(self, name: str, age: int, weight: float,
                 breed: str, trained: bool = False) -> None:
        super().__init__(name, age, weight)
        self.breed = breed
        self.trained = trained

    def sound(self) -> str:
        return "Гав!"

    def _extra(self) -> Dict[str, Any]:
        return {"breed": self.breed, "trained": self.trained}

    @classmethod
    def _create(cls, data: Dict[str, Any]) -> "Pet":
        return cls(str(data["name"]), int(data["age"]),
                   float(data["weight"]), str(data["breed"]),
                   to_bool(data["trained"]))


class Cat(Pet):
    def __init__(self, name: str, age: int, weight: float,
                 indoor: bool = True) -> None:
        super().__init__(name, age, weight)
        self.indoor = indoor

    def sound(self) -> str:
        return "Мяу!"

    def _extra(self) -> Dict[str, Any]:
        return {"indoor": self.indoor}

    @classmethod
    def _create(cls, data: Dict[str, Any]) -> "Pet":
        return cls(str(data["name"]), int(data["age"]),
                   float(data["weight"]), to_bool(data["indoor"]))


class Bird(Pet):
    def __init__(self, name: str, age: int, weight: float,
                 can_talk: bool = False) -> None:
        super().__init__(name, age, weight)
        self.can_talk = can_talk

    def sound(self) -> str:
        return "Чирик!"

    def _extra(self) -> Dict[str, Any]:
        return {"can_talk": self.can_talk}

    @classmethod
    def _create(cls, data: Dict[str, Any]) -> "Pet":
        return cls(str(data["name"]), int(data["age"]),
                   float(data["weight"]), to_bool(data["can_talk"]))


PET_TYPES: Dict[str, Type[Pet]] = {
    "Dog": Dog,
    "Cat": Cat,
    "Bird": Bird,
}


def pet_from_dict(data: Dict[str, Any]) -> Pet:
    """Создаёт животное нужного класса по полю 'type'."""
    kind = str(data["type"])
    if kind not in PET_TYPES:
        raise ValidationError(f"Неизвестный вид животного: {kind}")
    return PET_TYPES[kind].from_dict(data)


class Owner:
    """Владелец животных."""

    def __init__(self, name: str, phone: str) -> None:
        if not name.strip():
            raise InvalidNameError("Имя владельца не может быть пустым")
        if not PHONE_RE.match(phone):
            raise InvalidPhoneError(f"Неверный телефон: {phone}")
        self.name = name.strip()
        self.phone = phone
        self._pets: List[Pet] = []

    @property
    def pets(self) -> List[Pet]:
        return list(self._pets)

    def add_pet(self, pet: Pet) -> None:
        if any(p.name == pet.name for p in self._pets):
            raise ValidationError(f"Животное {pet.name} уже есть")
        self._pets.append(pet)

    def find_pet(self, name: str) -> Pet:
        for pet in self._pets:
            if pet.name == name:
                return pet
        raise PetNotFoundError(f"Животное не найдено: {name}")

    def remove_pet(self, name: str) -> None:
        self._pets.remove(self.find_pet(name))

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "phone": self.phone,
                "pets": [p.to_dict() for p in self._pets]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Owner":
        owner = cls(str(data["name"]), str(data["phone"]))
        for item in data.get("pets", []):
            owner.add_pet(pet_from_dict(item))
        return owner


class PetRegistry:
    """Реестр владельцев и их животных."""

    def __init__(self) -> None:
        self._owners: Dict[str, Owner] = {}

    @property
    def owners(self) -> List[Owner]:
        return list(self._owners.values())

    def add_owner(self, owner: Owner) -> None:
        if owner.name in self._owners:
            raise DuplicateOwnerError(f"Владелец уже есть: {owner.name}")
        self._owners[owner.name] = owner

    def get_owner(self, name: str) -> Owner:
        if name not in self._owners:
            raise OwnerNotFoundError(f"Владелец не найден: {name}")
        return self._owners[name]

    def remove_owner(self, name: str) -> None:
        self.get_owner(name)
        del self._owners[name]

    def all_pets(self) -> List[Pet]:
        return [p for o in self._owners.values() for p in o.pets]

    def to_dict(self) -> Dict[str, Any]:
        return {"owners": [o.to_dict() for o in self.owners]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PetRegistry":
        registry = cls()
        for item in data.get("owners", []):
            registry.add_owner(Owner.from_dict(item))
        return registry
