from uuid import UUID

from domain.pet.nickname import Nickname
from domain.pet.pet import Pet
from domain.pet.weight import Weight


# Кошка. Особенность: живет дома или гуляет во дворе.
class Cat(Pet):
    kind = "cat"

    def __init__(
            self,
            pet_id: UUID,
            owner_id: UUID,
            nickname: Nickname,
            weight: Weight,
            lives_indoor: bool
    ) -> None:
        super().__init__(pet_id, owner_id, nickname, weight)
        self.__lives_indoor = lives_indoor

    @property
    def lives_indoor(self) -> bool:
        return self.__lives_indoor

    @property
    def specification(self) -> str:
        return "живет дома" if self.__lives_indoor else "гуляет во дворе"
