from core.application import application
from core.bootstrap.assets import (
    create_asset_manager,
)
from core.bootstrap.checkpoints import (
    create_checkpoint_manager,
)
from core.bootstrap.generators import (
    register_generator_backends,
)
from core.bootstrap.pipelines import (
    create_pipeline_manager,
)
from core.bootstrap.presets import (
    create_preset_manager,
)
from core.bootstrap.loras import (
    create_lora_manager,
)
from core.loras import LoRAManager
from core.bootstrap.schedulers import (
    create_scheduler_dependencies,
)
from core.presets import (
    PresetManager,
)
from core.schedulers import SchedulerManager
from core.context import ApplicationContext
from core.engine import GenerationEngine
from core.models import (
    ModelAssetResolver,
    ModelManager,
)
from core.paths import MODELS
from core.registry import GeneratorRegistry
from core.requests import GenerationRequestFactory
from services.generator_service import GeneratorService
from ui.app import create_app
from ui.theme import (
    create_theme,
    load_css,
    load_js,
)


def bootstrap() -> ApplicationContext:
    """
    Build and connect all runtime application dependencies.
    """
    registry = GeneratorRegistry()

    preset_manager = create_preset_manager()

    scheduler_manager, scheduler_factory = (
        create_scheduler_dependencies()
    )

    pipeline_manager = create_pipeline_manager(
        scheduler_manager=scheduler_manager,
        scheduler_factory=scheduler_factory,
    )
    _validate_preset_schedulers(
        preset_manager=preset_manager,
        scheduler_manager=scheduler_manager,
    )

    register_generator_backends(
        registry=registry,
        pipeline_manager=pipeline_manager,
    )

    model_manager = ModelManager(
        models_directory=MODELS,
    )

    model_manager.scan()

    lora_manager = create_lora_manager()

    asset_manager = create_asset_manager()

    checkpoint_manager = create_checkpoint_manager()

    model_asset_resolver = ModelAssetResolver(
        asset_manager=asset_manager,
        checkpoint_manager=checkpoint_manager,
    )

    _print_model_manager_status(
        model_manager
    )

    _print_preset_manager_status(
        preset_manager
    )

    _print_scheduler_manager_status(
        scheduler_manager
    )

    _print_lora_manager_status(
        lora_manager
    )


    engine = GenerationEngine(
        registry=registry,
        model_manager=model_manager,
        model_asset_resolver=(
            model_asset_resolver
        ),
    )

    request_factory = GenerationRequestFactory(
        preset_manager=preset_manager,
        scheduler_manager=scheduler_manager,
        lora_manager=lora_manager,
    )

    generator_service = GeneratorService(
        engine=engine,
        request_factory=request_factory,
    )

    demo = create_app(
        application=application,
        generator_service=generator_service,
        model_manager=model_manager,
        preset_manager=preset_manager,
        scheduler_manager=scheduler_manager,
    )

    return ApplicationContext(
        application=application,
        registry=registry,
        model_manager=model_manager,
        preset_manager=preset_manager,
        scheduler_manager=scheduler_manager,
        lora_manager=lora_manager,
        scheduler_factory=scheduler_factory,
        asset_manager=asset_manager,
        checkpoint_manager=checkpoint_manager,
        pipeline_manager=pipeline_manager,
        model_asset_resolver=(
            model_asset_resolver
        ),
        engine=engine,
        generator_service=generator_service,
        demo=demo,
        theme=create_theme(),
        css=load_css(),
        js=load_js(),
        head=(
            '<script src="'
            'https://cdn.jsdelivr.net/npm/'
            'gsap@3.13.0/dist/gsap.min.js'
            '"></script>'
        ),
    )


def _validate_preset_schedulers(
    preset_manager: PresetManager,
    scheduler_manager: SchedulerManager,
) -> None:
    """
    Ensure preset scheduler IDs reference
    existing enabled schedulers.
    """
    invalid_presets: list[str] = []

    for preset in preset_manager.all(
        enabled_only=True,
    ):
        if preset.scheduler is None:
            continue

        try:
            scheduler_manager.require(
                preset.scheduler
            )
        except (KeyError, ValueError):
            invalid_presets.append(
                f"{preset.id} ({preset.scheduler})"
            )

    if invalid_presets:
        invalid = ", ".join(
            invalid_presets
        )

        raise ValueError(
            "Presets reference invalid schedulers: "
            f"{invalid}"
        )


def _print_model_manager_status(
    model_manager: ModelManager,
) -> None:
    """
    Print model catalog information and errors.
    """
    print(
        "[ModelManager] "
        f"Loaded {model_manager.count()} models, "
        f"{model_manager.count(enabled_only=True)} "
        "enabled."
    )

    if not model_manager.has_errors():
        return

    for file_path, error in (
        model_manager.get_errors().items()
    ):
        print(
            "[ModelManager] "
            f"Error in {file_path}: {error}"
        )

def _print_scheduler_manager_status(
    scheduler_manager: SchedulerManager,
) -> None:
    """
    Print scheduler catalog information and errors.
    """
    print(
        "[SchedulerManager] "
        f"Loaded {scheduler_manager.count()} schedulers, "
        f"{scheduler_manager.count(enabled_only=True)} "
        "enabled."
    )

    if not scheduler_manager.has_errors():
        return

    for file_path, error in (
        scheduler_manager.get_errors().items()
    ):
        print(
            "[SchedulerManager] "
            f"Error in {file_path}: {error}"
        )


def _print_preset_manager_status(
    preset_manager,
) -> None:
    """
    Print preset catalog information and errors.
    """
    print(
        "[PresetManager] "
        f"Loaded {preset_manager.count()} presets, "
        f"{preset_manager.count(enabled_only=True)} "
        "enabled."
    )

    if not preset_manager.has_errors():
        return

    for file_path, error in (
        preset_manager.get_errors().items()
    ):
        print(
            "[PresetManager] "
            f"Error in {file_path}: {error}"
        )

def _print_lora_manager_status(
    lora_manager: LoRAManager,
) -> None:
    """
    Print LoRA catalog information and errors.
    """
    print(
        "[LoRAManager] "
        f"Loaded {lora_manager.count()} LoRAs, "
        f"{lora_manager.count(enabled_only=True)} "
        "enabled."
    )

    if not lora_manager.has_errors():
        return

    for file_path, error in (
        lora_manager.get_errors().items()
    ):
        print(
            "[LoRAManager] "
            f"Error in {file_path}: {error}"
        )