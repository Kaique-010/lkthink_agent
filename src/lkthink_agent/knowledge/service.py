
from typing import Any

from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge

from lkthink_agent.embeddings.jina import JinaEmbeddingProvider
from lkthink_agent.knowledge.config import KnowledgeConfig
from lkthink_agent.knowledge.reader import criar_text_reader
from lkthink_agent.observability.context import obter_contexto
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

        self.vector_store.create()
        self._initialized = True

    def _resolver_escopo(
        self,
        *,
        tenant_id: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
    ) -> tuple[str, str, str | None]:
        """
        Resolve o escopo de segurança.

        Dentro do Runtime, o contexto é a fonte de autoridade.
        Fora dele, tenant_id e agent_id são obrigatórios.
        """
        contexto = obter_contexto()

        if contexto is not None:
            tenant_contexto = contexto.tenant_id
            agent_contexto = (
                contexto.agent.id
                if contexto.agent is not None
                else None
            )
            usuario_contexto = contexto.metadata.get("user_id")

            if tenant_id is not None and tenant_id != tenant_contexto:
                raise ValueError(
                    "tenant_id informado diverge do contexto do Runtime."
                )

            if agent_id is not None and agent_id != agent_contexto:
                raise ValueError(
                    "agent_id informado diverge do contexto do Runtime."
                )

            if user_id is not None and user_id != usuario_contexto:
                raise ValueError(
                    "user_id informado diverge do contexto do Runtime."
                )

            tenant_id = tenant_contexto
            agent_id = agent_contexto
            user_id = usuario_contexto

        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id é obrigatório.")

        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id é obrigatório.")

        if user_id is not None and (
            not isinstance(user_id, str) or not user_id.strip()
        ):
            raise ValueError("user_id inválido.")

        return tenant_id, agent_id, user_id

    def add_text(
        self,
        text: str,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        tenant_id: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        tenant_id, agent_id, user_id = self._resolver_escopo(
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
        )

        if not isinstance(text, str) or not text.strip():
            raise ValueError("O conteúdo não pode ser vazio.")

        metadados = dict(metadata or {})

        # Campos reservados: nunca confiar nos valores enviados
        # pelo consumidor da biblioteca.
        metadados["tenant_id"] = tenant_id
        metadados["agent_id"] = agent_id

        self._ensure_initialized()

        self.knowledge.insert(
            name=name or "Documento",
            text_content=text,
            metadata=metadados,
            reader=self.reader,
            upsert=True,
            user_id=user_id,
        )

    def search(
        self,
        query: str,
        *,
        limit: int | None = None,
        tenant_id: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        tenant_id, agent_id, user_id = self._resolver_escopo(
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
        )

        if not isinstance(query, str) or not query.strip():
            raise ValueError("A consulta não pode ser vazia.")

        if limit is not None and limit <= 0:
            raise ValueError("O limite deve ser maior que zero.")

        filtros = {
            "tenant_id": tenant_id,
            "agent_id": agent_id,
        }

        self._ensure_initialized()

        documentos = self.knowledge.search(
            query=query,
            max_results=limit if limit is not None else self.config.top_k,
            filters=filtros,
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

    def count(
        self,
        *,
        tenant_id: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
    ) -> int:
        tenant_id, agent_id, user_id = self._resolver_escopo(
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
        )

        self._ensure_initialized()

        return self.vector_store.count(
            filters={
                "tenant_id": tenant_id,
                "agent_id": agent_id,
            },
            user_id=user_id,
        )

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize()
