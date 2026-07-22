from typing import Any

from core.paths import CONFIG
from services.json_service import load_json


def load_app_config() -> dict[str, Any]:
    """
    Load the main application configuration.
    """
    config_path = CONFIG / "app.json"

    config = load_json(config_path)

    if not isinstance(config, dict):
        raise ValueError(
            "Application configuration must be a JSON object."
        )

    return config