from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class LoRADefinition:
    """
    Immutable definition of one LoRA adapter.

    The definition is loaded from JSON and describes
    where the LoRA comes from and how it should be used.
    """

    id: str
    name: str

    enabled: bool = True
    default: bool = False

    repository_id: str | None = None
    weight_name: str | None = None
    file_path: str | None = None

    default_scale: float = 1.0
    min_scale: float = 0.0
    max_scale: float = 2.0

    compatible_backends: tuple[str, ...] = ()
    compatible_models: tuple[str, ...] = ()

    trigger_words: tuple[str, ...] = ()

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
    ) -> "LoRADefinition":
        """
        Create a LoRA definition from decoded JSON data.
        """
        lora_id = str(
            data.get("id", "")
        ).strip()

        name = str(
            data.get("name", lora_id)
        ).strip()

        known_fields = {
            "id",
            "name",
            "enabled",
            "default",
            "repository_id",
            "weight_name",
            "file_path",
            "default_scale",
            "min_scale",
            "max_scale",
            "compatible_backends",
            "compatible_models",
            "trigger_words",
            "description",
        }

        metadata = {
            key: value
            for key, value in data.items()
            if key not in known_fields
        }

        return cls(
            id=lora_id,
            name=name,
            enabled=bool(
                data.get("enabled", True)
            ),
            default=bool(
                data.get("default", False)
            ),
            repository_id=cls._optional_string(
                data.get("repository_id")
            ),
            weight_name=cls._optional_string(
                data.get("weight_name")
            ),
            file_path=cls._optional_string(
                data.get("file_path")
            ),
            default_scale=float(
                data.get("default_scale", 1.0)
            ),
            min_scale=float(
                data.get("min_scale", 0.0)
            ),
            max_scale=float(
                data.get("max_scale", 2.0)
            ),
            compatible_backends=cls._string_tuple(
                data.get("compatible_backends")
            ),
            compatible_models=cls._string_tuple(
                data.get("compatible_models")
            ),
            trigger_words=cls._string_tuple(
                data.get("trigger_words")
            ),
            description=str(
                data.get("description", "")
            ).strip(),
            source_file=source_file,
            metadata=metadata,
        )

    def validate(self) -> None:
        """
        Validate the LoRA definition.
        """
        if not self.id:
            raise ValueError(
                "LoRA ID cannot be empty."
            )

        if not self.name:
            raise ValueError(
                "LoRA name cannot be empty."
            )

        configured_sources = [
            source
            for source in (
                self.repository_id,
                self.file_path,
            )
            if source
        ]

        if len(configured_sources) > 1:
            raise ValueError(
                "LoRA can use only one source: "
                "repository_id or file_path."
            )

        if (
            self.weight_name
            and not self.repository_id
        ):
            raise ValueError(
                "LoRA weight_name requires "
                "repository_id."
            )

        if self.min_scale > self.max_scale:
            raise ValueError(
                "LoRA min_scale cannot be greater "
                "than max_scale."
            )

        if not (
            self.min_scale
            <= self.default_scale
            <= self.max_scale
        ):
            raise ValueError(
                "LoRA default_scale must be between "
                "min_scale and max_scale."
            )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read optional LoRA-specific metadata.
        """
        return self.metadata.get(
            key,
            default,
        )

    def is_compatible_with_model(
        self,
        model_id: str,
    ) -> bool:
        """
        Return whether the LoRA supports the model.

        An empty compatible_models collection means that
        compatibility is not restricted by model ID.
        """
        if not self.compatible_models:
            return True

        return model_id in self.compatible_models

    def is_compatible_with_backend(
        self,
        backend: str,
    ) -> bool:
        """
        Return whether the LoRA supports the backend.

        An empty compatible_backends collection means that
        compatibility is not restricted by backend.
        """
        if not self.compatible_backends:
            return True

        normalized_backend = (
            backend.strip().lower()
        )

        return any(
            item.lower() == normalized_backend
            for item in self.compatible_backends
        )

    @property
    def source_type(self) -> str:
        """
        Return the configured source type.
        """
        if self.file_path:
            return "path"

        if self.repository_id:
            return "repository"

        return "undefined"

    @property
    def has_source(self) -> bool:
        return self.source_type != "undefined"

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()

        return normalized or None

    @staticmethod
    def _string_tuple(
        value: Any,
    ) -> tuple[str, ...]:
        if value is None:
            return ()

        if isinstance(value, str):
            normalized = value.strip()

            return (
                (normalized,)
                if normalized
                else ()
            )

        if not isinstance(
            value,
            (list, tuple),
        ):
            raise ValueError(
                "Expected a string or a list "
                "of strings."
            )

        result = []

        for item in value:
            normalized = str(item).strip()

            if normalized:
                result.append(normalized)

        return tuple(result)