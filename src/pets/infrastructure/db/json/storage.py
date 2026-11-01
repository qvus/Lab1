import json
from pathlib import Path
from typing import Any

from domain.exceptions import StorageError


# Читает записи из JSON-файла вида {"<root>": [...]}.
# Если файла еще нет, хранилище считается пустым.
def read_records(file_path: Path, root: str) -> list[dict[str, Any]]:
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data: Any = json.load(file)
    except (OSError, ValueError) as error:
        raise StorageError(f"Не удалось прочитать файл {file_path}") from error

    records = data.get(root) if isinstance(data, dict) else None

    if not isinstance(records, list) or not all(
        isinstance(record, dict) for record in records
    ):
        raise StorageError(f"В файле {file_path} нет списка {root}")

    return list(records)


# Записывает все записи целиком: файл маленький, поэтому
# проще переписать его, чем менять по частям.
def write_records(
        file_path: Path, root: str, records: list[dict[str, Any]]
) -> None:
    content = json.dumps({root: records}, ensure_ascii=False, indent=4)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
    except OSError as error:
        raise StorageError(f"Не удалось записать файл {file_path}") from error
