from typing import Any

from core.presets import PresetManager
from events.generator import register_generator_events
from events.preset import register_preset_events
from services.generator_service import GeneratorService
from events.model import register_model_events

def register_events(
    sidebar: dict[str, Any],
    preview: dict[str, Any],
    generator_service: GeneratorService,
    preset_manager: PresetManager,
    model_manager: ModelManager,
) -> None:
    """
    Register all application UI events.
    """
    register_generator_events(
        sidebar=sidebar,
        preview=preview,
        generator_service=generator_service,
    )

    register_preset_events(
        sidebar=sidebar,
        preset_manager=preset_manager,
    )

    register_model_events(
        sidebar=sidebar,
        model_manager=model_manager,
    )
