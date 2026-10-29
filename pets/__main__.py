"""Консольное приложение «Домашние животные»."""
from datetime import date
from typing import Callable, Dict

from exceptions import PetsError
from json_storage import load_json, save_json
from models import Bird, Cat, Dog, Owner, Pet, PetRegistry, Vaccination
from xml_storage import load_xml, save_xml

JSON_PATH = "data/pets.json"
XML_PATH = "data/pets.xml"

MENU = """
1. Показать всех
2. Добавить владельца
3. Добавить животное
4. Добавить прививку
5. Покормить животное
6. Сохранить в JSON
7. Загрузить из JSON
8. Сохранить в XML
9. Загрузить из XML
0. Выход
"""


def show(registry: PetRegistry) -> None:
    if not registry.owners:
        print("Реестр пуст")
    for owner in registry.owners:
        print(f"{owner.name} ({owner.phone})")
        for pet in owner.pets:
            print(f"  - {pet.describe()} [{pet.sound()}]")
            for vacc in pet.vaccinations:
                print(f"      прививка: {vacc.name}, {vacc.when}")


def add_owner(registry: PetRegistry) -> None:
    registry.add_owner(Owner(input("Имя: "), input("Телефон: ")))


def make_pet() -> Pet:
    kind = input("Вид (dog/cat/bird): ").strip().lower()
    name = input("Кличка: ")
    age = int(input("Возраст: "))
    weight = float(input("Вес, кг: "))
    if kind == "dog":
        return Dog(name, age, weight, input("Порода: "))
    if kind == "cat":
        return Cat(name, age, weight)
    if kind == "bird":
        return Bird(name, age, weight)
    raise PetsError(f"Неизвестный вид: {kind}")


def add_pet(registry: PetRegistry) -> None:
    owner = registry.get_owner(input("Владелец: "))
    owner.add_pet(make_pet())


def add_vaccination(registry: PetRegistry) -> None:
    owner = registry.get_owner(input("Владелец: "))
    pet = owner.find_pet(input("Кличка: "))
    name = input("Прививка: ")
    when = date.fromisoformat(input("Дата (ГГГГ-ММ-ДД): "))
    pet.add_vaccination(Vaccination(name, when))


def feed(registry: PetRegistry) -> None:
    owner = registry.get_owner(input("Владелец: "))
    pet = owner.find_pet(input("Кличка: "))
    print(pet.feed(int(input("Граммы: "))))


def main() -> None:
    registry = PetRegistry()
    actions: Dict[str, Callable[[], None]] = {
        "1": lambda: show(registry),
        "2": lambda: add_owner(registry),
        "3": lambda: add_pet(registry),
        "4": lambda: add_vaccination(registry),
        "5": lambda: feed(registry),
        "6": lambda: save_json(registry, JSON_PATH),
        "8": lambda: save_xml(registry, XML_PATH),
    }
    while True:
        print(MENU)
        choice = input("Выбор: ").strip()
        if choice == "0":
            break
        try:
            if choice == "7":
                registry = load_json(JSON_PATH)
            elif choice == "9":
                registry = load_xml(XML_PATH)
            elif choice in actions:
                actions[choice]()
            else:
                print("Нет такого пункта меню")
                continue
            print("Готово")
        except PetsError as exc:  # собственные исключения
            print(f"Ошибка: {exc}")
        except ValueError as exc:  # встроенное: int(), float(), date
            print(f"Неверный ввод: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nВвод прерван")
            break


if __name__ == "__main__":
    main()
