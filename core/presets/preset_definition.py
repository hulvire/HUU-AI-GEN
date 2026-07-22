from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class PresetDefinition:
    """
    Immutable definition of one generation preset.

    Presets provide recommended prompt fragments and
    generation settings without containing runtime state.
    """

    id: str
    name: str

    enabled: bool = True
    default: bool = False

    description: str = ""

    prompt_prefix: str = ""
    prompt_suffix: str = ""
    negative_prompt: str = ""

    steps: int | None = None
    guidance_scale: float | None = None
    scheduler: str | None = None
    strength: float | None = None

    source_file: Path | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        source_file: Path | None = None,
    ) -> "PresetDefinition":
        """
        Create a preset definition from decoded JSON data.
        """
        preset_id = str(
            data.get("id", "")
        ).strip()

        name = str(
            data.get("name", preset_id)
        ).strip()

        known_fields = {
            "id",
            "name",
            "enabled",
            "default",
            "description",
            "prompt_prefix",
            "prompt_suffix",
            "negative_prompt",
            "steps",
            "guidance_scale",
            "scheduler",
            "strength",
        }

        metadata = {
            key: value
            for key, value in data.items()
            if key not in known_fields
        }

        return cls(
            id=preset_id,
            name=name,
            enabled=bool(
                data.get("enabled", True)
            ),
            default=bool(
                data.get("default", False)
            ),
            description=str(
                data.get("description", "")
            ).strip(),
            prompt_prefix=str(
                data.get("prompt_prefix", "")
            ).strip(),
            prompt_suffix=str(
                data.get("prompt_suffix", "")
            ).strip(),
            negative_prompt=str(
                data.get("negative_prompt", "")
            ).strip(),
            steps=cls._optional_int(
                data.get("steps")
            ),
            guidance_scale=cls._optional_float(
                data.get("guidance_scale")
            ),
            scheduler=cls._optional_string(
                data.get("scheduler")
            ),
            strength=cls._optional_float(
                data.get("strength")
            ),
            source_file=source_file,
            metadata=metadata,
        )

    def validate(self) -> None:
        """
        Validate the preset definition.
        """
        if not self.id:
            raise ValueError(
                "Preset ID cannot be empty."
            )

        if not self.name:
            raise ValueError(
                "Preset name cannot be empty."
            )

        if (
            self.steps is not None
            and self.steps < 1
        ):
            raise ValueError(
                "Preset steps must be greater "
                "than zero."
            )

        if (
            self.guidance_scale is not None
            and self.guidance_scale < 0
        ):
            raise ValueError(
                "Preset guidance scale cannot "
                "be negative."
            )

        if (
            self.strength is not None
            and not 0.0 < self.strength <= 1.0
        ):
            raise ValueError(
                "Preset strength must be greater "
                "than 0 and at most 1."
            )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read an optional preset metadata value.
        """
        return self.metadata.get(
            key,
            default,
        )

    def build_prompt(
        self,
        prompt: str,
    ) -> str:
        """
        Combine the preset prompt fragments
        with a user prompt.
        """
        parts = (
            self.prompt_prefix,
            prompt.strip(),
            self.prompt_suffix,
        )

        return ", ".join(
            part.strip(" ,")
            for part in parts
            if part and part.strip(" ,")
        )

    def build_negative_prompt(
        self,
        negative_prompt: str,
    ) -> str:
        """
        Combine the preset negative prompt
        with a user negative prompt.
        """
        parts = (
            self.negative_prompt,
            negative_prompt.strip(),
        )

        return ", ".join(
            part.strip(" ,")
            for part in parts
            if part and part.strip(" ,")
        )

    def build_ui_settings(self) -> dict[str, object]:
        """
        Return UI values represented by this preset.
        """
        return {
            "scheduler": self.scheduler,
            "steps": self.steps,
            "guidance_scale": self.guidance_scale,
            "strength": self.strength,
            "negative_prompt": self.negative_prompt,
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the preset into a serializable dictionary.
        """
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "default": self.default,
            "description": self.description,
            "prompt_prefix": self.prompt_prefix,
            "prompt_suffix": self.prompt_suffix,
            "negative_prompt": self.negative_prompt,
        }

        if self.steps is not None:
            result["steps"] = self.steps

        if self.guidance_scale is not None:
            result["guidance_scale"] = (
                self.guidance_scale
            )

        if self.scheduler is not None:
            result["scheduler"] = self.scheduler

        if self.strength is not None:
            result["strength"] = self.strength

        result.update(self.metadata)

        return result

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()

        return normalized or None

    @staticmethod
    def _optional_int(
        value: Any,
    ) -> int | None:
        if value is None:
            return None

        return int(value)

    @staticmethod
    def _optional_float(
        value: Any,
    ) -> float | None:
        if value is None:
            return None

        return float(value)