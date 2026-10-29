"""Чтение и запись реестра в формате JSON."""
import json
from typing import Any

from exceptions import PetsError, StorageError
from models import PetRegistry


def save_json(registry: PetRegistry, path: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(registry.to_dict(), file,
                      ensure_ascii=False, indent=2)
    except OSError as exc:
        raise StorageError(f"Не удалось записать {path}: {exc}") from exc


def load_json(path: str) -> PetRegistry:
    try:
        with open(path, encoding="utf-8") as file:
            data: Any = json.load(file)
        return PetRegistry.from_dict(data)
    except OSError as exc:
        raise StorageError(f"Не удалось прочитать {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise StorageError(f"Некорректный JSON в {path}: {exc}") from exc
    except (KeyError, TypeError, ValueError, AttributeError,
            PetsError) as exc:
        raise StorageError(f"Неверная структура данных: {exc!r}") from exc
