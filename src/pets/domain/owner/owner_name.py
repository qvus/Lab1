from domain.exceptions import ValidationError

MAX_NAME_LENGTH = 100


# Объект-значение: имя владельца от 1 до 100 символов без цифр.
class OwnerName:
    def __init__(self, value: str) -> None:
        normalized = " ".join(value.split())

        if not 1 <= len(normalized) <= MAX_NAME_LENGTH:
            raise ValidationError(
                f"Имя владельца от 1 до {MAX_NAME_LENGTH} символов"
            )

        if any(char.isdigit() for char in normalized):
            raise ValidationError("Имя владельца не может содержать цифры")

        self.__value = normalized

    @property
    def value(self) -> str:
        return self.__value
