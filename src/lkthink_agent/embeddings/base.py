from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Gera um Embedding a partir de um Texto"""
        raise NotImplementedError("Subclasses Precisam Implementar este método.")
    
    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings para uma lista de textos"""
        raise NotImplementedError("Subclasses Precisam Implementar este método.")
    
    @property
    def dimensions(self) -> int:
        """Retorna a dimensão dos embeddings"""
        raise NotImplementedError("Subclasses Precisam Implementar este método.")