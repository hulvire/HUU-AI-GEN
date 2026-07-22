from abc import ABC, abstractmethod

from core.dto import GenerationRequest, GenerationResult


class BaseGenerator(ABC):
    """
    Contract implemented by every generation backend.
    """

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        raise NotImplementedError