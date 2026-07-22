from typing import Any


class PipelineCache:
    """
    Stores loaded pipeline instances by cache key.
    """

    def __init__(self) -> None:
        self._items: dict[str, Any] = {}

    def has(
        self,
        key: str,
    ) -> bool:
        """
        Check whether a pipeline is cached.
        """
        return key in self._items

    def get(
        self,
        key: str,
    ) -> Any:
        """
        Return a cached pipeline.
        """
        return self._items[key]

    def add(
        self,
        key: str,
        pipeline: Any,
    ) -> None:
        """
        Store or replace a pipeline.
        """
        self._items[key] = pipeline

    def remove(
        self,
        key: str,
    ) -> Any | None:
        """
        Remove and return a cached pipeline.
        """
        return self._items.pop(
            key,
            None,
        )

    def clear(self) -> tuple[Any, ...]:
        """
        Remove and return all cached pipelines.
        """
        pipelines = tuple(
            self._items.values()
        )

        self._items.clear()

        return pipelines

    def get_keys(self) -> tuple[str, ...]:
        """
        Return all pipeline cache keys.
        """
        return tuple(
            sorted(self._items)
        )

    def get_model_ids(self) -> tuple[str, ...]:
        """
        Backward-compatible alias for existing code.
        """
        return self.get_keys()

    def count(self) -> int:
        """
        Return the number of cached pipelines.
        """
        return len(self._items)