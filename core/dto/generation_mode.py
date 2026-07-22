from enum import StrEnum


class GenerationMode(StrEnum):
    """
    Supported image generation modes.
    """

    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_TO_IMAGE = "image-to-image"