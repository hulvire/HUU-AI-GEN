from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class HistoryDetails:
    """
    Represents complete metadata for one saved generation.
    """

    image_path: Path
    metadata_path: Path

    created_at: str

    prompt: str
    negative_prompt: str
    seed: int

    model_id: str
    model_name: str
    repository_id: str | None
    backend: str

    mode: str

    preset_id: str | None
    preset_name: str | None

    scheduler_id: str | None
    scheduler_name: str | None

    loras: tuple[dict[str, Any], ...]

    width: int
    height: int
    steps: int
    guidance_scale: float
    duration_seconds: float

    input_used: bool
    input_image_path: Path | None
    strength: float | None

    application_name: str
    application_version: str
    application_environment: str