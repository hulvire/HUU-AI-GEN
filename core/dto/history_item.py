from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class HistoryItem:
    """
    Represents one generated image stored in outputs/.
    """

    image_path: Path
    metadata_path: Path

    created_at: str

    prompt: str
    negative_prompt: str

    model: str
    preset: str
    scheduler: str

    width: int
    height: int

    seed: int

    duration_seconds: float