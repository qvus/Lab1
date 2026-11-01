from domain.exceptions import ValidationError
from domain.pet.nickname import Nickname
from domain.pet.pet import Pet
from domain.pet.weight import Weight

MIN_WALKS_PER_DAY = 1
MAX_WALKS_PER_DAY = 6


# Собака. Особенность: сколько раз в день ее выгуливают.
class Dog(Pet):
    kind = "dog"

    def __init__(
            self,
            pet_id: int,
            owner_id: int,
            nickname: Nickname,
            weight: Weight,
            walks_per_day: int
    ) -> None:
        super().__init__(pet_id, owner_id, nickname, weight)

        if not MIN_WALKS_PER_DAY <= walks_per_day <= MAX_WALKS_PER_DAY:
            raise ValidationError(
                f"Прогулок в день от {MIN_WALKS_PER_DAY} "
                f"до {MAX_WALKS_PER_DAY}"
            )

        self.__walks_per_day = walks_per_day

    @property
    def walks_per_day(self) -> int:
        return self.__walks_per_day

    @property
    def specification(self) -> str:
        return f"прогулок в день: {self.__walks_per_day}"
