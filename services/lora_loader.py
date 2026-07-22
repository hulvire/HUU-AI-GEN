from pathlib import Path
from typing import Any

from core.loras import (
    LoRARuntime,
    LoRASelection,
)


class LoRALoader:
    """
    Applies LoRA selections to Diffusers pipelines.

    The loader owns the runtime interaction with
    Diffusers LoRA APIs. Generators and engines should
    not load adapter weights directly.
    """

    def apply(
        self,
        pipeline: Any,
        selection: LoRASelection,
    ) -> None:
        """
        Load and activate all adapters in a selection.

        An empty selection clears previously loaded
        adapters from the pipeline.
        """
        self._validate_pipeline(pipeline)

        active_runtimes = selection.active()

        self.clear(pipeline)

        if not active_runtimes:
            return

        for runtime in active_runtimes:
            self._load_runtime(
                pipeline=pipeline,
                runtime=runtime,
            )

        pipeline.set_adapters(
            list(selection.adapter_names()),
            adapter_weights=list(
                selection.scales()
            ),
        )

    def clear(
        self,
        pipeline: Any,
    ) -> None:
        """
        Remove all LoRA weights from a pipeline.

        Pipelines without loaded LoRA adapters may raise
        implementation-specific errors, so unloading is
        treated as an idempotent operation.
        """
        unload = getattr(
            pipeline,
            "unload_lora_weights",
            None,
        )

        if not callable(unload):
            return

        try:
            unload()
        except (
            AttributeError,
            KeyError,
            RuntimeError,
            ValueError,
        ):
            # The pipeline may support the method but
            # currently have no LoRA adapters loaded.
            return

    def _load_runtime(
        self,
        pipeline: Any,
        runtime: LoRARuntime,
    ) -> None:
        """
        Load one runtime adapter into the pipeline.
        """
        if not runtime.has_source:
            raise ValueError(
                f"LoRA '{runtime.id}' has no configured "
                "repository_id or file_path."
            )

        source = self._resolve_source(runtime)

        arguments: dict[str, Any] = {
            "adapter_name": runtime.adapter_name,
        }

        if runtime.weight_name:
            arguments["weight_name"] = (
                runtime.weight_name
            )

        pipeline.load_lora_weights(
            source,
            **arguments,
        )

    @staticmethod
    def _resolve_source(
        runtime: LoRARuntime,
    ) -> str:
        """
        Resolve the value passed to load_lora_weights().
        """
        if runtime.file_path:
            file_path = Path(
                runtime.file_path
            ).expanduser()

            if not file_path.is_absolute():
                file_path = file_path.resolve()

            if not file_path.exists():
                raise FileNotFoundError(
                    "LoRA file or directory was not "
                    f"found: {file_path}"
                )

            return str(file_path)

        if runtime.repository_id:
            return runtime.repository_id

        raise ValueError(
            f"LoRA source is undefined: {runtime.id}"
        )

    @staticmethod
    def _validate_pipeline(
        pipeline: Any,
    ) -> None:
        """
        Ensure the pipeline exposes required LoRA APIs.
        """
        load = getattr(
            pipeline,
            "load_lora_weights",
            None,
        )

        set_adapters = getattr(
            pipeline,
            "set_adapters",
            None,
        )

        if not callable(load):
            raise TypeError(
                "Pipeline does not support "
                "load_lora_weights()."
            )

        if not callable(set_adapters):
            raise TypeError(
                "Pipeline does not support "
                "set_adapters()."
            )