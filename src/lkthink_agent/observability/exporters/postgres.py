
from __future__ import annotations

import json
import threading
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class PostgresExporter:
    """
    Exportador de eventos de observabilidade para PostgreSQL.
    """

    TABLE_NAME = "lkthink_agent_events"

    def __init__(
        self,
        database_url: str,
        *,
        engine: Engine | None = None,
        fail_silently: bool = True,
    ) -> None:
        if not database_url and engine is None:
            raise ValueError(
                "Informe database_url ou uma instância de Engine."
            )

        self.engine = engine or create_engine(
            database_url,
            pool_pre_ping=True,
        )

        self.fail_silently = fail_silently
        self._lock = threading.RLock()
        self._initialized = False

    def initialize(self) -> None:
        """Cria a estrutura de persistência, caso ainda não exista."""

        comandos = (
            """
            CREATE TABLE IF NOT EXISTS lkthink_agent_events (
                id BIGSERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                level VARCHAR(20),
                event VARCHAR(150) NOT NULL,
                message TEXT,
                trace_id VARCHAR(100),
                run_id VARCHAR(100),
                span_id VARCHAR(100),
                parent_span_id VARCHAR(100),
                tenant_id VARCHAR(150),
                agent_id VARCHAR(150),
                agent_name VARCHAR(255),
                component VARCHAR(100),
                operation VARCHAR(150),
                status VARCHAR(50),
                duration_ms DOUBLE PRECISION,
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                error JSONB,
                payload JSONB NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_lkthink_events_trace
            ON lkthink_agent_events (trace_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_lkthink_events_run
            ON lkthink_agent_events (run_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_lkthink_events_agent
            ON lkthink_agent_events (agent_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_lkthink_events_timestamp
            ON lkthink_agent_events (timestamp DESC)
            """,
        )

        with self._lock, self.engine.begin() as connection:
            for comando in comandos:
                connection.execute(text(comando))

        self._initialized = True

    @staticmethod
    def _serializar(valor: Any) -> str:
        return json.dumps(
            valor,
            ensure_ascii=False,
            default=str,
        )

    def export(self, evento: dict[str, Any]) -> None:
        if not self._initialized:
            raise RuntimeError(
                "PostgresExporter não foi inicializado."
            )

        agent = evento.get("agent") or {}
        error = evento.get("error")

        sql = text(
            """
            INSERT INTO lkthink_agent_events (
                timestamp,
                level,
                event,
                message,
                trace_id,
                run_id,
                span_id,
                parent_span_id,
                tenant_id,
                agent_id,
                agent_name,
                component,
                operation,
                status,
                duration_ms,
                metadata,
                error,
                payload
            )
            VALUES (
                CAST(:timestamp AS TIMESTAMPTZ),
                :level,
                :event,
                :message,
                :trace_id,
                :run_id,
                :span_id,
                :parent_span_id,
                :tenant_id,
                :agent_id,
                :agent_name,
                :component,
                :operation,
                :status,
                :duration_ms,
                CAST(:metadata AS JSONB),
                CAST(:error AS JSONB),
                CAST(:payload AS JSONB)
            )
            """
        )

        parametros = {
            "timestamp": evento.get("timestamp"),
            "level": evento.get("level"),
            "event": evento.get("event") or "unknown",
            "message": evento.get("message"),
            "trace_id": evento.get("trace_id"),
            "run_id": evento.get("run_id"),
            "span_id": evento.get("span_id"),
            "parent_span_id": evento.get("parent_span_id"),
            "tenant_id": evento.get("tenant_id"),
            "agent_id": agent.get("id") or evento.get("agent_id"),
            "agent_name": agent.get("name") or evento.get("agent_name"),
            "component": evento.get("component"),
            "operation": evento.get("operation"),
            "status": evento.get("status"),
            "duration_ms": evento.get("duration_ms"),
            "metadata": self._serializar(evento.get("metadata") or {}),
            "error": self._serializar(error) if error else None,
            "payload": self._serializar(evento),
        }

        try:
            with self._lock, self.engine.begin() as connection:
                connection.execute(sql, parametros)
        except Exception:
            if not self.fail_silently:
                raise

    def close(self) -> None:
        self.engine.dispose()
