from typing import Protocol

from domain.owner.owner import Owner


# Интерфейс хранилища владельцев. Его реализуют репозитории JSON и XML,
# поэтому сервисы не зависят от формата файла.
class OwnerRepository(Protocol):
    def add(self, owner: Owner) -> None:
        raise NotImplementedError

    def get_by_id(self, owner_id: int) -> Owner | None:
        raise NotImplementedError

    def get_all(self) -> list[Owner]:
        raise NotImplementedError

    def update(self, owner: Owner) -> None:
        raise NotImplementedError

    def delete(self, owner_id: int) -> None:
        raise NotImplementedError
