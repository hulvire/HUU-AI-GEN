from core.pipelines import PipelineManager
from core.registry import GeneratorRegistry
from generators.diffusers_generator import (
    DiffusersGenerator,
)
from generators.pillow_generator import (
    PillowGenerator,
)
from services.lora_loader import LoRALoader


def register_generator_backends(
    registry: GeneratorRegistry,
    pipeline_manager: PipelineManager,
    lora_loader: LoRALoader,
) -> None:
    """
    Register all built-in generator backends.
    """
    registry.register(
        "diffusers",
        lambda model, model_source: DiffusersGenerator(
            model=model,
            model_source=model_source,
            pipeline_manager=pipeline_manager,
            lora_loader=lora_loader,
        ),
    )

    registry.register(
        "pillow",
        lambda model, model_source: PillowGenerator(
            model=model,
        ),
    )