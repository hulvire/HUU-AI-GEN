from core.assets import (
    AssetManager,
    AssetType,
)
from core.paths import (
    CHECKPOINTS,
    CONTROLNET,
    EMBEDDINGS,
    LORAS,
    UPSCALERS,
    VAE,
)


def create_asset_manager() -> AssetManager:
    """
    Create and initialize the application asset manager.
    """
    manager = AssetManager(
        directories={
            AssetType.CHECKPOINT: CHECKPOINTS,
            AssetType.LORA: LORAS,
            AssetType.VAE: VAE,
            AssetType.EMBEDDING: EMBEDDINGS,
            AssetType.CONTROLNET: CONTROLNET,
            AssetType.UPSCALER: UPSCALERS,
        }
    )

    manager.scan()

    return manager