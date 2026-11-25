from agno.vectordb.pgvector import PgVector

from lkthink_agent.embeddings.jina import JinaEmbeddingProvider
from lkthink_agent.knowledge.config import KnowledgeConfig


class PgVectorStore:

    def __init__(
        self,
        config: KnowledgeConfig,
        embedder: JinaEmbeddingProvider,
    ):
        self.config = config

        self.client = PgVector(
            table_name=config.vector_table,
            schema=config.schema,
            db_url=config.database_url,
            embedder=embedder.client,
            distance="cosine",
            create_schema=True,
        )

    def create(self) -> None:
        self.client.create()

    def exists(self) -> bool:
        return self.client.exists()

    def count(self) -> int:
        return self.client.get_count()

    def drop(self) -> None:
        self.client.drop()