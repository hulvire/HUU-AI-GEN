from dataclasses import dataclass

from core.loras.lora_runtime import (
    LoRARuntime,
)


@dataclass(slots=True, frozen=True)
class LoRASelection:
    """
    Immutable collection of LoRA runtime configurations
    selected for one image generation.
    """

    runtimes: tuple[LoRARuntime, ...] = ()

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """
        Validate the complete LoRA selection.
        """
        seen_ids: set[str] = set()
        seen_adapter_names: set[str] = set()

        for runtime in self.runtimes:
            runtime.validate()

            if runtime.id in seen_ids:
                raise ValueError(
                    "Duplicate LoRA ID in selection: "
                    f"{runtime.id}"
                )

            if runtime.adapter_name in seen_adapter_names:
                raise ValueError(
                    "Duplicate LoRA adapter name "
                    "in selection: "
                    f"{runtime.adapter_name}"
                )

            seen_ids.add(runtime.id)
            seen_adapter_names.add(
                runtime.adapter_name
            )

    def all(self) -> tuple[LoRARuntime, ...]:
        """
        Return all selected LoRA runtimes.
        """
        return self.runtimes

    def active(self) -> tuple[LoRARuntime, ...]:
        """
        Return only adapters that should be applied.
        """
        return tuple(
            runtime
            for runtime in self.runtimes
            if runtime.is_active
        )

    def enabled(self) -> tuple[LoRARuntime, ...]:
        """
        Return all enabled adapters, including scale zero.
        """
        return tuple(
            runtime
            for runtime in self.runtimes
            if runtime.enabled
        )

    def get(
        self,
        lora_id: str,
    ) -> LoRARuntime | None:
        """
        Find one selected LoRA by its catalog ID.
        """
        for runtime in self.runtimes:
            if runtime.id == lora_id:
                return runtime

        return None

    def require(
        self,
        lora_id: str,
    ) -> LoRARuntime:
        """
        Return one selected LoRA or raise an error.
        """
        runtime = self.get(lora_id)

        if runtime is None:
            raise ValueError(
                "LoRA is not present in selection: "
                f"{lora_id}"
            )

        return runtime

    def has(
        self,
        lora_id: str,
    ) -> bool:
        return self.get(lora_id) is not None

    def adapter_names(
        self,
        *,
        active_only: bool = True,
    ) -> tuple[str, ...]:
        """
        Return Diffusers adapter names.
        """
        runtimes = (
            self.active()
            if active_only
            else self.runtimes
        )

        return tuple(
            runtime.adapter_name
            for runtime in runtimes
        )

    def scales(
        self,
        *,
        active_only: bool = True,
    ) -> tuple[float, ...]:
        """
        Return adapter scales in selection order.
        """
        runtimes = (
            self.active()
            if active_only
            else self.runtimes
        )

        return tuple(
            runtime.scale
            for runtime in runtimes
        )

    def trigger_words(
        self,
        *,
        active_only: bool = True,
    ) -> tuple[str, ...]:
        """
        Return unique trigger words in stable order.
        """
        runtimes = (
            self.active()
            if active_only
            else self.runtimes
        )

        result: list[str] = []
        seen: set[str] = set()

        for runtime in runtimes:
            for trigger_word in (
                runtime.trigger_words
            ):
                normalized = trigger_word.strip()

                if (
                    not normalized
                    or normalized in seen
                ):
                    continue

                seen.add(normalized)
                result.append(normalized)

        return tuple(result)

    def with_runtime(
        self,
        runtime: LoRARuntime,
    ) -> "LoRASelection":
        """
        Return a selection with one runtime added.

        Existing runtime with the same LoRA ID is replaced
        while preserving its position.
        """
        updated = list(self.runtimes)

        for index, existing in enumerate(updated):
            if existing.id == runtime.id:
                updated[index] = runtime

                return LoRASelection(
                    runtimes=tuple(updated),
                )

        updated.append(runtime)

        return LoRASelection(
            runtimes=tuple(updated),
        )

    def without(
        self,
        lora_id: str,
    ) -> "LoRASelection":
        """
        Return a selection without the given LoRA.
        """
        return LoRASelection(
            runtimes=tuple(
                runtime
                for runtime in self.runtimes
                if runtime.id != lora_id
            ),
        )

    @property
    def is_empty(self) -> bool:
        return not self.runtimes

    @property
    def has_active(self) -> bool:
        return bool(self.active())

    @property
    def total(self) -> int:
        return len(self.runtimes)

    @property
    def active_total(self) -> int:
        return len(self.active())

    def __len__(self) -> int:
        return self.total

    def __iter__(self):
        return iter(self.runtimes)

    @classmethod
    def empty(cls) -> "LoRASelection":
        """
        Create an empty LoRA selection.
        """
        return cls()

    @classmethod
    def from_runtimes(
        cls,
        runtimes: tuple[LoRARuntime, ...]
        | list[LoRARuntime],
    ) -> "LoRASelection":
        """
        Create a validated selection from runtimes.
        """
        return cls(
            runtimes=tuple(runtimes),
        )