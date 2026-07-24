from dataclasses import dataclass
from typing import Any

import gradio as gr

from core.application import Application
from core.assets import (
    AssetManager,
    CheckpointManager,
)
from core.engine import GenerationEngine
from core.loras import LoRAManager
from core.models import (
    ModelAssetResolver,
    ModelManager,
)
from core.pipelines import PipelineManager
from core.presets import PresetManager
from core.registry import GeneratorRegistry
from core.schedulers import (
    SchedulerFactory,
    SchedulerManager,
)
from services.generator_service import GeneratorService
from core.history import HistoryManager




@dataclass(slots=True)
class ApplicationContext:
    """
    Contains all runtime dependencies of the application.
    """

    application: Application
    registry: GeneratorRegistry

    model_manager: ModelManager
    preset_manager: PresetManager
    scheduler_manager: SchedulerManager
    lora_manager: LoRAManager
    history_manager: HistoryManager

    scheduler_factory: SchedulerFactory
    asset_manager: AssetManager
    checkpoint_manager: CheckpointManager
    pipeline_manager: PipelineManager
    model_asset_resolver: ModelAssetResolver

    engine: GenerationEngine
    generator_service: GeneratorService

    demo: gr.Blocks
    theme: Any
    css: str
    js: str
    head: str

    def run(self) -> None:
        """
        Launch the Gradio application.
        """
        self.demo.launch(
            theme=self.theme,
            css=self.css,
            js=self.js,
            head=self.head,
        )