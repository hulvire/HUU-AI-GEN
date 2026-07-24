from core.history import HistoryManager
from services.history_service import HistoryService


def create_history_manager() -> HistoryManager:
    """
    Create the application history manager.
    """
    return HistoryManager(
        history_service=HistoryService(),
    )