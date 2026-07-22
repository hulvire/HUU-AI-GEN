from dataclasses import dataclass, field

from PIL import Image

from core.dto.generation_mode import GenerationMode
from core.loras import LoRASelection

@dataclass(slots=True)
class GenerationRequest:
    """
    Contains all inputs required for one image generation.
    """

    prompt: str
    negative_prompt: str

    model_id: str
    resolution_id: str

    seed: int | None
    steps: int
    guidance_scale: float

    preset_id: str | None = None
    preset_name: str | None = None

    scheduler_id: str | None = None
    scheduler_name: str | None = None

    loras: LoRASelection = field(
        default_factory=LoRASelection.empty,
    )

    mode: GenerationMode = (
        GenerationMode.TEXT_TO_IMAGE
    )

    input_image: Image.Image | None = None
    strength: float = 0.75

    # Resolved by the engine from the
    # resolution configuration.
    width: int | None = None
    height: int | None = None

    def validate(self) -> None:
        """
        Validate values that must be available
        before generation.
        """
        self.prompt = self.prompt.strip()
        self.negative_prompt = (
            self.negative_prompt.strip()
        )

        if not self.prompt:
            raise ValueError(
                "Prompt cannot be empty."
            )

        if not self.model_id:
            raise ValueError(
                "Model ID cannot be empty."
            )

        if not self.resolution_id:
            raise ValueError(
                "Resolution ID cannot be empty."
            )

        self.loras.validate()

        if self.steps < 1:
            raise ValueError(
                "Steps must be greater than zero."
            )

        if self.guidance_scale < 0:
            raise ValueError(
                "Guidance scale cannot be negative."
            )

        if not 0.0 < self.strength <= 1.0:
            raise ValueError(
                "Image-to-image strength must be "
                "greater than 0 and at most 1."
            )

        if (
            self.mode
            == GenerationMode.IMAGE_TO_IMAGE
            and self.input_image is None
        ):
            raise ValueError(
                "Image-to-image mode requires "
                "an input image."
            )