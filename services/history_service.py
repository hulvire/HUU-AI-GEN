from pathlib import Path

from core.dto import HistoryItem


class HistoryService:
    """
    Reads generation history from outputs/.
    """

    def load(self) -> list[HistoryItem]:
        """
        Load generation history.

        Returns newest items first.
        """
        return []