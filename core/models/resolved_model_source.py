from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ResolvedModelSource:
    """
    Represents the resolved runtime source of a model.
    """

    type: str
    repository_id: str | None = None
    local_path: Path | None = None

    @property
    def is_repository(self) -> bool:
        return self.type == "repository"

    @property
    def is_local(self) -> bool:
        return self.type in {
            "asset",
            "path",
        }

    def to_dict(self) -> dict[str, str | None]:
        return {
            "type": self.type,
            "repository_id": self.repository_id,
            "local_path": (
                str(self.local_path)
                if self.local_path
                else None
            ),
        }