import secrets
import time
from typing import Any

import torch
from PIL import Image, ImageOps

from core.dto import (
    GenerationMode,
    GenerationRequest,
    GenerationResult,
)
from core.models import ResolvedModelSource
from core.pipelines import PipelineManager
from generators.base import BaseGenerator
from services.lora_loader import LoRALoader

class DiffusersGenerator(BaseGenerator):
    """
    Generates images using a pipeline managed
    by PipelineManager.
    """

    def __init__(
        self,
        model: dict[str, Any],
        model_source: ResolvedModelSource | None,
        pipeline_manager: PipelineManager,
        lora_loader: LoRALoader,
    ) -> None:
        if model_source is None:
            raise ValueError(
                "Diffusers generator requires "
                "a resolved model source."
            )

        self.model = model
        self._model_source = model_source
        self._pipeline_manager = pipeline_manager
        self._lora_loader = lora_loader

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Generate one image from the supplied request.
        """
        if (
            request.width is None
            or request.height is None
        ):
            raise ValueError(
                "Generation resolution has not been resolved."
            )

        pipeline = self._pipeline_manager.get_pipeline(
            model=self.model,
            model_source=self._model_source,
            mode=request.mode,
        )

        applied_scheduler_id = (
            self._pipeline_manager.apply_scheduler(
                pipeline=pipeline,
                scheduler_id=request.scheduler_id,
            )
        )

        if (
            request.scheduler_id is not None
            and applied_scheduler_id
            != request.scheduler_id
        ):
            raise RuntimeError(
                "Applied scheduler does not match "
                "the requested scheduler."
            )
        
        self._lora_loader.apply(
            pipeline=pipeline,
            selection=request.loras,
        )

        used_seed = (
            int(request.seed)
            if request.seed is not None
            else secrets.randbelow(
                2_147_483_647
            )
        )

        random_generator = torch.Generator(
            device="cpu"
        ).manual_seed(
            used_seed
        )

        started_at = time.perf_counter()

        common_arguments = {
            "prompt": request.prompt,
            "negative_prompt": (
                request.negative_prompt
                or None
            ),
            "num_inference_steps": request.steps,
            "guidance_scale": request.guidance_scale,
            "generator": random_generator,
        }

        if (
            request.mode
            == GenerationMode.TEXT_TO_IMAGE
        ):
            pipeline_result = pipeline(
                **common_arguments,
                width=request.width,
                height=request.height,
            )

        elif (
            request.mode
            == GenerationMode.IMAGE_TO_IMAGE
        ):
            if request.input_image is None:
                raise ValueError(
                    "Image-to-image mode requires "
                    "an input image."
                )

            prepared_image = ImageOps.fit(
                request.input_image.convert("RGB"),
                (
                    request.width,
                    request.height,
                ),
                method=Image.Resampling.LANCZOS,
            )

            pipeline_result = pipeline(
                **common_arguments,
                image=prepared_image,
                strength=request.strength,
            )

        else:
            raise ValueError(
                "Unsupported generation mode: "
                f"{request.mode}"
            )

        duration_seconds = round(
            time.perf_counter()
            - started_at,
            2,
        )

        return GenerationResult(
            image=pipeline_result.images[0],
            seed=used_seed,
            duration_seconds=duration_seconds,
            model_id=self.model.get(
                "id",
                "unknown-model",
            ),
            model_name=self.model.get(
                "name",
                "Unknown model",
            ),
            width=request.width,
            height=request.height,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
        )