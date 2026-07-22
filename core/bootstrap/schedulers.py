from core.paths import SCHEDULER_CONFIGS
from core.schedulers import (
    SchedulerFactory,
    SchedulerManager,
)


def create_scheduler_dependencies(
) -> tuple[
    SchedulerManager,
    SchedulerFactory,
]:
    """
    Create and validate scheduler runtime dependencies.
    """
    scheduler_manager = SchedulerManager(
        schedulers_directory=SCHEDULER_CONFIGS,
    )

    scheduler_manager.scan()

    scheduler_factory = SchedulerFactory()

    _validate_scheduler_classes(
        scheduler_manager=scheduler_manager,
        scheduler_factory=scheduler_factory,
    )

    return (
        scheduler_manager,
        scheduler_factory,
    )


def _validate_scheduler_classes(
    scheduler_manager: SchedulerManager,
    scheduler_factory: SchedulerFactory,
) -> None:
    """
    Ensure every enabled scheduler uses a supported class.
    """
    unsupported_schedulers: list[str] = []

    for scheduler in scheduler_manager.all(
        enabled_only=True,
    ):
        if not scheduler_factory.supports(
            scheduler.class_name
        ):
            unsupported_schedulers.append(
                f"{scheduler.id} "
                f"({scheduler.class_name})"
            )

    if unsupported_schedulers:
        unsupported = ", ".join(
            unsupported_schedulers
        )

        raise ValueError(
            "Unsupported scheduler definitions: "
            f"{unsupported}"
        )