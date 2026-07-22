from core.paths import PRESETS
from core.presets import PresetManager


def create_preset_manager() -> PresetManager:
    """
    Create, scan and return the runtime preset manager.
    """
    preset_manager = PresetManager(
        presets_directory=PRESETS,
    )

    preset_manager.scan()

    return preset_manager