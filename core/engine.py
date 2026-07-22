from typing import Any

from core.dto import (
    GenerationRequest,
    GenerationResult,
)
from core.models import (
    ModelAssetResolver,
    ModelDefinition,
    ModelManager,
    ResolvedModelSource,
)
from core.registry import GeneratorRegistry
from generators.base import BaseGenerator
from services.output_service import save_generation
from services.resolution_service import get_resolution


class GenerationEngine:
    """
    Central engine responsible for executing image generations.
    """

    def __init__(
        self,
        registry: GeneratorRegistry,
        model_manager: ModelManager,
        model_asset_resolver: ModelAssetResolver,
    ) -> None:
        self._registry = registry
        self._model_manager = model_manager
        self._model_asset_resolver = model_asset_resolver

        self._generator_cache: dict[
            str,
            BaseGenerator,
        ] = {}

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Validate and execute one generation request.
        """
        request.validate()

        model = self._resolve_model(
            request.model_id
        )

        model_source = self._resolve_model_source(
            model
        )
        
        resolution = self._resolve_resolution(
            request.resolution_id
        )

        request.width = int(
            resolution["width"]
        )

        request.height = int(
            resolution["height"]
        )

        generator = self._get_generator(
            model=model,
            model_source=model_source,
        )

        result = generator.generate(request)

        image_path, metadata_path = save_generation(
            request=request,
            result=result,
            model=model,
        )

        result.image_path = image_path
        result.metadata_path = metadata_path

        return result

    def clear_generator_cache(
        self,
        model_id: str | None = None,
    ) -> None:
        """
        Clear one cached generator or the complete cache.
        """
        if model_id is None:
            self._generator_cache.clear()
            return

        self._generator_cache.pop(
            model_id,
            None,
        )

    def get_cached_model_ids(
        self,
    ) -> tuple[str, ...]:
        """
        Return model identifiers stored in the generator cache.
        """
        return tuple(
            sorted(self._generator_cache)
        )

    def get_registered_backends(
        self,
    ) -> tuple[str, ...]:
        """
        Return generator backends available to this engine.
        """
        return self._registry.get_registered_backends()

    def _resolve_model(
        self,
        model_id: str,
    ) -> ModelDefinition:
        model = self._model_manager.require(
            model_id
        )

        if not model.enabled:
            raise ValueError(
                f"Model is disabled: {model_id}"
            )

        return model

    def _resolve_model_source(
        self,
        model: ModelDefinition,
    ) -> ResolvedModelSource | None:
        """
        Resolve and validate the runtime source of a model.

        Diagnostic generators may not require a source.
        """
        if model.backend == "pillow":
            return None

        validation_errors = (
            self._model_asset_resolver.validate(
                model
            )
        )

        if validation_errors:
            raise ValueError(
                f"Invalid model source for {model.id}: "
                + "; ".join(validation_errors)
            )

        return self._model_asset_resolver.resolve_source(
            model
        )

    def _resolve_resolution(
        self,
        resolution_id: str,
    ) -> dict[str, Any]:
        resolution = get_resolution(
            resolution_id
        )

        if resolution is None:
            raise ValueError(
                "Resolution was not found: "
                f"{resolution_id}"
            )

        if not resolution.get(
            "enabled",
            True,
        ):
            raise ValueError(
                "Resolution is disabled: "
                f"{resolution_id}"
            )

        return resolution

    def _get_generator(
        self,
        model: ModelDefinition,
        model_source: ResolvedModelSource | None,
    ) -> BaseGenerator:
        """
        Return a cached generator instance for a model.
        """
        if model.id not in self._generator_cache:
            self._generator_cache[model.id] = (
                self._registry.create(
                    model=model,
                    model_source=model_source,
                )
            )

        return self._generator_cache[
            model.id
        ]