from typing import Any

from core.paths import RESOLUTION_CONFIGS
from services.json_service import load_json_directory


def get_resolutions() -> list[dict[str, Any]]:
    """
    Return all enabled resolution configurations.
    """
    resolutions = load_json_directory(RESOLUTION_CONFIGS)

    return [
        resolution
        for resolution in resolutions
        if resolution.get("enabled", True)
    ]


def get_resolution_choices() -> list[tuple[str, str]]:
    """
    Return dropdown choices containing a visible label
    and an internal resolution ID.
    """
    return [
        (
            (
                f"{resolution['name']} — "
                f"{resolution['width']} × {resolution['height']}"
            ),
            resolution["id"],
        )
        for resolution in get_resolutions()
    ]


def get_default_resolution_id() -> str | None:
    resolutions = get_resolutions()

    for resolution in resolutions:
        if resolution.get("default", False):
            return resolution["id"]

    return resolutions[0]["id"] if resolutions else None


def get_resolution(
    resolution_id: str,
) -> dict[str, Any] | None:
    for resolution in get_resolutions():
        if resolution["id"] == resolution_id:
            return resolution

    return None