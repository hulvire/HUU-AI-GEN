from PIL import Image

from core.dto import (
    GenerationMode,
    GenerationRequest,
)
from core.presets import PresetManager
from core.schedulers import SchedulerManager
from core.loras import LoRAManager
from core.models import ModelManager

class GenerationRequestFactory:
    """
    Creates validated generation requests from UI values.
    """

    def __init__(
        self,
        preset_manager: PresetManager,
        scheduler_manager: SchedulerManager,
        lora_manager: LoRAManager,
        model_manager: ModelManager,
    ) -> None:
        self._preset_manager = preset_manager
        self._scheduler_manager = scheduler_manager
        self._lora_manager = lora_manager
        self._model_manager = model_manager

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
        steps: int | float | None,
        guidance_scale: int | float | None,
        lora_selections: dict[str, float] | None = None,
    ) -> GenerationRequest:
        """
        Create a generation request and apply
        the selected preset to textual prompts.
        """
        preset = self._preset_manager.require(
            preset_id
        )

        model = self._model_manager.require(
            model_id
        )

        generation_defaults = (
            model.generation_defaults
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

        lora_selection = (
            self._lora_manager.create_selection(
                lora_selections
            )
        )

        resolved_steps = (
            steps
            if steps is not None
            else generation_defaults.get(
                "steps",
                20,
            )
        )

        resolved_guidance_scale = (
            guidance_scale
            if guidance_scale is not None
            else generation_defaults.get(
                "guidance_scale",
                7.0,
            )
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
            loras=lora_selection,
            seed=self._normalize_seed(seed),
            steps=self._normalize_steps(
                resolved_steps
            ),
            guidance_scale=(
                self._normalize_guidance_scale(
                    resolved_guidance_scale
                )
            ),
            mode=generation_mode,
            input_image=input_image,
            strength=self._normalize_strength(
                strength
            ),
        )


        print("=" * 70)
        print("GENERATION REQUEST")
        print("Model:", model.id)
        print("Repository:", model.repository_id)
        print("Preset:", preset.id)
        print("Scheduler:", scheduler.id)
        print("Steps:", request.steps)
        print("Guidance scale:", request.guidance_scale)
        print("Mode:", request.mode.value)
        print("Prompt:", request.prompt)
        print("Negative prompt:", request.negative_prompt)
        print("LoRAs:", request.loras)
        print("=" * 70)

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