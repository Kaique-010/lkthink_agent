
import os
import uuid

from sqlalchemy import create_engine, text

from lkthink_agent import (
    AgentConfig,
    AgentManager,
    AgentRuntime,
    LKThinkAgent,
)

from lkthink_agent.knowledge.service import KnowledgeService
from lkthink_agent.memory.service import MemoryService
from lkthink_agent.mcp.manager import MCPManager
from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.events import EventName
from lkthink_agent.observability.logger import EventLogger
from lkthink_agent.providers.deepseek import DeepSeekProvider
from lkthink_agent.tools.adapters.agno import AgnoToolAdapter
from lkthink_agent.vectorstores.pgvector import PgVectorStore


def main():
    print("Validando imports públicos e módulos...")

    print("API pública: OK")
    print("Knowledge: OK")
    print("Memory: OK")
    print("MCP: OK")
    print("Observability: OK")
    print("Providers: OK")
    print("Tools: OK")
    print("VectorStore: OK")

    database_url = os.environ["DATABASE_URL"]

    print("\nValidando conexão PostgreSQL...")

    engine = create_engine(database_url)

    with engine.begin() as connection:
        connection.execute(text("SELECT 1"))

        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        version = connection.execute(
            text("SELECT version()")
        ).scalar_one()

        vector_version = connection.execute(
            text(
                "SELECT extversion FROM pg_extension "
                "WHERE extname = 'vector'"
            )
        ).scalar_one()

    print("PostgreSQL: OK")
    print(f"pgvector: {vector_version}")
    print(f"Banco: {version.split(',')[0]}")

    print("\nValidando exporter PostgreSQL...")

    identificador = str(uuid.uuid4())
    mensagem = f"LKThink persistence test {identificador}"

    config = ObservabilityConfig(
        service_name="lkthink-smoke-test",
        environment="test",
        console_enabled=False,
        json_enabled=False,
        postgres_enabled=True,
        postgres_url=database_url,
    )

    logger = EventLogger(config=config)

    try:
        evento = logger.info(
            EventName.AGENT_RUN_STARTED,
            mensagem,
            component="smoke_test",
            operation="postgres_persistence",
            status="success",
            metadata={
                "test_id": identificador,
                "provider": "deepseek",
                "validation": True,
            },
        )

        print("Evento emitido pelo EventLogger: OK")

    finally:
        if logger.postgres_exporter is not None:
            logger.postgres_exporter.close()

    print("\nConsultando evento persistido...")

    with engine.connect() as connection:
        registro = connection.execute(
            text("""
                SELECT
                    id,
                    event,
                    message,
                    component,
                    operation,
                    status,
                    metadata,
                    payload
                FROM lkthink_agent_events
                WHERE message = :message
                ORDER BY id DESC
                LIMIT 1
            """),
            {"message": mensagem},
        ).mappings().first()

    assert registro is not None, (
        "O evento não foi encontrado no PostgreSQL."
    )

    assert registro["message"] == mensagem
    assert registro["component"] == "smoke_test"
    assert registro["operation"] == "postgres_persistence"
    assert registro["metadata"]["test_id"] == identificador
    assert registro["payload"]["metadata"]["validation"] is True

    print(f"Registro ID: {registro['id']}")
    print(f"Evento: {registro['event']}")
    print(f"Mensagem: {registro['message']}")
    print("Metadata JSONB: OK")
    print("Payload JSONB: OK")
    print("Persistência real: OK")

    engine.dispose()

    print("\nVALIDAÇÃO DO LKTHINK AGENT CONCLUÍDA")


if __name__ == "__main__":
    main()
