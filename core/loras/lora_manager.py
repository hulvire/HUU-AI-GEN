import json
from pathlib import Path
from typing import Iterator

from core.loras.lora_definition import (
    LoRADefinition,
)
from core.loras.lora_runtime import (
    LoRARuntime,
)

class LoRAManager:
    """
    Load, validate and provide LoRA definitions.

    Other application components should request LoRAs
    through this manager instead of reading JSON files
    directly.
    """

    def __init__(
        self,
        loras_directory: Path,
    ) -> None:
        self._loras_directory = (
            loras_directory.resolve()
        )

        self._loras: dict[
            str,
            LoRADefinition,
        ] = {}

        self._errors: dict[
            Path,
            str,
        ] = {}

    @property
    def loras_directory(self) -> Path:
        return self._loras_directory

    def scan(self) -> None:
        """
        Reload all LoRA definitions.
        """
        self._loras.clear()
        self._errors.clear()

        if not self._loras_directory.exists():
            self._loras_directory.mkdir(
                parents=True,
                exist_ok=True,
            )
            return

        for file_path in sorted(
            self._loras_directory.glob(
                "*.json"
            )
        ):
            self._load_file(file_path)

        self._validate_catalog()

    def get(
        self,
        lora_id: str,
    ) -> LoRADefinition | None:
        return self._loras.get(lora_id)

    def require(
        self,
        lora_id: str,
    ) -> LoRADefinition:
        lora = self.get(lora_id)

        if lora is None:
            raise ValueError(
                f"LoRA was not found: {lora_id}"
            )

        return lora

    def get_default(
        self,
    ) -> LoRADefinition | None:
        enabled_loras = self.all(
            enabled_only=True,
        )

        for lora in enabled_loras:
            if lora.default:
                return lora

        return (
            enabled_loras[0]
            if enabled_loras
            else None
        )

    def get_default_id(
        self,
    ) -> str | None:
        lora = self.get_default()

        return lora.id if lora else None

    def get_choices(
        self,
        enabled_only: bool = True,
    ) -> list[tuple[str, str]]:
        return [
            (
                lora.name,
                lora.id,
            )
            for lora in self.all(
                enabled_only=enabled_only,
            )
        ]

    def all(
        self,
        enabled_only: bool = False,
    ) -> tuple[LoRADefinition, ...]:
        loras = self._loras.values()

        if enabled_only:
            loras = (
                lora
                for lora in loras
                if lora.enabled
            )

        return tuple(
            sorted(
                loras,
                key=lambda lora: (
                    lora.name.lower(),
                    lora.id.lower(),
                ),
            )
        )

    def compatible_with_model(
        self,
        model_id: str,
        *,
        enabled_only: bool = True,
    ) -> tuple[LoRADefinition, ...]:
        return tuple(
            lora
            for lora in self.all(
                enabled_only=enabled_only,
            )
            if lora.is_compatible_with_model(
                model_id
            )
        )

    def compatible_with_backend(
        self,
        backend: str,
        *,
        enabled_only: bool = True,
    ) -> tuple[LoRADefinition, ...]:
        return tuple(
            lora
            for lora in self.all(
                enabled_only=enabled_only,
            )
            if lora.is_compatible_with_backend(
                backend
            )
        )

    def has(
        self,
        lora_id: str,
    ) -> bool:
        return lora_id in self._loras

    def count(
        self,
        enabled_only: bool = False,
    ) -> int:
        return len(
            self.all(
                enabled_only=enabled_only,
            )
        )

    def get_errors(
        self,
    ) -> dict[Path, str]:
        return dict(self._errors)

    def has_errors(self) -> bool:
        return bool(self._errors)

    def __iter__(
        self,
    ) -> Iterator[LoRADefinition]:
        return iter(self.all())

    def _validate_catalog(self) -> None:
        default_loras = [
            lora
            for lora in self._loras.values()
            if lora.enabled
            and lora.default
        ]

        if len(default_loras) <= 1:
            return

        default_ids = ", ".join(
            lora.id
            for lora in default_loras
        )

        raise ValueError(
            "Multiple enabled LoRAs are marked "
            f"as default: {default_ids}"
        )

    def _load_file(
        self,
        file_path: Path,
    ) -> None:
        try:
            data = json.loads(
                file_path.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(data, dict):
                raise ValueError(
                    "The root JSON value "
                    "must be an object."
                )

            lora = LoRADefinition.from_dict(
                data=data,
                source_file=file_path,
            )

            lora.validate()

            if lora.id in self._loras:
                existing_file = (
                    self._loras[
                        lora.id
                    ].source_file
                )

                raise ValueError(
                    "Duplicate LoRA ID "
                    f"'{lora.id}'. "
                    "Already defined in: "
                    f"{existing_file}"
                )

            self._loras[lora.id] = lora

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exception:
            self._errors[file_path] = (
                f"{type(exception).__name__}: "
                f"{exception}"
            )


    def create_runtime(
        self,
        lora_id: str,
        *,
        scale: float | None = None,
        enabled: bool = True,
    ) -> LoRARuntime:
        """
        Create runtime configuration for a catalog LoRA.
        """
        definition = self.require(lora_id)

        if not definition.enabled:
            raise ValueError(
                f"LoRA is disabled: {lora_id}"
            )

        return LoRARuntime.from_definition(
            definition=definition,
            scale=scale,
            enabled=enabled,
        )

    def create_runtimes(
        self,
        selections: dict[str, float],
    ) -> tuple[LoRARuntime, ...]:
        """
        Create runtime configurations from ID-scale pairs.
        """
        return tuple(
            self.create_runtime(
                lora_id=lora_id,
                scale=scale,
            )
            for lora_id, scale in selections.items()
        )