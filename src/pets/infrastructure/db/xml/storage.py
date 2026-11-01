import xml.etree.ElementTree as ET
from pathlib import Path

from domain.exceptions import StorageError


# Читает записи из XML-файла с корнем <root>. Дочерние элементы
# и есть записи. Если файла еще нет, хранилище считается пустым.
def read_records(file_path: Path, root: str) -> list[ET.Element]:
    if not file_path.exists():
        return []

    try:
        document = ET.parse(file_path).getroot()
    except (OSError, ET.ParseError) as error:
        raise StorageError(
            f"Файл {file_path} повреждён или не читается"
        ) from error

    if document.tag != root:
        raise StorageError(f"В файле {file_path} корень должен быть <{root}>")

    return list(document)


def write_records(
        file_path: Path, root: str, records: list[ET.Element]
) -> None:
    document = ET.Element(root)
    document.extend(records)
    ET.indent(document, space="    ")

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(document).write(
            file_path, encoding="utf-8", xml_declaration=True
        )
    except OSError as error:
        raise StorageError(f"Не удалось записать файл {file_path}") from error


# Текст поля записи. Отсутствие поля - это повреждённые данные.
def read_text(element: ET.Element, tag: str) -> str:
    text = element.findtext(tag)

    if text is None:
        raise StorageError(f"В записи нет поля {tag}")

    return text
