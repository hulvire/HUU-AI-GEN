import json
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict[str, Any]:
    """
    Load and decode a JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON content is invalid.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"JSON configuration file was not found: {file_path}"
        )

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON configuration in {file_path}: {error}"
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            f"JSON configuration must contain an object: {file_path}"
        )

    return data


def load_json_directory(directory: Path) -> list[dict[str, Any]]:
    """
    Load all JSON objects from a directory.
    """
    if not directory.exists():
        return []

    return [
        load_json(file_path)
        for file_path in sorted(directory.glob("*.json"))
    ]