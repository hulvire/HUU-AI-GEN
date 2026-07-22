import json
from pathlib import Path
from typing import Iterator

from core.models.model_definition import (
    ModelDefinition,
)


class ModelManager:
    """
    Loads, validates and provides model definitions.

    ModelManager owns the runtime model catalog. Other application
    components should ask this manager for models instead of reading
    JSON files directly.
    """

    def __init__(
        self,
        models_directory: Path,
    ) -> None:
        self._models_directory = (
            models_directory.resolve()
        )

        self._models: dict[
            str,
            ModelDefinition,
        ] = {}

        self._errors: dict[
            Path,
            str,
        ] = {}

    @property
    def models_directory(self) -> Path:
        return self._models_directory

    def scan(self) -> None:
        """
        Reload all model definitions from the models directory.
        """
        self._models.clear()
        self._errors.clear()

        if not self._models_directory.exists():
            self._models_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            return

        for file_path in sorted(
            self._models_directory.glob("*.json")
        ):
            self._load_file(file_path)

        self._validate_catalog()

    def _validate_catalog(self) -> None:
        """
        Validate relationships between loaded model definitions.
        """
        default_models = [
            model
            for model in self._models.values()
            if model.enabled and model.default
        ]

        if len(default_models) <= 1:
            return

        default_ids = ", ".join(
            model.id
            for model in default_models
        )

        raise ValueError(
            "Multiple enabled models are marked as default: "
            f"{default_ids}"
        )

    def get(
        self,
        model_id: str,
    ) -> ModelDefinition | None:
        """
        Return a model by its unique ID.
        """
        return self._models.get(model_id)

    def get_default(
        self,
    ) -> ModelDefinition | None:
        """
        Return the enabled model marked as default.

        When no model is explicitly marked as default,
        return the first enabled model sorted by name.
        """
        enabled_models = self.all(
            enabled_only=True,
        )

        for model in enabled_models:
            if model.default:
                return model

        return (
            enabled_models[0]
            if enabled_models
            else None
        )


    def get_default_id(
        self,
    ) -> str | None:
        """
        Return the default enabled model ID.
        """
        model = self.get_default()

        return model.id if model else None


    def get_choices(
        self,
        enabled_only: bool = True,
    ) -> list[tuple[str, str]]:
        """
        Return model choices for UI dropdowns.
        """
        return [
            (
                model.name,
                model.id,
            )
            for model in self.all(
                enabled_only=enabled_only,
            )
        ]

    def require(
        self,
        model_id: str,
    ) -> ModelDefinition:
        """
        Return a model or raise an explicit error.
        """
        model = self.get(model_id)

        if model is None:
            raise ValueError(
                f"Model was not found: {model_id}"
            )

        return model

    def all(
        self,
        enabled_only: bool = False,
    ) -> tuple[ModelDefinition, ...]:
        """
        Return all model definitions sorted by name.
        """
        models = self._models.values()

        if enabled_only:
            models = (
                model
                for model in models
                if model.enabled
            )

        return tuple(
            sorted(
                models,
                key=lambda model: (
                    model.name.lower(),
                    model.id.lower(),
                ),
            )
        )

    def by_backend(
        self,
        backend: str,
        enabled_only: bool = True,
    ) -> tuple[ModelDefinition, ...]:
        """
        Return models using the selected generator backend.
        """
        normalized_backend = (
            backend.strip().lower()
        )

        return tuple(
            model
            for model in self.all(
                enabled_only=enabled_only
            )
            if model.backend.lower()
            == normalized_backend
        )

    def has(
        self,
        model_id: str,
    ) -> bool:
        return model_id in self._models

    def count(
        self,
        enabled_only: bool = False,
    ) -> int:
        return len(
            self.all(
                enabled_only=enabled_only
            )
        )

    def get_errors(
        self,
    ) -> dict[Path, str]:
        """
        Return configuration errors found during the latest scan.
        """
        return dict(self._errors)

    def has_errors(self) -> bool:
        return bool(self._errors)

    def __iter__(
        self,
    ) -> Iterator[ModelDefinition]:
        return iter(self.all())

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
                    "The root JSON value must be an object."
                )

            model = ModelDefinition.from_dict(
                data=data,
                source_file=file_path,
            )

            model.validate()

            if model.id in self._models:
                existing_file = (
                    self._models[
                        model.id
                    ].source_file
                )

                raise ValueError(
                    "Duplicate model ID "
                    f"'{model.id}'. "
                    f"Already defined in: "
                    f"{existing_file}"
                )

            self._models[model.id] = model

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