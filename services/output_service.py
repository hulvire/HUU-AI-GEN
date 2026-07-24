import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.application import application
from core.dto import (
    GenerationMode,
    GenerationRequest,
    GenerationResult,
)
from core.models import ModelDefinition
from core.paths import OUTPUTS


def create_output_directory() -> Path:
    """
    Create a directory for the current date.
    """
    directory = OUTPUTS / datetime.now().strftime(
        "%Y-%m-%d"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def create_output_name() -> str:
    """
    Create a unique output filename.
    """
    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    unique_id = uuid4().hex[:8]

    return f"{timestamp}-{unique_id}"


def save_input_image(
    request: GenerationRequest,
    output_directory: Path,
    output_name: str,
) -> Path | None:
    """
    Save a copy of the image-to-image input image.

    Text-to-image requests and requests without an input image
    return None.
    """
    if (
        request.mode
        != GenerationMode.IMAGE_TO_IMAGE
        or request.input_image is None
    ):
        return None

    input_image_path = output_directory / (
        f"{output_name}-input.png"
    )

    input_image = request.input_image.convert("RGB")

    input_image.save(
        input_image_path,
        format="PNG",
        optimize=True,
    )

    return input_image_path


def create_metadata(
    request: GenerationRequest,
    result: GenerationResult,
    model: ModelDefinition,
    input_image_path: Path | None = None,
) -> dict[str, Any]:
    """
    Create JSON-serializable generation metadata.

    The PIL input image object is never inserted directly
    into the metadata.
    """
    is_image_to_image = (
        request.mode
        == GenerationMode.IMAGE_TO_IMAGE
    )

    metadata: dict[str, Any] = {
        "application": {
            "name": application.name,
            "version": application.version,
            "environment": application.environment,
        },
        "prompt": request.prompt,
        "negative_prompt": request.negative_prompt,
        "seed": result.seed,
        "model": {
            "id": model.id,
            "name": model.name,
            "repository_id": model.repository_id,
            "backend": model.backend,
        },
        "generation": {
            "mode": request.mode.value,
            "preset": {
                "id": request.preset_id,
                "name": request.preset_name,
            },
            "scheduler": {
                "id": request.scheduler_id,
                "name": request.scheduler_name,
            },
            "loras": [
                {
                    "id": runtime.id,
                    "name": runtime.name,
                    "scale": runtime.scale,
                    "adapter_name": runtime.adapter_name,
                    "repository_id": runtime.repository_id,
                    "weight_name": runtime.weight_name,
                    "file_path": runtime.file_path,
                    "trigger_words": list(
                        runtime.trigger_words
                    ),
                }
                for runtime in request.loras.active()
            ],
            "width": result.width,
            "height": result.height,
            "steps": result.steps,
            "guidance_scale": result.guidance_scale,
            "duration_seconds": result.duration_seconds,
        },
        "input": {
            "used": request.input_image is not None,
            "image": (
                str(input_image_path)
                if input_image_path is not None
                else None
            ),
            "strength": (
                request.strength
                if is_image_to_image
                else None
            ),
        },
        "output": {
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        },
    }

    return metadata


def save_generation(
    request: GenerationRequest,
    result: GenerationResult,
    model: ModelDefinition,
) -> tuple[Path, Path]:
    """
    Save the generated image, optional input image
    and JSON metadata.
    """
    output_directory = create_output_directory()
    output_name = create_output_name()

    image_path = output_directory / (
        f"{output_name}.png"
    )

    metadata_path = output_directory / (
        f"{output_name}.json"
    )

    result.image.save(
        image_path,
        format="PNG",
        optimize=True,
    )

    input_image_path = save_input_image(
        request=request,
        output_directory=output_directory,
        output_name=output_name,
    )

    metadata = create_metadata(
        request=request,
        result=result,
        model=model,
        input_image_path=input_image_path,
    )

    metadata["output"]["image"] = str(
        image_path
    )

    metadata["output"]["metadata"] = str(
        metadata_path
    )

    with metadata_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=4,
        )

    return image_path, metadata_path