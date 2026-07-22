import traceback

from PIL import Image

from core.engine import GenerationEngine
from core.requests import GenerationRequestFactory


class GeneratorService:
    """
    Adapter between the Gradio interface
    and GenerationEngine.
    """

    def __init__(
        self,
        engine: GenerationEngine,
        request_factory: GenerationRequestFactory,
    ) -> None:
        self._engine = engine
        self._request_factory = request_factory

    def generate_image(
        self,
        preset_id: str,
        scheduler_id: str,
        mode: str,
        input_image: Image.Image | None,
        strength: int | float,
        prompt: str,
        negative_prompt: str,
        model_id: str,
        resolution_id: str,
        seed: int | float | None,
        steps: int | float,
        guidance_scale: int | float,
    ) -> tuple[Image.Image | None, str]:
        """
        Convert UI values into a generation request
        and execute it.
        """
        try:
            request = self._request_factory.create(
                preset_id=preset_id,
                scheduler_id=scheduler_id,
                mode=mode,
                input_image=input_image,
                strength=strength,
                prompt=prompt,
                negative_prompt=negative_prompt,
                model_id=model_id,
                resolution_id=resolution_id,
                seed=seed,
                steps=steps,
                guidance_scale=guidance_scale,
            )

            result = self._engine.generate(
                request
            )

            status = (
                "Generation completed successfully.\n\n"
                f"Mode: {request.mode.value}\n"
                f"Preset: "
                f"{request.preset_name or 'none'}\n"
                f"Scheduler: "
                f"{request.scheduler_name or 'none'}\n"
                f"Model: {result.model_name}\n"
                f"Resolution: "
                f"{result.width} × {result.height}\n"
                f"Seed: {result.seed}\n"
                f"Steps: {result.steps}\n"
                f"CFG Scale: "
                f"{result.guidance_scale}\n"
                f"Time: "
                f"{result.duration_seconds} seconds\n\n"
                f"Image: {result.image_path}\n"
                f"Metadata: {result.metadata_path}"
            )

            return result.image, status

        except Exception as exception:
            traceback.print_exc()

            status = (
                "Generation failed.\n\n"
                f"{type(exception).__name__}: "
                f"{exception}"
            )

            return None, status