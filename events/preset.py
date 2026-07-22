import gradio as gr

from core.presets import PresetManager


def apply_preset(
    preset_id: str,
    preset_manager: PresetManager,
) -> tuple[
    gr.update,
    gr.update,
    gr.update,
    gr.update,
    gr.update,
]:
    """
    Return UI updates for the selected preset.
    """
    preset = preset_manager.require(preset_id)

    return (
        gr.update(
            value=preset.scheduler,
        ),
        gr.update(
            value=preset.steps,
        ),
        gr.update(
            value=preset.guidance_scale,
        ),
        gr.update(
            value=preset.strength,
        ),
        gr.update(
            value=preset.negative_prompt,
        ),
    )


def register_preset_events(
    sidebar: dict[str, object],
    preset_manager: PresetManager,
) -> None:
    """
    Register preset-related UI events.
    """
    sidebar["preset"].change(
        fn=lambda preset_id: apply_preset(
            preset_id=preset_id,
            preset_manager=preset_manager,
        ),
        inputs=[
            sidebar["preset"],
        ],
        outputs=[
            sidebar["scheduler"],
            sidebar["steps"],
            sidebar["guidance_scale"],
            sidebar["strength"],
            sidebar["negative"],
        ],
    )