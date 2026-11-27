
from agno.knowledge.embedder.jina import JinaEmbedder

from lkthink_agent.embeddings.base import BaseEmbedder
from lkthink_agent.knowledge.config import KnowledgeConfig


class JinaEmbeddingProvider(BaseEmbedder):
    def __init__(self, config: KnowledgeConfig):
        self.config = config
        self.client = JinaEmbedder(
            id=config.embedding_model,
            dimensions=config.embedding_dimensions,
            api_key=config.jina_api_key,
        )

    @property
    def dimensions(self) -> int:
        return self.config.embedding_dimensions

    def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("O texto para embedding não pode ser vazio.")

        embedding = self.client.get_embedding(text)

        if not embedding:
            raise RuntimeError("O Jina não retornou um embedding.")

        if len(embedding) != self.dimensions:
            raise RuntimeError(
                f"Dimensão incorreta: esperado {self.dimensions}, "
                f"recebido {len(embedding)}."
            )

        return embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        return [self.embed(text) for text in texts]
