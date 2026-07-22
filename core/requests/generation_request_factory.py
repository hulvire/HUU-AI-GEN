from PIL import Image

from core.dto import (
    GenerationMode,
    GenerationRequest,
)
from core.presets import PresetManager
from core.schedulers import SchedulerManager

class GenerationRequestFactory:
    """
    Creates validated generation requests from UI values.
    """

    def __init__(
        self,
        preset_manager: PresetManager,
        scheduler_manager: SchedulerManager,
    ) -> None:
        self._preset_manager = preset_manager
        self._scheduler_manager = scheduler_manager

    def create(
        self,
        preset_id: str,
        scheduler_id: str | None,
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
    ) -> GenerationRequest:
        """
        Create a generation request and apply
        the selected preset to textual prompts.
        """
        preset = self._preset_manager.require(
            preset_id
        )

        generation_mode = GenerationMode(mode)


        resolved_scheduler_id = (
            scheduler_id
            or self._scheduler_manager.get_default_id()
        )

        if resolved_scheduler_id is None:
            raise RuntimeError(
                "No scheduler is available."
            )

        scheduler = self._scheduler_manager.require(
            resolved_scheduler_id
        )

        request = GenerationRequest(
            preset_id=preset.id,
            preset_name=preset.name,
            scheduler_id=scheduler.id,
            scheduler_name=scheduler.name,
            prompt=preset.build_prompt(
                prompt or "",
            ),
            negative_prompt=(
                preset.build_negative_prompt(
                    negative_prompt or "",
                )
            ),
            model_id=model_id,
            resolution_id=resolution_id,
            seed=self._normalize_seed(seed),
            steps=self._normalize_steps(steps),
            guidance_scale=(
                self._normalize_guidance_scale(
                    guidance_scale
                )
            ),
            mode=generation_mode,
            input_image=input_image,
            strength=self._normalize_strength(
                strength
            ),
        )

        request.validate()

        return request

    @staticmethod
    def _normalize_seed(
        seed: int | float | None,
    ) -> int | None:
        """
        Convert the UI seed into an optional integer.
        """
        if seed is None:
            return None

        normalized_seed = int(seed)

        if normalized_seed < 0:
            return None

        return normalized_seed

    @staticmethod
    def _normalize_steps(
        steps: int | float,
    ) -> int:
        """
        Clamp generation steps to the supported range.
        """
        return max(
            1,
            min(
                int(steps),
                100,
            ),
        )

    @staticmethod
    def _normalize_guidance_scale(
        guidance_scale: int | float,
    ) -> float:
        """
        Clamp CFG scale to the supported range.
        """
        return max(
            0.0,
            min(
                float(guidance_scale),
                30.0,
            ),
        )

    @staticmethod
    def _normalize_strength(
        strength: int | float,
    ) -> float:
        """
        Clamp image-to-image strength.
        """
        return max(
            0.05,
            min(
                float(strength),
                1.0,
            ),
        )