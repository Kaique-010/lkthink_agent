
from sqlalchemy import func, or_, select

from lkthink_agent.embeddings.jina import JinaEmbeddingProvider
from lkthink_agent.knowledge.config import KnowledgeConfig


class PgVectorStore:
    def __init__(
        self,
        config: KnowledgeConfig,
        embedder: JinaEmbeddingProvider,
    ):
        self.config = config

        # Importação interna para manter Agno encapsulado.
        from agno.vectordb.pgvector import PgVector

        self.client = PgVector(
            table_name=config.vector_table,
            schema=config.schema,
            db_url=config.database_url,
            embedder=embedder.client,
            distance=config.distance,
            create_schema=True,
        )

    def create(self) -> None:
        self.client.create()

    def exists(self) -> bool:
        return self.client.exists()

    def count(
        self,
        *,
        filters: dict,
        user_id: str | None = None,
    ) -> int:
        """
        Conta documentos respeitando o escopo de tenant, agente e usuário.

        Usuários autenticados enxergam seus próprios registros e os
        registros compartilhados (user_id IS NULL).
        """
        if not filters:
            raise ValueError("Filtros de isolamento são obrigatórios.")

        possui_coluna_usuario = self.client._require_owner_column(user_id)

        condicoes = [
            self.client.table.c.meta_data.contains(filters)
        ]

        if user_id is not None and possui_coluna_usuario:
            condicoes.append(
                or_(
                    self.client.table.c.user_id == user_id,
                    self.client.table.c.user_id.is_(None),
                )
            )

        with self.client.Session() as session:
            statement = (
                select(func.count())
                .select_from(self.client.table)
                .where(*condicoes)
            )

            resultado = session.execute(statement).scalar_one()

            return int(resultado)

    def drop(self) -> None:
        self.client.drop()
