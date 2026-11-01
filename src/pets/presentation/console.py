# readline включает стрелки и историю ввода в input().
import readline  # noqa: F401
from collections.abc import Callable
from uuid import UUID, uuid4

from application.owner_service import OwnerService
from application.pet_service import PetService
from domain.exceptions import PetsError, ValidationError
from domain.owner.owner import Owner
from domain.owner.owner_name import OwnerName
from domain.pet.cat import Cat
from domain.pet.dog import Dog
from domain.pet.nickname import Nickname
from domain.pet.pet import Pet
from domain.pet.weight import Weight

MENU = """
Меню:
1 - показать владельцев
2 - добавить владельца
3 - переименовать владельца
4 - удалить владельца
5 - показать животных
6 - найти животное по кличке
7 - добавить животное
8 - изменить кличку и вес животного
9 - удалить животное
0 - выход
"""


# Терминал иногда передает обрывки байтов кириллицы.
# Возвращаем их в байты и отбрасываем то, что не декодируется.
def read_line(prompt: str) -> str:
    raw = input(prompt)
    return raw.encode("utf-8", "surrogateescape").decode("utf-8", "ignore")


# Ввод с проверкой: неверное значение превращается в ValidationError,
# который консоль покажет пользователю.
def ask_int(prompt: str) -> int:
    raw = read_line(prompt).strip()

    try:
        return int(raw)
    except ValueError as error:
        raise ValidationError("Введите целое число") from error


def ask_float(prompt: str) -> float:
    raw = read_line(prompt).strip().replace(",", ".")

    try:
        return float(raw)
    except ValueError as error:
        raise ValidationError("Введите число") from error


def ask_uuid(prompt: str) -> UUID:
    raw = read_line(prompt).strip()

    try:
        return UUID(raw)
    except ValueError as error:
        raise ValidationError("Некорректный id") from error


def ask_bool(prompt: str) -> bool:
    raw = read_line(prompt).strip().casefold()

    if raw in ("да", "д", "y", "yes"):
        return True

    if raw in ("нет", "н", "n", "no"):
        return False

    raise ValidationError("Ответьте да или нет")


# Плоское меню без подменю. Консоль только спрашивает пользователя
# и печатает результат, а правила живут в сервисах и классах.
class Console:
    def __init__(
            self,
            owner_service: OwnerService,
            pet_service: PetService
    ) -> None:
        self.__owner_service = owner_service
        self.__pet_service = pet_service

    def run(self) -> None:
        actions: dict[str, Callable[[], None]] = {
            "1": self.__show_owners,
            "2": self.__add_owner,
            "3": self.__rename_owner,
            "4": self.__delete_owner,
            "5": self.__show_pets,
            "6": self.__find_pets,
            "7": self.__add_pet,
            "8": self.__change_pet,
            "9": self.__delete_pet,
        }

        try:
            while True:
                print(MENU)
                choice = read_line("Выберите пункт: ").strip()

                if choice == "0":
                    print("До свидания")
                    return

                action = actions.get(choice)

                if action is None:
                    print("Такого пункта нет")
                    continue

                self.__run_action(action)
        except (KeyboardInterrupt, EOFError):
            print()

    # Ошибки предметной области и ввода не завершают программу.
    @staticmethod
    def __run_action(action: Callable[[], None]) -> None:
        try:
            action()
        except PetsError as error:
            print(f"Ошибка: {error}")
        except (ValueError, TypeError) as error:
            print(f"Ошибка ввода: {error}")

    def __show_owners(self) -> None:
        owners = self.__owner_service.get_all_owners()

        if not owners:
            print("Владельцев пока нет")

        for owner in owners:
            print(f"{owner.id} | {owner.name.value}")

    def __add_owner(self) -> None:
        owner = Owner(uuid4(), OwnerName(read_line("Имя владельца: ")))

        self.__owner_service.add_owner(owner)
        print(f"Владелец добавлен, id: {owner.id}")

    def __rename_owner(self) -> None:
        owner_id = ask_uuid("id владельца: ")
        name = OwnerName(read_line("Новое имя: "))

        self.__owner_service.rename_owner(owner_id, name)
        print("Имя изменено")

    def __delete_owner(self) -> None:
        self.__owner_service.delete_owner(ask_uuid("id владельца: "))
        print("Владелец удален")

    def __show_pets(self) -> None:
        pets = self.__pet_service.get_all_pets()

        if not pets:
            print("Животных пока нет")

        for pet in pets:
            self.__print_pet(pet)

    def __find_pets(self) -> None:
        text = read_line("Часть клички: ")

        for pet in self.__pet_service.find_pets_by_nickname(text):
            self.__print_pet(pet)

    def __add_pet(self) -> None:
        owner_id = ask_uuid("id владельца: ")
        kind = read_line("Вид: 1 - кошка, 2 - собака: ").strip()
        nickname = Nickname(read_line("Кличка: "))
        weight = Weight(ask_float("Вес, кг: "))

        pet: Pet
        if kind == "1":
            pet = Cat(
                pet_id=uuid4(),
                owner_id=owner_id,
                nickname=nickname,
                weight=weight,
                lives_indoor=ask_bool("Живет дома (да/нет): "),
            )
        elif kind == "2":
            pet = Dog(
                pet_id=uuid4(),
                owner_id=owner_id,
                nickname=nickname,
                weight=weight,
                walks_per_day=ask_int("Прогулок в день: "),
            )
        else:
            raise ValidationError("Выберите 1 или 2")

        self.__pet_service.add_pet(pet)
        print(f"Животное добавлено, id: {pet.id}")

    def __change_pet(self) -> None:
        pet_id = ask_uuid("id животного: ")
        nickname = Nickname(read_line("Новая кличка: "))
        weight = Weight(ask_float("Новый вес, кг: "))

        self.__pet_service.change_pet(pet_id, nickname, weight)
        print("Животное изменено")

    def __delete_pet(self) -> None:
        self.__pet_service.delete_pet(ask_uuid("id животного: "))
        print("Животное удалено")

    @staticmethod
    def __print_pet(pet: Pet) -> None:
        print(
            f"{pet.id} | {pet.nickname.value} | "
            f"{pet.weight.kilograms:g} кг | {pet.specification} | "
            f"владелец {pet.owner_id}"
        )
