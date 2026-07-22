from dataclasses import dataclass

from core.loras.lora_definition import (
    LoRADefinition,
)


@dataclass(slots=True)
class LoRARuntime:
    """
    Runtime configuration of one LoRA adapter.

    A LoRA definition describes the adapter globally.
    A LoRA runtime instance describes how the adapter
    should be used during one generation request.
    """

    definition: LoRADefinition
    scale: float
    enabled: bool = True

    def __post_init__(self) -> None:
        self.validate()

    @property
    def id(self) -> str:
        return self.definition.id

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def adapter_name(self) -> str:
        """
        Return a stable Diffusers adapter name.
        """
        normalized = "".join(
            character
            if character.isalnum()
            else "_"
            for character in self.definition.id
        )

        return normalized.strip("_")

    @property
    def repository_id(self) -> str | None:
        return self.definition.repository_id

    @property
    def weight_name(self) -> str | None:
        return self.definition.weight_name

    @property
    def file_path(self) -> str | None:
        return self.definition.file_path

    @property
    def trigger_words(self) -> tuple[str, ...]:
        return self.definition.trigger_words

    @property
    def source_type(self) -> str:
        return self.definition.source_type

    @property
    def has_source(self) -> bool:
        return self.definition.has_source

    @property
    def is_active(self) -> bool:
        """
        Return whether this adapter should be applied.
        """
        return self.enabled and self.scale > 0.0

    def validate(self) -> None:
        """
        Validate runtime-specific configuration.
        """
        if not self.adapter_name:
            raise ValueError(
                "LoRA adapter name cannot be empty."
            )

        if not (
            self.definition.min_scale
            <= self.scale
            <= self.definition.max_scale
        ):
            raise ValueError(
                f"LoRA scale for '{self.id}' must be "
                f"between {self.definition.min_scale} "
                f"and {self.definition.max_scale}. "
                f"Received: {self.scale}"
            )

    def with_scale(
        self,
        scale: float,
    ) -> "LoRARuntime":
        """
        Return a copy with a different scale.
        """
        return LoRARuntime(
            definition=self.definition,
            scale=scale,
            enabled=self.enabled,
        )

    def with_enabled(
        self,
        enabled: bool,
    ) -> "LoRARuntime":
        """
        Return a copy with a different enabled state.
        """
        return LoRARuntime(
            definition=self.definition,
            scale=self.scale,
            enabled=enabled,
        )

    @classmethod
    def from_definition(
        cls,
        definition: LoRADefinition,
        *,
        scale: float | None = None,
        enabled: bool = True,
    ) -> "LoRARuntime":
        """
        Create runtime configuration from a definition.
        """
        resolved_scale = (
            definition.default_scale
            if scale is None
            else scale
        )

        return cls(
            definition=definition,
            scale=resolved_scale,
            enabled=enabled,
        )