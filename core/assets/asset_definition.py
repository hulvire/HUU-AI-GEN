from dataclasses import dataclass
from pathlib import Path

from core.assets.asset_type import AssetType


@dataclass(slots=True, frozen=True)
class AssetDefinition:
    """
    Represents one physical AI asset stored on disk.
    """

    id: str
    name: str
    type: AssetType
    path: Path
    extension: str
    size_bytes: int

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def size_megabytes(self) -> float:
        return round(
            self.size_bytes / 1024 / 1024,
            2,
        )

    def to_dict(self) -> dict[str, object]:
        """
        Convert the asset into a serializable dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "path": str(self.path),
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "size_megabytes": self.size_megabytes,
        }