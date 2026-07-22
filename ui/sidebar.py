from typing import Any

import gradio as gr

from core.dto import GenerationMode
from core.models import ModelManager
from core.presets import PresetManager
from core.schedulers import SchedulerManager
from services.resolution_service import (
    get_default_resolution_id,
    get_resolution_choices,
)
from ui.components.collapsible_section import (
    collapsible_section,
)


def create_sidebar(
    model_manager: ModelManager,
    preset_manager: PresetManager,
    scheduler_manager: SchedulerManager,
) -> dict[str, Any]:
    """
    Create the generator sidebar controls.
    """

    # -------------------------------------------------
    # Available choices
    # -------------------------------------------------

    model_choices = model_manager.get_choices(
        enabled_only=True,
    )

    preset_choices = preset_manager.get_choices(
        enabled_only=True,
    )

    scheduler_choices = (
        scheduler_manager.get_choices(
            enabled_only=True,
        )
    )

    resolution_choices = (
        get_resolution_choices()
    )

    mode_choices = [
        (
            "Text to Image",
            GenerationMode.TEXT_TO_IMAGE.value,
        ),
        (
            "Image to Image",
            GenerationMode.IMAGE_TO_IMAGE.value,
        ),
    ]

    # -------------------------------------------------
    # Default values
    # -------------------------------------------------

    default_model = (
        model_manager.get_default_id()
    )

    default_preset = (
        preset_manager.get_default_id()
    )

    default_scheduler = (
        scheduler_manager.get_default_id()
    )

    default_resolution = (
        get_default_resolution_id()
    )

    default_mode = (
        GenerationMode.TEXT_TO_IMAGE.value
    )

    # -------------------------------------------------
    # Sidebar interface
    # -------------------------------------------------

    with gr.Column(
        elem_id="generator-sidebar",
        elem_classes=["huu-panel"],
        scale=3,
        min_width=360,
    ):
        gr.HTML(
            """
            <div class="panel-heading">
                <span class="panel-heading__eyebrow">
                    Generator
                </span>

                <h2 class="panel-heading__title">
                    Generation settings
                </h2>
            </div>
            """
        )

        # ---------------------------------------------
        # Prompt
        # ---------------------------------------------

        with collapsible_section(
            section_id="prompt-settings",
            title="Prompt",
            open_by_default=True,
        ):
            preset = gr.Dropdown(
                label="Preset",
                choices=preset_choices,
                value=default_preset,
                interactive=True,
                info=(
                    "Select a predefined generation "
                    "configuration."
                ),
            )

            mode = gr.Radio(
                label="Generation mode",
                choices=mode_choices,
                value=default_mode,
                interactive=True,
            )

            input_image = gr.Image(
                label="Input image",
                type="pil",
                visible=False,
            )

            strength = gr.Slider(
                label="Image strength",
                minimum=0.05,
                maximum=1.0,
                value=0.75,
                step=0.05,
                info=(
                    "Lower values preserve more "
                    "of the original image."
                ),
                visible=False,
            )

            prompt = gr.Textbox(
                label="Prompt",
                placeholder=(
                    "Describe the image you want "
                    "to generate..."
                ),
                lines=6,
            )

            negative_prompt = gr.Textbox(
                label="Negative prompt",
                placeholder=(
                    "Describe what should "
                    "not appear..."
                ),
                lines=3,
            )

        # ---------------------------------------------
        # Model and output
        # ---------------------------------------------

        with collapsible_section(
            section_id="model-settings",
            title="Model and output",
            open_by_default=True,
        ):
            model = gr.Dropdown(
                label="Model",
                choices=model_choices,
                value=default_model,
                interactive=True,
            )

            resolution = gr.Dropdown(
                label="Resolution",
                choices=resolution_choices,
                value=default_resolution,
                interactive=True,
            )

        # ---------------------------------------------
        # Advanced settings
        # ---------------------------------------------

        with collapsible_section(
            section_id="advanced-settings",
            title="Advanced settings",
            open_by_default=False,
        ):
            scheduler = gr.Dropdown(
                label="Scheduler",
                choices=scheduler_choices,
                value=default_scheduler,
                interactive=True,
                info=(
                    "Select the diffusion sampling "
                    "scheduler."
                ),
            )

            seed = gr.Number(
                label="Seed",
                value=-1,
                precision=0,
                info="Use -1 for a random seed.",
            )

            steps = gr.Slider(
                label="Steps",
                minimum=1,
                maximum=100,
                value=20,
                step=1,
            )

            guidance_scale = gr.Slider(
                label="CFG Scale",
                minimum=0.0,
                maximum=30.0,
                value=7.5,
                step=0.5,
            )

            lora = gr.Dropdown(
                label="LoRA",
                choices=[
                    ("None", ""),
                    ("LCM LoRA SDXL", "lcm-lora-sdxl"),
                ],
                value="",
            )

            lora_scale = gr.Slider(
                label="LoRA Scale",
                minimum=0.0,
                maximum=1.5,
                value=1.0,
                step=0.05,
            )

        # ---------------------------------------------
        # Primary action
        # ---------------------------------------------

        generate = gr.Button(
            value="Generate image",
            variant="primary",
            elem_id="generate-button",
        )

    return {
        "preset": preset,
        "scheduler": scheduler,
        "mode": mode,
        "input_image": input_image,
        "strength": strength,
        "prompt": prompt,
        "negative": negative_prompt,
        "model": model,
        "resolution": resolution,
        "seed": seed,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "lora": lora,
        "lora_scale": lora_scale,
        "generate": generate,
    }