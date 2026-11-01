from abc import ABC, abstractmethod
from typing import ClassVar
from uuid import UUID

from domain.pet.nickname import Nickname
from domain.pet.weight import Weight


# Базовый класс домашнего животного. Владелец задается при создании,
# кличку и вес меняет метод change, id остается прежним.
class Pet(ABC):
    # Значение поля kind в файлах хранилища.
    kind: ClassVar[str]

    def __init__(
            self,
            pet_id: UUID,
            owner_id: UUID,
            nickname: Nickname,
            weight: Weight
    ) -> None:
        self.__id = pet_id
        self.__owner_id = owner_id
        self.__nickname = nickname
        self.__weight = weight

    def change(self, nickname: Nickname, weight: Weight) -> None:
        self.__nickname = nickname
        self.__weight = weight

    @property
    def id(self) -> UUID:
        return self.__id

    @property
    def owner_id(self) -> UUID:
        return self.__owner_id

    @property
    def nickname(self) -> Nickname:
        return self.__nickname

    @property
    def weight(self) -> Weight:
        return self.__weight

    # Особая характеристика вида животного для вывода на экран.
    @property
    @abstractmethod
    def specification(self) -> str:
        raise NotImplementedError
