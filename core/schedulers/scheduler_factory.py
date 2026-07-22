from typing import Any, TypeAlias

from diffusers import (
    DDIMScheduler,
    DPMSolverMultistepScheduler,
    EulerAncestralDiscreteScheduler,
    EulerDiscreteScheduler,
    UniPCMultistepScheduler,
)
from diffusers.schedulers.scheduling_utils import (
    SchedulerMixin,
)

from core.schedulers.scheduler_definition import (
    SchedulerDefinition,
)


SchedulerClass: TypeAlias = type[SchedulerMixin]


class SchedulerFactory:
    """
    Creates Diffusers scheduler instances
    from scheduler definitions.
    """

    def __init__(self) -> None:
        self._scheduler_classes: dict[
            str,
            SchedulerClass,
        ] = {
            "DDIMScheduler": DDIMScheduler,
            "DPMSolverMultistepScheduler": (
                DPMSolverMultistepScheduler
            ),
            "EulerAncestralDiscreteScheduler": (
                EulerAncestralDiscreteScheduler
            ),
            "EulerDiscreteScheduler": (
                EulerDiscreteScheduler
            ),
            "UniPCMultistepScheduler": (
                UniPCMultistepScheduler
            ),
        }

    def create(
        self,
        definition: SchedulerDefinition,
        source_scheduler: SchedulerMixin,
    ) -> SchedulerMixin:
        """
        Create a scheduler using the configuration
        of an existing pipeline scheduler.
        """
        scheduler_class = self._get_scheduler_class(
            definition.class_name
        )

        configuration = self._build_configuration(
            definition=definition,
            source_scheduler=source_scheduler,
        )

        return scheduler_class.from_config(
            configuration
        )

    def supports(
        self,
        class_name: str,
    ) -> bool:
        """
        Return whether a scheduler class is registered.
        """
        return class_name in self._scheduler_classes

    def get_supported_class_names(
        self,
    ) -> tuple[str, ...]:
        """
        Return all registered scheduler class names.
        """
        return tuple(
            self._scheduler_classes.keys()
        )

    def _get_scheduler_class(
        self,
        class_name: str,
    ) -> SchedulerClass:
        """
        Resolve a registered scheduler class.
        """
        scheduler_class = (
            self._scheduler_classes.get(
                class_name
            )
        )

        if scheduler_class is None:
            raise ValueError(
                "Unsupported scheduler class: "
                f"{class_name}"
            )

        return scheduler_class

    @staticmethod
    def _build_configuration(
        definition: SchedulerDefinition,
        source_scheduler: SchedulerMixin,
    ) -> dict[str, Any]:
        """
        Merge the source scheduler configuration
        with the definition overrides.
        """
        source_configuration = dict(
            source_scheduler.config
        )

        return {
            **source_configuration,
            **definition.configuration,
        }