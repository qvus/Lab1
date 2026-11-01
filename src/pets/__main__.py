from application.owner_service import OwnerService
from application.pet_service import PetService
from domain.exceptions import PetsError
from domain.owner.repository import OwnerRepository
from domain.pet.repository import PetRepository
from infrastructure.db.json.owner_repository import JsonOwnerRepository
from infrastructure.db.json.pet_repository import JsonPetRepository
from infrastructure.db.xml.owner_repository import XmlOwnerRepository
from infrastructure.db.xml.pet_repository import XmlPetRepository
from presentation.console import Console, read_line

# Пункт выбора при запуске и соответствующий формат файлов.
STORAGE_FORMATS = {"1": "xml", "2": "json"}


def choose_storage_format() -> str:
    while True:
        choice = read_line(
            "Формат хранения данных (1 - XML, 2 - JSON): "
        ).strip()

        if choice in STORAGE_FORMATS:
            return STORAGE_FORMATS[choice]

        print("Введите 1 или 2")


def build_repositories(
        storage_format: str,
) -> tuple[OwnerRepository, PetRepository]:
    if storage_format == "json":
        return (
            JsonOwnerRepository("data/owners.json"),
            JsonPetRepository("data/pets.json"),
        )

    return (
        XmlOwnerRepository("data/owners.xml"),
        XmlPetRepository("data/pets.xml"),
    )


# Собираем зависимости: репозитории передаются в сервисы,
# сервисы - в консоль.
def build_console(storage_format: str) -> Console:
    owner_repository, pet_repository = build_repositories(storage_format)

    owner_service = OwnerService(
        owner_repository=owner_repository,
        pet_repository=pet_repository,
    )
    pet_service = PetService(
        pet_repository=pet_repository,
        owner_repository=owner_repository,
    )

    return Console(
        owner_service=owner_service,
        pet_service=pet_service,
    )


def main() -> None:
    try:
        storage_format = choose_storage_format()
    except (KeyboardInterrupt, EOFError):
        print()
        return

    try:
        console = build_console(storage_format)
    except PetsError as error:
        print(f"Не удалось подготовить хранилище: {error}")
        return

    console.run()


if __name__ == "__main__":
    main()
