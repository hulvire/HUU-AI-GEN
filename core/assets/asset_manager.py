from pathlib import Path
from typing import Iterator

from core.assets.asset_definition import AssetDefinition
from core.assets.asset_type import AssetType


class AssetManager:
    """
    Scans and provides physical AI assets stored on disk.
    """

    SUPPORTED_EXTENSIONS = {
        ".safetensors",
        ".ckpt",
        ".pt",
        ".pth",
        ".bin",
    }

    def __init__(
        self,
        directories: dict[AssetType, Path],
    ) -> None:
        self._directories = {
            asset_type: directory.resolve()
            for asset_type, directory in directories.items()
        }

        self._assets: dict[
            str,
            AssetDefinition,
        ] = {}

        self._errors: dict[
            Path,
            str,
        ] = {}

    def prepare_directories(self) -> None:
        """
        Create all configured asset directories.
        """
        for directory in self._directories.values():
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    def scan(self) -> None:
        """
        Scan all configured directories.
        """
        self._assets.clear()
        self._errors.clear()

        self.prepare_directories()

        for asset_type, directory in (
            self._directories.items()
        ):
            self._scan_directory(
                asset_type=asset_type,
                directory=directory,
            )

    def all(
        self,
        asset_type: AssetType | None = None,
    ) -> tuple[AssetDefinition, ...]:
        """
        Return all assets, optionally filtered by type.
        """
        assets = self._assets.values()

        if asset_type is not None:
            assets = (
                asset
                for asset in assets
                if asset.type == asset_type
            )

        return tuple(
            sorted(
                assets,
                key=lambda asset: (
                    asset.type.value,
                    asset.name.lower(),
                ),
            )
        )

    def get(
        self,
        asset_id: str,
    ) -> AssetDefinition | None:
        """
        Return an asset by its unique ID.
        """
        return self._assets.get(asset_id)

    def require(
        self,
        asset_id: str,
    ) -> AssetDefinition:
        """
        Return an asset or raise an explicit error.
        """
        asset = self.get(asset_id)

        if asset is None:
            raise ValueError(
                f"Asset was not found: {asset_id}"
            )

        return asset

    def has(
        self,
        asset_id: str,
    ) -> bool:
        return asset_id in self._assets

    def count(
        self,
        asset_type: AssetType | None = None,
    ) -> int:
        return len(
            self.all(
                asset_type=asset_type,
            )
        )


    def get_checkpoints(
        self,
    ) -> tuple[AssetDefinition, ...]:
        """
        Return all checkpoint assets.
        """
        return self.all(
            asset_type=AssetType.CHECKPOINT,
        )
        
    def get_choices(
        self,
        asset_type: AssetType | None = None,
    ) -> list[tuple[str, str]]:
        """
        Return asset choices suitable for UI dropdowns.
        """
        return [
            (
                asset.name,
                asset.id,
            )
            for asset in self.all(
                asset_type=asset_type,
            )
        ]

    def get_errors(
        self,
    ) -> dict[Path, str]:
        return dict(self._errors)

    def has_errors(self) -> bool:
        return bool(self._errors)

    def get_directory(
        self,
        asset_type: AssetType,
    ) -> Path:
        """
        Return the directory assigned to an asset type.
        """
        try:
            return self._directories[asset_type]
        except KeyError as exception:
            raise ValueError(
                "Asset directory is not configured for "
                f"type: {asset_type.value}"
            ) from exception

    def __iter__(
        self,
    ) -> Iterator[AssetDefinition]:
        return iter(self.all())

    def _scan_directory(
        self,
        asset_type: AssetType,
        directory: Path,
    ) -> None:
        try:
            for file_path in sorted(
                directory.rglob("*")
            ):
                if not file_path.is_file():
                    continue

                extension = (
                    file_path.suffix.lower()
                )

                if (
                    extension
                    not in self.SUPPORTED_EXTENSIONS
                ):
                    continue

                asset = self._create_asset(
                    asset_type=asset_type,
                    file_path=file_path,
                )

                if asset.id in self._assets:
                    raise ValueError(
                        "Duplicate asset ID: "
                        f"{asset.id}"
                    )

                self._assets[asset.id] = asset

        except (
            OSError,
            ValueError,
        ) as exception:
            self._errors[directory] = (
                f"{type(exception).__name__}: "
                f"{exception}"
            )

    def _create_asset(
        self,
        asset_type: AssetType,
        file_path: Path,
    ) -> AssetDefinition:
        relative_path = file_path.relative_to(
            self.get_directory(asset_type)
        )

        relative_without_suffix = (
            relative_path.with_suffix("")
        )

        normalized_path = "-".join(
            relative_without_suffix.parts
        )

        asset_id = (
            f"{asset_type.value}:"
            f"{normalized_path.lower()}"
        )

        return AssetDefinition(
            id=asset_id,
            name=file_path.stem,
            type=asset_type,
            path=file_path.resolve(),
            extension=file_path.suffix.lower(),
            size_bytes=file_path.stat().st_size,
        )