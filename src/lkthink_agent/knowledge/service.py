
from typing import Any

from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge

from lkthink_agent.embeddings.jina import JinaEmbeddingProvider
from lkthink_agent.knowledge.config import KnowledgeConfig
from lkthink_agent.knowledge.reader import criar_text_reader
from lkthink_agent.vectorstores.pgvector import PgVectorStore


class KnowledgeService:
    def __init__(self, config: KnowledgeConfig):
        self.config = config

        self.embedder = JinaEmbeddingProvider(config)

        self.vector_store = PgVectorStore(
            config=config,
            embedder=self.embedder,
        )

        self.content_db = PostgresDb(
            db_url=config.database_url,
            db_schema=config.schema,
            knowledge_table=config.knowledge_table,
        )

        self.reader = criar_text_reader(config)

        self.knowledge = Knowledge(
            name="LKThink Knowledge",
            description="Base de conhecimento vetorial do LKThink Agent.",
            vector_db=self.vector_store.client,
            contents_db=self.content_db,
            max_results=config.top_k,
        )

        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        # Inicializa somente o armazenamento vetorial.
        # O Agno cria a tabela de conteúdos sob demanda.
        self.vector_store.create()

        self._initialized = True

    def add_text(
        self,
        text: str,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> None:
        self._ensure_initialized()

        if not text or not text.strip():
            raise ValueError("O conteúdo não pode ser vazio.")

        self.knowledge.insert(
            name=name or "Documento",
            text_content=text,
            metadata=metadata or {},
            reader=self.reader,
            upsert=True,
            user_id=user_id,
        )

    def search(
        self,
        query: str,
        limit: int | None = None,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_initialized()

        if not query or not query.strip():
            raise ValueError("A consulta não pode ser vazia.")

        documentos = self.knowledge.search(
            query=query,
            max_results=limit or self.config.top_k,
            user_id=user_id,
        )

        return [
            {
                "id": documento.id,
                "content": documento.content,
                "metadata": documento.meta_data,
            }
            for documento in documentos
        ]

    def count(self) -> int:
        self._ensure_initialized()
        return self.vector_store.count()

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize()
