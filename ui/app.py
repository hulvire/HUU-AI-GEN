import gradio as gr

from core.application import Application
from core.models import ModelManager
from core.presets import PresetManager
from core.schedulers import SchedulerManager
from events.register import register_events
from services.generator_service import GeneratorService
from ui.preview import create_preview
from ui.sidebar import create_sidebar


def create_app(
    application: Application,
    generator_service: GeneratorService,
    model_manager: ModelManager,
    preset_manager: PresetManager,
    scheduler_manager: SchedulerManager,
) -> gr.Blocks:
    """
    Build the HUU-AI-GEN Gradio interface.
    """
    with gr.Blocks(
        title=application.get_display_title(),
    ) as demo:
        gr.Markdown(
            f"""
# {application.name}

{application.description}

**Version:** {application.get_display_version()}  
**Release date:** {application.release_date}
""",
    elem_classes=["app-header"],
        )

        with gr.Row():
            sidebar = create_sidebar(
                model_manager=model_manager,
                preset_manager=preset_manager,
                scheduler_manager=scheduler_manager,
            )

            preview = create_preview()

        register_events(
            sidebar=sidebar,
            preview=preview,
            generator_service=generator_service,
            preset_manager=preset_manager,
        )

    return demo