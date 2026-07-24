from collections.abc import Callable
from typing import Any

from generators.base import BaseGenerator
from core.models import (
    ModelDefinition,
    ResolvedModelSource,
)

from collections.abc import Callable

from generators.base import BaseGenerator


GeneratorFactory = Callable[
    [
        ModelDefinition,
        ResolvedModelSource | None,
    ],
    BaseGenerator,
]


class GeneratorRegistry:
    """
    Stores and creates registered generator backends.

    The registry maps a backend identifier, such as "diffusers",
    to a factory capable of creating the corresponding generator.
    """

    def __init__(self) -> None:
        self._factories: dict[
            str,
            GeneratorFactory,
        ] = {}

    def register(
        self,
        backend: str,
        factory: GeneratorFactory,
    ) -> None:
        """
        Register a generator factory for a backend identifier.
        """
        normalized_backend = self._normalize_backend(
            backend
        )

        if normalized_backend in self._factories:
            raise ValueError(
                "Generator backend is already registered: "
                f"{normalized_backend}"
            )

        self._factories[normalized_backend] = factory

    def replace(
        self,
        backend: str,
        factory: GeneratorFactory,
    ) -> None:
        """
        Register or replace an existing generator factory.
        """
        normalized_backend = self._normalize_backend(
            backend
        )

        self._factories[normalized_backend] = factory

    def unregister(
        self,
        backend: str,
    ) -> None:
        """
        Remove a registered generator backend.
        """
        normalized_backend = self._normalize_backend(
            backend
        )

        if normalized_backend not in self._factories:
            raise ValueError(
                "Generator backend is not registered: "
                f"{normalized_backend}"
            )

        del self._factories[normalized_backend]

    def create(
        self,
        model: ModelDefinition,
        model_source: ResolvedModelSource | None = None,
    ) -> BaseGenerator:
        """
        Create a generator for the model backend.
        """
        backend = model.backend

        factory = self._factories.get(backend)

        if factory is None:
            raise ValueError(
                "Generator backend is not registered: "
                f"{backend}"
            )

        return factory(
            model,
            model_source,
        )

    def has(
        self,
        backend: str,
    ) -> bool:
        """
        Determine whether a backend is registered.
        """
        normalized_backend = self._normalize_backend(
            backend
        )

        return normalized_backend in self._factories

    def get_registered_backends(
        self,
    ) -> tuple[str, ...]:
        """
        Return all registered backend identifiers.
        """
        return tuple(
            sorted(self._factories)
        )

    @staticmethod
    def _normalize_backend(
        backend: str | None,
    ) -> str:
        """
        Normalize and validate a backend identifier.
        """
        if backend is None:
            raise ValueError(
                "Model configuration does not define "
                "a generator backend."
            )

        normalized_backend = backend.strip().lower()

        if not normalized_backend:
            raise ValueError(
                "Generator backend cannot be empty."
            )

        return normalized_backend


