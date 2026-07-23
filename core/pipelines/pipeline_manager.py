from typing import Any

import torch
from diffusers import (
    StableDiffusionImg2ImgPipeline,
    StableDiffusionPipeline,
    StableDiffusionXLImg2ImgPipeline,
    StableDiffusionXLPipeline,
)

from core.dto import GenerationMode
from core.models import ResolvedModelSource
from core.pipelines.pipeline_cache import PipelineCache
from core.schedulers import (
    SchedulerFactory,
    SchedulerManager,
)

StableDiffusionRuntimePipeline = (
    StableDiffusionPipeline
    | StableDiffusionImg2ImgPipeline
    | StableDiffusionXLPipeline
    | StableDiffusionXLImg2ImgPipeline
)

class PipelineManager:
    """
    Loads, caches and releases Diffusers pipelines.
    """

    def __init__(
        self,
        cache: PipelineCache | None = None,
        scheduler_manager: SchedulerManager | None = None,
        scheduler_factory: SchedulerFactory | None = None,
    ) -> None:
        self._cache = cache or PipelineCache()

        self._scheduler_manager = scheduler_manager
        self._scheduler_factory = scheduler_factory

    def get_pipeline(
        self,
        model: dict[str, Any],
        model_source: ResolvedModelSource,
        mode: GenerationMode,
    ) -> StableDiffusionRuntimePipeline:
        """
        Return a cached pipeline or load a new one.
        """
        model_id = self._get_model_id(model)

        cache_key = self._get_cache_key(
            model_id=model_id,
            mode=mode,
        )

        if self._cache.has(cache_key):
            print(
                "[PipelineManager] "
                f"Using cached pipeline: {cache_key}"
            )

            return self._cache.get(cache_key)

        pipeline = self._load_pipeline(
            model=model,
            model_source=model_source,
            mode=mode,
        )

        self._cache.add(
            key=cache_key,
            pipeline=pipeline,
        )

        return pipeline

    def apply_scheduler(
        self,
        pipeline: StableDiffusionRuntimePipeline,
        scheduler_id: str | None,
    ) -> str:
        """
        Apply a scheduler to an existing pipeline.
        """
        if (
            self._scheduler_manager is None
            or self._scheduler_factory is None
        ):
            raise RuntimeError(
                "Scheduler support is not configured."
            )

        scheduler_id = (
            scheduler_id
            or self._scheduler_manager.get_default_id()
        )

        if scheduler_id is None:
            raise RuntimeError(
                "No scheduler is available."
            )

        definition = (
            self._scheduler_manager.require(
                scheduler_id
            )
        )

        pipeline.scheduler = (
            self._scheduler_factory.create(
                definition=definition,
                source_scheduler=pipeline.scheduler,
            )
        )

        print(
            "[PipelineManager] "
            f"Scheduler applied: {definition.name}"
        )

        return definition.id

    def has_pipeline(
        self,
        model_id: str,
        mode: GenerationMode,
    ) -> bool:
        """
        Check whether a pipeline mode is cached.
        """
        cache_key = self._get_cache_key(
            model_id=model_id,
            mode=mode,
        )

        return self._cache.has(cache_key)

    def get_cached_model_ids(
        self,
    ) -> tuple[str, ...]:
        """
        Return all pipeline cache keys.

        Example:
            stable-diffusion-15:text-to-image
            stable-diffusion-15:image-to-image
        """
        return self._cache.get_model_ids()

    def get_cached_pipeline_count(
        self,
    ) -> int:
        """
        Return the number of cached pipelines.
        """
        return self._cache.count()

    def unload(
        self,
        model_id: str,
        mode: GenerationMode,
    ) -> bool:
        """
        Remove one pipeline mode from the cache.
        """
        cache_key = self._get_cache_key(
            model_id=model_id,
            mode=mode,
        )

        pipeline = self._cache.remove(cache_key)

        if pipeline is None:
            return False

        del pipeline

        self._clear_cuda_cache()

        print(
            "[PipelineManager] "
            f"Pipeline unloaded: {cache_key}"
        )

        return True

    def unload_model(
        self,
        model_id: str,
    ) -> int:
        """
        Remove all cached pipeline modes for one model.

        Returns the number of unloaded pipelines.
        """
        matching_keys = tuple(
            cache_key
            for cache_key in self._cache.get_model_ids()
            if cache_key.startswith(
                f"{model_id}:"
            )
        )

        unloaded_count = 0

        for cache_key in matching_keys:
            pipeline = self._cache.remove(
                cache_key
            )

            if pipeline is None:
                continue

            del pipeline
            unloaded_count += 1

            print(
                "[PipelineManager] "
                f"Pipeline unloaded: {cache_key}"
            )

        if unloaded_count > 0:
            self._clear_cuda_cache()

        return unloaded_count

    def unload_all(self) -> None:
        """
        Remove all pipelines from the cache.
        """
        pipelines = self._cache.clear()

        for pipeline in pipelines:
            del pipeline

        self._clear_cuda_cache()

        print(
            "[PipelineManager] "
            "All pipelines unloaded."
        )

    def _load_pipeline(
        self,
        model: dict[str, Any],
        model_source: ResolvedModelSource,
        mode: GenerationMode,
    ) -> StableDiffusionRuntimePipeline:
        """
        Load a pipeline from a resolved model source.
        """
        model_id = self._get_model_id(model)

        model_name = model.get(
            "name",
            model_id,
        )

        repository_id = model_source.repository_id
        model_path = model_source.local_path

        runtime = model.runtime

        variant = runtime.get("variant")

        pipeline_class = self._get_pipeline_class(
            model=model,
            mode=mode,
        )

        print("=" * 60)
        print("LOADING PIPELINE")
        print("MODEL ID:", model_id)
        print("MODEL NAME:", model_name)
        print("GENERATION MODE:", mode.value)
        print(
            "PIPELINE CLASS:",
            pipeline_class.__name__,
        )
        print("SOURCE TYPE:", model_source.type)
        print("REPOSITORY:", repository_id)
        print("MODEL PATH:", model_path)
        print("RUNTIME:", runtime)
        print("=" * 60)

        if model_source.type == "repository":
            if not repository_id:
                raise ValueError(
                    "Resolved repository source does not "
                    "contain a repository ID."
                )

            load_kwargs: dict[str, Any] = {
                "torch_dtype": torch.float16,
                "use_safetensors": True,
            }

            if variant:
                load_kwargs["variant"] = variant

            if model.get("family") == "sd15":
                load_kwargs["safety_checker"] = None
                load_kwargs["requires_safety_checker"] = False

            pipeline = pipeline_class.from_pretrained(
                repository_id,
                **load_kwargs,
            )

        elif model_source.type in {
            "path",
            "asset",
        }:
            if model_path is None:
                raise ValueError(
                    "Resolved local source does not "
                    "contain a model path."
                )

            pipeline = pipeline_class.from_single_file(
                str(model_path),
                torch_dtype=torch.float16,
                use_safetensors=True,
                safety_checker=None,
                requires_safety_checker=False,
            )

        else:
            raise ValueError(
                "Unsupported resolved model source type: "
                f"{model_source.type}"
            )

        self._validate_pipeline(
            model_id=model_id,
            pipeline=pipeline,
        )

        self._optimize_pipeline(pipeline)

        print(
            "[PipelineManager] "
            f"Pipeline loaded: {model_id}:{mode.value}"
        )

        return pipeline

    def _get_pipeline_class(
        self,
        model: dict[str, Any],
        mode: GenerationMode,
    ) -> type[StableDiffusionRuntimePipeline]:
        """
        Resolve the Diffusers pipeline class
        for a model family and generation mode.
        """
        family = model.get("family")

        if family == "sd15":
            if mode == GenerationMode.TEXT_TO_IMAGE:
                return StableDiffusionPipeline

            if mode == GenerationMode.IMAGE_TO_IMAGE:
                return StableDiffusionImg2ImgPipeline

        elif family == "sdxl":
            if mode == GenerationMode.TEXT_TO_IMAGE:
                return StableDiffusionXLPipeline

            if mode == GenerationMode.IMAGE_TO_IMAGE:
                return StableDiffusionXLImg2ImgPipeline

        else:
            raise ValueError(
                "Unsupported or missing model family "
                f"for model '{self._get_model_id(model)}': "
                f"{family!r}"
            )

        raise ValueError(
            "Unsupported generation mode "
            f"'{mode.value}' for model family '{family}'."
        )

    def _get_cache_key(
        self,
        model_id: str,
        mode: GenerationMode,
    ) -> str:
        """
        Build a unique cache key for a model
        and generation mode.
        """
        return f"{model_id}:{mode.value}"

    def _validate_pipeline(
        self,
        model_id: str,
        pipeline: StableDiffusionRuntimePipeline,
    ) -> None:
        """
        Validate the loaded pipeline architecture.
        """
        addition_embed_type = (
            pipeline.unet.config.get(
                "addition_embed_type"
            )
        )

        cross_attention_dim = (
            pipeline.unet.config.get(
                "cross_attention_dim"
            )
        )

        print(
            "Pipeline:",
            type(pipeline).__name__,
        )
        print(
            "UNet addition_embed_type:",
            addition_embed_type,
        )
        print(
            "UNet cross_attention_dim:",
            cross_attention_dim,
        )

        if model_id != "stable-diffusion-15":
            return

        if addition_embed_type is not None:
            raise RuntimeError(
                "Loaded model is not Stable Diffusion 1.5. "
                f"addition_embed_type="
                f"{addition_embed_type!r}"
            )

        if cross_attention_dim != 768:
            raise RuntimeError(
                "Loaded model is not Stable Diffusion 1.5. "
                f"cross_attention_dim="
                f"{cross_attention_dim!r}; "
                "expected 768."
            )

    def _optimize_pipeline(
        self,
        pipeline: StableDiffusionRuntimePipeline,
    ) -> None:
        """
        Apply low-VRAM optimizations.
        """
        pipeline.enable_attention_slicing()

        if getattr(
            pipeline,
            "vae",
            None,
        ) is not None:
            pipeline.vae.enable_slicing()

        pipeline.enable_model_cpu_offload()

    def _get_model_id(
        self,
        model: dict[str, Any],
    ) -> str:
        """
        Return and validate the model identifier.
        """
        model_id = model.get("id")

        if not model_id:
            raise ValueError(
                "Model configuration does not "
                "contain an ID."
            )

        return str(model_id)

    def _clear_cuda_cache(self) -> None:
        """
        Release unused CUDA memory when available.
        """
        if torch.cuda.is_available():
            torch.cuda.empty_cache()