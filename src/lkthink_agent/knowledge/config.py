import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeConfig:
    database_url: str
    jina_api_key: str

    embedding_model: str = "jina-embeddings-v3"
    embedding_dimensions: int = 1024

    chunk_size: int = 900
    chunk_overlap: int = 100
    top_k: int = 5

    schema: str = "public"
    vector_table: str = "lkthink_vectors"
    knowledge_table: str = "lkthink_knowledge"

    distance: str = "cosine"

    def __post_init__(self):
        if not self.database_url:
            raise ValueError("DATABASE_URL não configurada.")

        if not self.database_url.startswith(
            ("postgresql://", "postgresql+psycopg://")
        ):
            raise ValueError(
                "O LKThink Agent exige uma conexão PostgreSQL."
            )

        if not self.jina_api_key:
            raise ValueError("JINA_API_KEY não configurada.")

        if self.embedding_dimensions <= 0:
            raise ValueError("Dimensão dos embeddings inválida.")

        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE deve ser maior que zero.")

        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("CHUNK_OVERLAP inválido.")

        if self.top_k <= 0:
            raise ValueError("TOP_K deve ser maior que zero.")

    @classmethod
    def from_env(cls):
        return cls(
            database_url=os.getenv("DATABASE_URL", ""),
            jina_api_key=os.getenv("JINA_API_KEY", ""),
            embedding_model=os.getenv(
                "JINA_EMBEDDING_MODEL",
                "jina-embeddings-v3",
            ),
            embedding_dimensions=int(
                os.getenv("JINA_EMBEDDING_DIMENSIONS", "1024")
            ),
            chunk_size=int(
                os.getenv("KNOWLEDGE_CHUNK_SIZE", "900")
            ),
            chunk_overlap=int(
                os.getenv("KNOWLEDGE_CHUNK_OVERLAP", "100")
            ),
            top_k=int(
                os.getenv("KNOWLEDGE_TOP_K", "5")
            ),
        )