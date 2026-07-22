from pathlib import Path

from core.assets import (
    AssetDefinition,
    AssetManager,
    CheckpointManager,
)
from core.models.model_definition import (
    ModelDefinition,
)
from core.models.resolved_model_source import (
    ResolvedModelSource,
)


class ModelAssetResolver:
    """
    Resolves and validates physical model sources
    from model definitions.
    """

    def __init__(
        self,
        asset_manager: AssetManager,
        checkpoint_manager: CheckpointManager,
    ) -> None:
        self._asset_manager = asset_manager
        self._checkpoint_manager = checkpoint_manager

    def resolve_checkpoint(
        self,
        model: ModelDefinition,
    ) -> AssetDefinition | None:
        """
        Resolve a checkpoint asset assigned to a model.
        """
        if not model.checkpoint_asset_id:
            return None

        return self._asset_manager.require(
            model.checkpoint_asset_id
        )

    def resolve_source(
        self,
        model: ModelDefinition,
    ) -> ResolvedModelSource:
        """
        Resolve the complete runtime source of a model.
        """
        if model.checkpoint_asset_id:
            checkpoint = self.resolve_checkpoint(model)

            if checkpoint is None:
                raise ValueError(
                    "Checkpoint asset could not be resolved "
                    f"for model: {model.id}"
                )

            checkpoint_path = (
                self._checkpoint_manager.resolve(
                    checkpoint.path
                )
            )

            return ResolvedModelSource(
                type="asset",
                local_path=checkpoint_path,
            )

        if model.model_path:
            checkpoint_path = (
                self._checkpoint_manager.resolve(
                    model.model_path
                )
            )

            return ResolvedModelSource(
                type="path",
                local_path=checkpoint_path,
            )

        if model.repository_id:
            return ResolvedModelSource(
                type="repository",
                repository_id=model.repository_id,
            )

        raise ValueError(
            f"Model has no configured source: {model.id}"
        )

    def resolve_path(
        self,
        model: ModelDefinition,
    ) -> Path | None:
        """
        Resolve the validated local filesystem path
        of a model.
        """
        checkpoint = self.resolve_checkpoint(model)

        if checkpoint is not None:
            return self._checkpoint_manager.resolve(
                checkpoint.path
            )

        if model.model_path:
            return self._checkpoint_manager.resolve(
                model.model_path
            )

        return None

    def validate(
        self,
        model: ModelDefinition,
    ) -> list[str]:
        """
        Validate the physical source assigned to a model.
        """
        errors: list[str] = []

        if model.checkpoint_asset_id:
            asset = self._asset_manager.get(
                model.checkpoint_asset_id
            )

            if asset is None:
                errors.append(
                    "Checkpoint asset was not found: "
                    f"{model.checkpoint_asset_id}"
                )
            else:
                try:
                    self._checkpoint_manager.resolve(
                        asset.path
                    )
                except ValueError as error:
                    errors.append(str(error))

        if model.model_path:
            try:
                self._checkpoint_manager.resolve(
                    model.model_path
                )
            except ValueError as error:
                errors.append(str(error))

        if (
            model.backend != "pillow"
            and not model.has_source
        ):
            errors.append(
                "Model does not define a repository, "
                "local path or checkpoint asset."
            )

        return errors