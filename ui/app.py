import gradio as gr

from core.application import Application
from core.models import ModelManager
from core.presets import PresetManager
from core.schedulers import SchedulerManager
from events.register import register_events
from services.generator_service import GeneratorService
from ui.header import create_header
from ui.preview import create_preview
from ui.sidebar import create_sidebar
from core.history import HistoryManager
from ui.history import create_history


def create_app(
    application: Application,
    generator_service: GeneratorService,
    model_manager: ModelManager,
    preset_manager: PresetManager,
    scheduler_manager: SchedulerManager,
    history_manager: HistoryManager,
) -> gr.Blocks:
    """
    Build the HUU-AI-GEN Gradio interface.
    """
    with gr.Blocks(
        title=application.get_display_title(),
    ) as demo:
        create_header(
            application=application,
        )

        with gr.Row(
            elem_id="generator-workspace",
        ):
            sidebar = create_sidebar(
                model_manager=model_manager,
                preset_manager=preset_manager,
                scheduler_manager=scheduler_manager,
            )

            with gr.Column(
                scale=7,
                elem_id="output-workspace",
            ):
                preview = create_preview()

                history = create_history(
                    history_manager=history_manager,
                )

        register_events(
            sidebar=sidebar,
            preview=preview,
            history=history,
            generator_service=generator_service,
            preset_manager=preset_manager,
            model_manager=model_manager,
            history_manager=history_manager,
        )

    return demo