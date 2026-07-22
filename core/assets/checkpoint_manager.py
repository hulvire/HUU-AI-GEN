from pathlib import Path


class CheckpointManager:
    """
    Resolves and validates local model checkpoint files.
    """

    SUPPORTED_EXTENSIONS = {
        ".safetensors",
        ".ckpt",
    }

    def __init__(
        self,
        checkpoints_directory: Path,
    ) -> None:
        self._checkpoints_directory = (
            checkpoints_directory.resolve()
        )

    @property
    def checkpoints_directory(self) -> Path:
        """
        Return the configured checkpoints directory.
        """
        return self._checkpoints_directory

    def resolve(
        self,
        checkpoint_path: str | Path,
    ) -> Path:
        """
        Resolve and validate a checkpoint path.

        Relative paths are resolved against the configured
        checkpoints directory.
        """
        path = Path(checkpoint_path)

        if not path.is_absolute():
            path = (
                self._checkpoints_directory
                / path
            )

        path = path.resolve()

        self._validate_path(path)

        return path

    def exists(
        self,
        checkpoint_path: str | Path,
    ) -> bool:
        """
        Check whether a valid checkpoint exists.
        """
        try:
            self.resolve(checkpoint_path)
        except ValueError:
            return False

        return True

    def is_supported(
        self,
        checkpoint_path: str | Path,
    ) -> bool:
        """
        Check whether the checkpoint file extension
        is supported.
        """
        extension = Path(
            checkpoint_path
        ).suffix.lower()

        return extension in self.SUPPORTED_EXTENSIONS

    def _validate_path(
        self,
        path: Path,
    ) -> None:
        """
        Validate the resolved checkpoint path.
        """
        if not path.exists():
            raise ValueError(
                "Checkpoint file does not exist: "
                f"{path}"
            )

        if not path.is_file():
            raise ValueError(
                "Checkpoint path is not a file: "
                f"{path}"
            )

        if not self.is_supported(path):
            supported = ", ".join(
                sorted(self.SUPPORTED_EXTENSIONS)
            )

            raise ValueError(
                "Unsupported checkpoint file format: "
                f"{path.suffix or '<no extension>'}. "
                f"Supported formats: {supported}."
            )