from enum import StrEnum


class AssetType(StrEnum):
    """
    Supported AI asset categories.
    """

    CHECKPOINT = "checkpoint"
    LORA = "lora"
    VAE = "vae"
    EMBEDDING = "embedding"
    CONTROLNET = "controlnet"
    UPSCALER = "upscaler"