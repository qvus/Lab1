from domain.owner.owner_name import OwnerName


# Владелец домашних животных. Имя меняется методом rename,
# id остается прежним.
class Owner:
    def __init__(self, owner_id: int, name: OwnerName) -> None:
        self.__id = owner_id
        self.__name = name

    def rename(self, name: OwnerName) -> None:
        self.__name = name

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> OwnerName:
        return self.__name
