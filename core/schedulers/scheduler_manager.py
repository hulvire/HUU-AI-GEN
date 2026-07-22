import json
from pathlib import Path

from core.schedulers.scheduler_definition import (
    SchedulerDefinition,
)


class SchedulerManager:
    """
    Loads and manages scheduler definitions.
    """

    def __init__(
        self,
        schedulers_directory: Path,
    ) -> None:
        self._schedulers_directory = (
            schedulers_directory
        )

        self._schedulers: dict[
            str,
            SchedulerDefinition,
        ] = {}

        self._errors: dict[str, str] = {}

    def scan(self) -> None:
        """
        Load all scheduler definitions from JSON files.
        """
        self._schedulers.clear()
        self._errors.clear()

        if not self._schedulers_directory.exists():
            self._schedulers_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            return

        for file_path in sorted(
            self._schedulers_directory.glob(
                "*.json"
            )
        ):
            self._load_file(file_path)

        self._validate_catalog()

    def _load_file(
        self,
        file_path: Path,
    ) -> None:
        """
        Load one scheduler definition file.
        """
        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            scheduler = (
                SchedulerDefinition.from_dict(
                    data
                )
            )

            if scheduler.id in self._schedulers:
                raise ValueError(
                    "Duplicate scheduler ID: "
                    f"{scheduler.id}"
                )

            self._schedulers[
                scheduler.id
            ] = scheduler

        except Exception as exception:
            self._errors[str(file_path)] = (
                f"{type(exception).__name__}: "
                f"{exception}"
            )

    def _validate_catalog(self) -> None:
        """
        Validate cross-file scheduler constraints.
        """
        default_schedulers = [
            scheduler
            for scheduler in self._schedulers.values()
            if scheduler.default
            and scheduler.enabled
        ]

        if len(default_schedulers) > 1:
            raise ValueError(
                "Only one enabled scheduler "
                "can be marked as default."
            )

    def get(
        self,
        scheduler_id: str,
    ) -> SchedulerDefinition | None:
        """
        Return a scheduler or None.
        """
        return self._schedulers.get(
            scheduler_id
        )

    def require(
        self,
        scheduler_id: str,
    ) -> SchedulerDefinition:
        """
        Return a scheduler or raise an error.
        """
        scheduler = self.get(
            scheduler_id
        )

        if scheduler is None:
            raise KeyError(
                "Unknown scheduler: "
                f"{scheduler_id}"
            )

        if not scheduler.enabled:
            raise ValueError(
                "Scheduler is disabled: "
                f"{scheduler_id}"
            )

        return scheduler

    def get_default(
        self,
    ) -> SchedulerDefinition | None:
        """
        Return the enabled default scheduler.
        """
        for scheduler in (
            self._schedulers.values()
        ):
            if (
                scheduler.default
                and scheduler.enabled
            ):
                return scheduler

        return next(
            (
                scheduler
                for scheduler
                in self._schedulers.values()
                if scheduler.enabled
            ),
            None,
        )

    def get_default_id(
        self,
    ) -> str | None:
        """
        Return the default scheduler ID.
        """
        scheduler = self.get_default()

        return (
            scheduler.id
            if scheduler is not None
            else None
        )

    def get_choices(
        self,
        enabled_only: bool = True,
    ) -> list[tuple[str, str]]:
        """
        Return Gradio dropdown choices.
        """
        schedulers = (
            scheduler
            for scheduler
            in self._schedulers.values()
            if (
                scheduler.enabled
                or not enabled_only
            )
        )

        return [
            (
                scheduler.name,
                scheduler.id,
            )
            for scheduler in schedulers
        ]

    def all(
        self,
        enabled_only: bool = False,
    ) -> tuple[
        SchedulerDefinition,
        ...,
    ]:
        """
        Return all scheduler definitions.
        """
        return tuple(
            scheduler
            for scheduler
            in self._schedulers.values()
            if (
                scheduler.enabled
                or not enabled_only
            )
        )

    def count(
        self,
        enabled_only: bool = False,
    ) -> int:
        """
        Return scheduler count.
        """
        return len(
            self.all(
                enabled_only=enabled_only
            )
        )

    def has_errors(self) -> bool:
        """
        Return whether loading errors occurred.
        """
        return bool(self._errors)

    def get_errors(self) -> dict[str, str]:
        """
        Return scheduler loading errors.
        """
        return dict(self._errors)