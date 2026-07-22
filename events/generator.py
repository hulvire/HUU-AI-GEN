from typing import Any

import gradio as gr

from core.dto import GenerationMode
from services.generator_service import GeneratorService


def register_generator_events(
    sidebar: dict[str, Any],
    preview: dict[str, Any],
    generator_service: GeneratorService,
) -> None:
    """
    Register image generation UI events.
    """

    def update_generation_mode(
        mode: str,
    ) -> tuple[gr.update, gr.update]:
        is_image_to_image = (
            mode
            == GenerationMode.IMAGE_TO_IMAGE.value
        )

        return (
            gr.update(
                visible=is_image_to_image,
            ),
            gr.update(
                visible=is_image_to_image,
            ),
        )

    sidebar["mode"].change(
        fn=update_generation_mode,
        inputs=[
            sidebar["mode"],
        ],
        outputs=[
            sidebar["input_image"],
            sidebar["strength"],
        ],
    )

    generation_event = sidebar["generate"].click(
        fn=generator_service.generate_image,
        inputs=[
            sidebar["preset"],
            sidebar["scheduler"],
            sidebar["mode"],
            sidebar["input_image"],
            sidebar["strength"],
            sidebar["prompt"],
            sidebar["negative"],
            sidebar["model"],
            sidebar["resolution"],
            sidebar["seed"],
            sidebar["steps"],
            sidebar["guidance_scale"],
        ],
        outputs=[
            preview["image"],
            preview["status"],
        ],
    )
    