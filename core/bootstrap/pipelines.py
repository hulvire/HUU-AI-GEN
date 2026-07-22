from core.pipelines import (
    PipelineCache,
    PipelineManager,
)
from core.schedulers import (
    SchedulerFactory,
    SchedulerManager,
)


def create_pipeline_manager(
    scheduler_manager: SchedulerManager,
    scheduler_factory: SchedulerFactory,
) -> PipelineManager:
    """
    Create the application pipeline manager.
    """
    return PipelineManager(
        cache=PipelineCache(),
        scheduler_manager=scheduler_manager,
        scheduler_factory=scheduler_factory,
    )