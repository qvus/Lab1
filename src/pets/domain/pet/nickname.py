from domain.exceptions import ValidationError

MAX_NICKNAME_LENGTH = 30


# Объект-значение: кличка животного от 1 до 30 символов.
class Nickname:
    def __init__(self, value: str) -> None:
        normalized = " ".join(value.split())

        if not 1 <= len(normalized) <= MAX_NICKNAME_LENGTH:
            raise ValidationError(
                f"Кличка от 1 до {MAX_NICKNAME_LENGTH} символов"
            )

        self.__value = normalized

    @property
    def value(self) -> str:
        return self.__value
