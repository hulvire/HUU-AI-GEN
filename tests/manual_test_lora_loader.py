from core.loras import (
    LoRADefinition,
    LoRARuntime,
    LoRASelection,
)
from services.lora_loader import LoRALoader


class FakePipeline:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def load_lora_weights(
        self,
        source: str,
        **kwargs,
    ) -> None:
        self.calls.append(
            (
                "load",
                source,
                kwargs,
            )
        )

    def set_adapters(
        self,
        adapter_names: list[str],
        adapter_weights: list[float],
    ) -> None:
        self.calls.append(
            (
                "set",
                adapter_names,
                adapter_weights,
            )
        )

    def unload_lora_weights(self) -> None:
        self.calls.append(
            (
                "unload",
            )
        )


definition = LoRADefinition(
    id="test-lora",
    name="Test LoRA",
    repository_id="example/test-lora",
    weight_name="test.safetensors",
    default_scale=0.8,
)

definition.validate()

runtime = LoRARuntime.from_definition(
    definition,
    scale=0.65,
)

selection = LoRASelection.from_runtimes(
    [runtime]
)

pipeline = FakePipeline()
loader = LoRALoader()

loader.apply(
    pipeline=pipeline,
    selection=selection,
)

for call in pipeline.calls:
    print(call)