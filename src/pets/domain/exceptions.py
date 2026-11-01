# Базовое исключение приложения: консоль перехватывает его
# и показывает пользователю сообщение вместо трассировки.
class PetsError(Exception):
    pass


# Данные нарушают правила предметной области.
class ValidationError(PetsError):
    pass


# Записи с указанным id нет в хранилище.
class NotFoundError(PetsError):
    pass


# Такая запись уже есть в хранилище.
class AlreadyExistsError(PetsError):
    pass


# Файл хранилища не удалось прочитать, записать или разобрать.
class StorageError(PetsError):
    pass
