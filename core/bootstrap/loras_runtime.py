from services.lora_loader import LoRALoader


def create_lora_loader() -> LoRALoader:
    """
    Create the Diffusers LoRA runtime loader.
    """
    return LoRALoader()