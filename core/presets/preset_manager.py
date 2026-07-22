import json
from pathlib import Path
from typing import Iterator

from core.presets.preset_definition import (
    PresetDefinition,
)


class PresetManager:
    """
    Loads, validates and provides generation presets.

    Other application components should use this manager
    instead of reading preset JSON files directly.
    """

    def __init__(
        self,
        presets_directory: Path,
    ) -> None:
        self._presets_directory = (
            presets_directory.resolve()
        )

        self._presets: dict[
            str,
            PresetDefinition,
        ] = {}

        self._errors: dict[
            Path,
            str,
        ] = {}

    @property
    def presets_directory(self) -> Path:
        return self._presets_directory

    def scan(self) -> None:
        """
        Reload all presets from the presets directory.
        """
        self._presets.clear()
        self._errors.clear()

        if not self._presets_directory.exists():
            self._presets_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            return

        for file_path in sorted(
            self._presets_directory.glob("*.json")
        ):
            self._load_file(file_path)

        self._validate_catalog()

    def get(
        self,
        preset_id: str,
    ) -> PresetDefinition | None:
        """
        Return a preset by its unique ID.
        """
        return self._presets.get(preset_id)

    def require(
        self,
        preset_id: str,
    ) -> PresetDefinition:
        """
        Return a preset or raise an explicit error.
        """
        preset = self.get(preset_id)

        if preset is None:
            raise ValueError(
                f"Preset was not found: {preset_id}"
            )

        return preset

    def get_default(
        self,
    ) -> PresetDefinition | None:
        """
        Return the default enabled preset.

        When no preset is explicitly marked as default,
        return the first enabled preset sorted by name.
        """
        enabled_presets = self.all(
            enabled_only=True,
        )

        for preset in enabled_presets:
            if preset.default:
                return preset

        return (
            enabled_presets[0]
            if enabled_presets
            else None
        )

    def get_default_id(
        self,
    ) -> str | None:
        """
        Return the default enabled preset ID.
        """
        preset = self.get_default()

        return preset.id if preset else None

    def get_choices(
        self,
        enabled_only: bool = True,
    ) -> list[tuple[str, str]]:
        """
        Return preset choices for UI dropdowns.
        """
        return [
            (
                preset.name,
                preset.id,
            )
            for preset in self.all(
                enabled_only=enabled_only,
            )
        ]

    def all(
        self,
        enabled_only: bool = False,
    ) -> tuple[PresetDefinition, ...]:
        """
        Return all presets sorted by name.
        """
        presets = self._presets.values()

        if enabled_only:
            presets = (
                preset
                for preset in presets
                if preset.enabled
            )

        return tuple(
            sorted(
                presets,
                key=lambda preset: (
                    preset.name.lower(),
                    preset.id.lower(),
                ),
            )
        )

    def has(
        self,
        preset_id: str,
    ) -> bool:
        """
        Return whether a preset exists.
        """
        return preset_id in self._presets

    def count(
        self,
        enabled_only: bool = False,
    ) -> int:
        """
        Return the number of presets.
        """
        return len(
            self.all(
                enabled_only=enabled_only,
            )
        )

    def get_errors(
        self,
    ) -> dict[Path, str]:
        """
        Return errors found during the latest scan.
        """
        return dict(self._errors)

    def has_errors(self) -> bool:
        """
        Return whether the latest scan found errors.
        """
        return bool(self._errors)

    def __iter__(
        self,
    ) -> Iterator[PresetDefinition]:
        return iter(self.all())

    def _validate_catalog(self) -> None:
        """
        Validate relationships between loaded presets.
        """
        default_presets = [
            preset
            for preset in self._presets.values()
            if preset.enabled and preset.default
        ]

        if len(default_presets) <= 1:
            return

        default_ids = ", ".join(
            preset.id
            for preset in default_presets
        )

        raise ValueError(
            "Multiple enabled presets are marked "
            f"as default: {default_ids}"
        )

    def _load_file(
        self,
        file_path: Path,
    ) -> None:
        """
        Load and validate one preset JSON file.
        """
        try:
            data = json.loads(
                file_path.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(data, dict):
                raise ValueError(
                    "The root JSON value must "
                    "be an object."
                )

            preset = PresetDefinition.from_dict(
                data=data,
                source_file=file_path,
            )

            preset.validate()

            if preset.id in self._presets:
                existing_file = (
                    self._presets[
                        preset.id
                    ].source_file
                )

                raise ValueError(
                    "Duplicate preset ID "
                    f"'{preset.id}'. "
                    "Already defined in: "
                    f"{existing_file}"
                )

            self._presets[preset.id] = preset

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