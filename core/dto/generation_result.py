from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(slots=True)
class GenerationResult:
    """
    Contains the completed image and generation information.
    """

    image: Image.Image
    seed: int
    duration_seconds: float

    model_id: str
    model_name: str

    width: int
    height: int

    steps: int
    guidance_scale: float

    image_path: Path | None = None
    metadata_path: Path | None = None