import json
from pathlib import Path
from typing import Any

from core.dto import HistoryDetails, HistoryItem
from core.paths import OUTPUTS


class HistoryService:
    """
    Reads generation history from outputs/.
    """

    def load(self) -> list[HistoryItem]:
        """
        Load generation history.

        Invalid or incomplete metadata files are skipped.
        Items are returned newest first.
        """
        if not OUTPUTS.exists():
            return []

        items: list[HistoryItem] = []

        for metadata_path in OUTPUTS.rglob("*.json"):
            item = self._load_item(
                metadata_path=metadata_path,
            )

            if item is not None:
                items.append(item)

        return sorted(
            items,
            key=lambda item: item.created_at,
            reverse=True,
        )

    def _load_item(
        self,
        metadata_path: Path,
    ) -> HistoryItem | None:
        """
        Load one history item from a metadata file.
        """
        try:
            metadata = self._read_metadata(
                metadata_path=metadata_path,
            )

            image_path = self._resolve_image_path(
                metadata=metadata,
                metadata_path=metadata_path,
            )

            if image_path is None:
                return None

            return self._create_item(
                metadata=metadata,
                metadata_path=metadata_path,
                image_path=image_path,
            )

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            json.JSONDecodeError,
        ):
            return None

    def load_details(
        self,
        metadata_path: Path,
    ) -> HistoryDetails | None:
        """
        Load complete details for one saved generation.
        """
        try:
            metadata = self._read_metadata(
                metadata_path=metadata_path,
            )

            image_path = self._resolve_image_path(
                metadata=metadata,
                metadata_path=metadata_path,
            )

            if image_path is None:
                return None

            return self._create_details(
                metadata=metadata,
                metadata_path=metadata_path,
                image_path=image_path,
            )

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            json.JSONDecodeError,
        ):
            return None

    def _create_details(
        self,
        metadata: dict[str, Any],
        metadata_path: Path,
        image_path: Path,
    ) -> HistoryDetails:
        """
        Convert metadata into complete generation details.
        """
        application = metadata.get(
            "application",
            {},
        )

        model = metadata.get(
            "model",
            {},
        )

        generation = metadata.get(
            "generation",
            {},
        )

        preset = generation.get(
            "preset",
            {},
        )

        scheduler = generation.get(
            "scheduler",
            {},
        )

        input_data = metadata.get(
            "input",
            {},
        )

        output = metadata.get(
            "output",
            {},
        )

        raw_input_image = input_data.get("image")

        input_image_path = (
            Path(raw_input_image)
            if raw_input_image
            else None
        )

        raw_loras = generation.get(
            "loras",
            [],
        )

        loras = tuple(
            item
            for item in raw_loras
            if isinstance(item, dict)
        )

        return HistoryDetails(
            image_path=image_path,
            metadata_path=metadata_path,
            created_at=str(
                output.get(
                    "created_at",
                    "",
                )
            ),
            prompt=str(
                metadata.get(
                    "prompt",
                    "",
                )
            ),
            negative_prompt=str(
                metadata.get(
                    "negative_prompt",
                    "",
                )
            ),
            seed=int(
                metadata.get(
                    "seed",
                    0,
                )
            ),
            model_id=str(
                model.get(
                    "id",
                    "",
                )
            ),
            model_name=str(
                model.get(
                    "name",
                    "",
                )
            ),
            repository_id=(
                str(model["repository_id"])
                if model.get("repository_id")
                else None
            ),
            backend=str(
                model.get(
                    "backend",
                    "",
                )
            ),
            mode=str(
                generation.get(
                    "mode",
                    "",
                )
            ),
            preset_id=(
                str(preset["id"])
                if preset.get("id")
                else None
            ),
            preset_name=(
                str(preset["name"])
                if preset.get("name")
                else None
            ),
            scheduler_id=(
                str(scheduler["id"])
                if scheduler.get("id")
                else None
            ),
            scheduler_name=(
                str(scheduler["name"])
                if scheduler.get("name")
                else None
            ),
            loras=loras,
            width=int(
                generation.get(
                    "width",
                    0,
                )
            ),
            height=int(
                generation.get(
                    "height",
                    0,
                )
            ),
            steps=int(
                generation.get(
                    "steps",
                    0,
                )
            ),
            guidance_scale=float(
                generation.get(
                    "guidance_scale",
                    0.0,
                )
            ),
            duration_seconds=float(
                generation.get(
                    "duration_seconds",
                    0.0,
                )
            ),
            input_used=bool(
                input_data.get(
                    "used",
                    False,
                )
            ),
            input_image_path=input_image_path,
            strength=(
                float(input_data["strength"])
                if input_data.get("strength")
                is not None
                else None
            ),
            application_name=str(
                application.get(
                    "name",
                    "",
                )
            ),
            application_version=str(
                application.get(
                    "version",
                    "",
                )
            ),
            application_environment=str(
                application.get(
                    "environment",
                    "",
                )
            ),
        )


    def _read_metadata(
        self,
        metadata_path: Path,
    ) -> dict[str, Any]:
        """
        Read and validate a metadata JSON file.
        """
        with metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        if not isinstance(metadata, dict):
            raise ValueError(
                "Generation metadata must be an object."
            )

        return metadata

    def _resolve_image_path(
        self,
        metadata: dict[str, Any],
        metadata_path: Path,
    ) -> Path | None:
        """
        Resolve the generated image path.

        The metadata path is preferred. A PNG file with the same
        filename is used as a fallback.
        """
        output = metadata.get("output", {})
        stored_image_path = output.get("image")

        if stored_image_path:
            image_path = Path(stored_image_path)

            if not image_path.is_absolute():
                image_path = (
                    metadata_path.parent
                    / image_path
                ).resolve()

            if image_path.exists():
                return image_path

        fallback_path = metadata_path.with_suffix(
            ".png"
        )

        if fallback_path.exists():
            return fallback_path

        return None

    def _create_item(
        self,
        metadata: dict[str, Any],
        metadata_path: Path,
        image_path: Path,
    ) -> HistoryItem:
        """
        Convert generation metadata into a HistoryItem.
        """
        model = metadata.get("model", {})
        generation = metadata.get(
            "generation",
            {},
        )
        output = metadata.get("output", {})

        preset = generation.get("preset", {})
        scheduler = generation.get(
            "scheduler",
            {},
        )

        return HistoryItem(
            image_path=image_path,
            metadata_path=metadata_path,
            created_at=str(
                output.get(
                    "created_at",
                    "",
                )
            ),
            prompt=str(
                metadata.get(
                    "prompt",
                    "",
                )
            ),
            negative_prompt=str(
                metadata.get(
                    "negative_prompt",
                    "",
                )
            ),
            model=str(
                model.get(
                    "name",
                    model.get(
                        "id",
                        "",
                    ),
                )
            ),
            preset=str(
                preset.get(
                    "name",
                    preset.get(
                        "id",
                        "",
                    ),
                )
            ),
            scheduler=str(
                scheduler.get(
                    "name",
                    scheduler.get(
                        "id",
                        "",
                    ),
                )
            ),
            width=int(
                generation.get(
                    "width",
                    0,
                )
            ),
            height=int(
                generation.get(
                    "height",
                    0,
                )
            ),
            seed=int(
                metadata.get(
                    "seed",
                    0,
                )
            ),
            duration_seconds=float(
                generation.get(
                    "duration_seconds",
                    0.0,
                )
            ),
        )