from core.assets import CheckpointManager
from core.paths import CHECKPOINTS


def create_checkpoint_manager() -> CheckpointManager:
    """
    Create the application checkpoint manager.
    """
    CHECKPOINTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    return CheckpointManager(
        checkpoints_directory=CHECKPOINTS,
    )