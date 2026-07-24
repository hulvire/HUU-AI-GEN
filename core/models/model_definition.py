from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class ModelDefinition:
    """
    Immutable definition of one generator model.

    The object is created from a JSON configuration file
    and is used throughout the application instead of
    passing unstructured dictionaries.
    """

    id: str
    name: str
    backend: str

    enabled: bool = True
    default: bool = False

    model_path: str | None = None
    repository_id: str | None = None
    checkpoint_asset_id: str | None = None

    description: str = ""
    source_file: Path | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        source_file: Path | None = None,
    ) -> "ModelDefinition":
        """
        Create a model definition from decoded JSON data.
        """
        model_id = str(
            data.get("id", "")
        ).strip()

        name = str(
            data.get("name", model_id)
        ).strip()

        backend = str(
            data.get("backend", "")
        ).strip()

        known_fields = {
            "id",
            "name",
            "backend",
            "enabled",
            "default",
            "model_path",
            "repository_id",
            "checkpoint_asset_id",
            "description",
        }

        metadata = {
            key: value
            for key, value in data.items()
            if key not in known_fields
        }

        return cls(
            id=model_id,
            name=name,
            backend=backend,
            enabled=bool(
                data.get("enabled", True)
            ),
            default=bool(
                data.get("default", False)
            ),
            model_path=cls._optional_string(
                data.get("model_path")
            ),
            repository_id=cls._optional_string(
                data.get("repository_id")
            ),
            checkpoint_asset_id=cls._optional_string(
                data.get("checkpoint_asset_id")
            ),
            description=str(
                data.get("description", "")
            ).strip(),
            source_file=source_file,
            metadata=metadata,
        )

    def validate(self) -> None:
        """
        Validate the model definition.
        """
        if not self.id:
            raise ValueError(
                "Model ID cannot be empty."
            )

        if not self.name:
            raise ValueError(
                "Model name cannot be empty."
            )

        if not self.backend:
            raise ValueError(
                "Model backend cannot be empty."
            )

        configured_sources = [
            source
            for source in (
                self.checkpoint_asset_id,
                self.model_path,
                self.repository_id,
            )
            if source
        ]

        if len(configured_sources) > 1:
            raise ValueError(
                "Model can use only one source: "
                "checkpoint_asset_id, model_path "
                "or repository_id."
            )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read an optional backend-specific metadata value.
        """
        return self.metadata.get(
            key,
            default,
        )

    @property
    def family(self) -> str:
        """
        Return the model family.
        """
        family = self.get(
            "family",
            "",
        )

        return str(family).strip()

    @property
    def runtime(self) -> dict[str, Any]:
        """
        Return validated runtime configuration.
        """
        runtime = self.get(
            "runtime",
            {},
        )

        if not isinstance(runtime, dict):
            return {}

        return runtime

    @property
    def generation_defaults(
        self,
    ) -> dict[str, Any]:
        """
        Return validated generation defaults.
        """
        defaults = self.get(
            "generation_defaults",
            {},
        )

        if not isinstance(defaults, dict):
            return {}

        return defaults

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the definition into a serializable dictionary.
        """
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "backend": self.backend,
            "enabled": self.enabled,
            "default": self.default,
            "checkpoint_asset_id": (
                self.checkpoint_asset_id
            ),
            "description": self.description,
        }

        if self.model_path is not None:
            result["model_path"] = self.model_path

        if self.repository_id is not None:
            result["repository_id"] = (
                self.repository_id
            )

        result.update(self.metadata)

        return result

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        """
        Normalize an optional string value.
        """
        if value is None:
            return None

        normalized = str(value).strip()

        return normalized or None

    @property
    def source_type(self) -> str:
        """
        Return the configured source type of the model.
        """
        if self.checkpoint_asset_id:
            return "asset"

        if self.model_path:
            return "path"

        if self.repository_id:
            return "repository"

        return "undefined"

    @property
    def has_source(self) -> bool:
        """
        Return whether the model has any configured source.
        """
        return self.source_type != "undefined"