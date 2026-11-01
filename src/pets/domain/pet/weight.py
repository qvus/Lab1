from domain.exceptions import ValidationError

MIN_WEIGHT_KG = 0.1
MAX_WEIGHT_KG = 100.0


# Объект-значение: вес животного в килограммах.
class Weight:
    def __init__(self, kilograms: float) -> None:
        if not MIN_WEIGHT_KG <= kilograms <= MAX_WEIGHT_KG:
            raise ValidationError(
                f"Вес от {MIN_WEIGHT_KG} до {MAX_WEIGHT_KG:g} кг"
            )

        self.__kilograms = kilograms

    @property
    def kilograms(self) -> float:
        return self.__kilograms
