"""Чтение и запись реестра в формате XML."""
import xml.etree.ElementTree as ET
from typing import Any, Dict

from exceptions import PetsError, StorageError
from models import PetRegistry


def _text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _pet_to_xml(parent: ET.Element, data: Dict[str, Any]) -> None:
    pet = ET.SubElement(parent, "pet", {"type": str(data["type"])})
    for key, value in data.items():
        if key in ("type", "vaccinations"):
            continue
        ET.SubElement(pet, key).text = _text(value)
    vaccs = ET.SubElement(pet, "vaccinations")
    for item in data["vaccinations"]:
        ET.SubElement(vaccs, "vaccination",
                      {"name": item["name"], "date": item["date"]})


def _pet_from_xml(element: ET.Element) -> Dict[str, Any]:
    data: Dict[str, Any] = {"type": element.attrib["type"],
                            "vaccinations": []}
    for child in element:
        if child.tag == "vaccinations":
            data["vaccinations"] = [dict(v.attrib) for v in child]
        else:
            data[child.tag] = child.text or ""
    return data


def save_xml(registry: PetRegistry, path: str) -> None:
    root = ET.Element("registry")
    for owner in registry.to_dict()["owners"]:
        owner_el = ET.SubElement(root, "owner", {
            "name": owner["name"], "phone": owner["phone"]})
        for pet in owner["pets"]:
            _pet_to_xml(owner_el, pet)
    ET.indent(root)
    try:
        ET.ElementTree(root).write(path, encoding="utf-8",
                                   xml_declaration=True)
    except OSError as exc:
        raise StorageError(f"Не удалось записать {path}: {exc}") from exc


def load_xml(path: str) -> PetRegistry:
    try:
        root = ET.parse(path).getroot()
        owners = [{
            "name": o.attrib["name"],
            "phone": o.attrib["phone"],
            "pets": [_pet_from_xml(p) for p in o.findall("pet")],
        } for o in root.findall("owner")]
        return PetRegistry.from_dict({"owners": owners})
    except OSError as exc:
        raise StorageError(f"Не удалось прочитать {path}: {exc}") from exc
    except ET.ParseError as exc:
        raise StorageError(f"Некорректный XML в {path}: {exc}") from exc
    except (KeyError, TypeError, ValueError, AttributeError,
            PetsError) as exc:
        raise StorageError(f"Неверная структура данных: {exc!r}") from exc
