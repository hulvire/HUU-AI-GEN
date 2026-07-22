from core.loras import LoRAManager
from core.paths import LORAS


def create_lora_manager() -> LoRAManager:
    """
    Create and initialize the runtime LoRA catalog.
    """
    manager = LoRAManager(
        loras_directory=LORAS,
    )

    manager.scan()

    return manager