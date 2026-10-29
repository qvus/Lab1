"""Собственные исключения предметной области «Домашние животные»."""


class PetsError(Exception):
    """Базовое исключение предметной области."""


class ValidationError(PetsError):
    """Некорректное значение поля."""


class InvalidNameError(ValidationError):
    """Пустое или неверное имя."""


class InvalidAgeError(ValidationError):
    """Возраст вне допустимого диапазона."""


class InvalidWeightError(ValidationError):
    """Вес вне допустимого диапазона."""


class InvalidPhoneError(ValidationError):
    """Неверный формат телефона."""


class InvalidVaccinationError(ValidationError):
    """Некорректная запись о прививке."""


class PetNotFoundError(PetsError):
    """Животное не найдено."""


class OwnerNotFoundError(PetsError):
    """Владелец не найден."""


class DuplicateOwnerError(PetsError):
    """Владелец с таким именем уже существует."""


class StorageError(PetsError):
    """Ошибка чтения или записи файла (XML/JSON)."""
