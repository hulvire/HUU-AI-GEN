from core.dto import HistoryItem
from services.history_service import HistoryService
from pathlib import Path

from core.dto import HistoryDetails, HistoryItem
from services.history_service import HistoryService



class HistoryManager:
    """
    Provides application-level access to generation history.
    """

    def __init__(
        self,
        history_service: HistoryService,
    ) -> None:
        self._history_service = history_service

    def get_items(self) -> list[HistoryItem]:
        """
        Return all valid history items, newest first.
        """
        return self._history_service.load()

    def get_latest(
        self,
        limit: int = 50,
    ) -> list[HistoryItem]:
        """
        Return the newest history items.
        """
        if limit <= 0:
            return []

        return self.get_items()[:limit]

    def get_details(
        self,
        metadata_path: Path,
    ) -> HistoryDetails | None:
        """
        Return complete details for one history item.
        """
        return self._history_service.load_details(
            metadata_path=metadata_path,
        )