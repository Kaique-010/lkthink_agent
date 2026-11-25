from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Contrato interno para construção de modelos."""

    @abstractmethod
    def build_model(self) -> Any:
        raise NotImplementedError("Subclasses Precisam Implementar esse método")