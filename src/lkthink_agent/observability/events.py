
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from lkthink_agent.observability.context import (
    ObservabilityContext,
    obter_contexto,
)


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventName(StrEnum):
    # Orquestrador
    ORCHESTRATOR_RUN_STARTED = "orchestrator.run.started"
    ORCHESTRATOR_RUN_COMPLETED = "orchestrator.run.completed"
    ORCHESTRATOR_RUN_FAILED = "orchestrator.run.failed"
    AGENT_SELECTION_COMPLETED = "agent.selection.completed"

    # Agentes
    AGENT_RUN_STARTED = "agent.run.started"
    AGENT_RUN_COMPLETED = "agent.run.completed"
    AGENT_RUN_FAILED = "agent.run.failed"

    # Runtime
    RUNTIME_EXECUTION_STARTED = "runtime.execution.started"
    RUNTIME_EXECUTION_COMPLETED = "runtime.execution.completed"
    RUNTIME_EXECUTION_FAILED = "runtime.execution.failed"

    # LLM
    LLM_REQUEST_STARTED = "llm.request.started"
    LLM_REQUEST_COMPLETED = "llm.request.completed"
    LLM_REQUEST_FAILED = "llm.request.failed"

    # Conhecimento / RAG
    RAG_RETRIEVAL_STARTED = "rag.retrieval.started"
    RAG_RETRIEVAL_COMPLETED = "rag.retrieval.completed"
    RAG_RETRIEVAL_FAILED = "rag.retrieval.failed"

    # Embeddings
    EMBEDDING_GENERATION_STARTED = "embedding.generation.started"
    EMBEDDING_GENERATION_COMPLETED = "embedding.generation.completed"
    EMBEDDING_GENERATION_FAILED = "embedding.generation.failed"

    # Ferramentas
    TOOL_CALL_STARTED = "tool.call.started"
    TOOL_CALL_COMPLETED = "tool.call.completed"
    TOOL_CALL_FAILED = "tool.call.failed"

    # MCP
    MCP_CONNECTION_STARTED = "mcp.connection.started"
    MCP_CONNECTION_COMPLETED = "mcp.connection.completed"
    MCP_CONNECTION_FAILED = "mcp.connection.failed"
    MCP_TOOL_EXECUTED = "mcp.tool.executed"

    # Memória
    MEMORY_READ_COMPLETED = "memory.read.completed"
    MEMORY_WRITE_COMPLETED = "memory.write.completed"
    MEMORY_READ_FAILED = "memory.read.failed"
    MEMORY_WRITE_FAILED = "memory.write.failed"


@dataclass(slots=True)
class LogEvent:
    timestamp: str
    level: str
    event: str
    message: str

    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None
    run_id: str | None = None

    tenant_id: str | None = None
    agent: dict[str, Any] | None = None

    component: str | None = None
    operation: str | None = None
    status: str | None = None

    duration_ms: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Converte o evento para um dicionário serializável."""
        return asdict(self)


def criar_evento(
    *,
    event: EventName | str,
    message: str,
    level: LogLevel = LogLevel.INFO,
    status: str | None = None,
    context: ObservabilityContext | None = None,
    component: str | None = None,
    operation: str | None = None,
    duration_ms: float | None = None,
    metadata: dict[str, Any] | None = None,
    error: Exception | None = None,
) -> LogEvent:
    """Cria um evento padronizado usando o contexto atual."""

    contexto = context or obter_contexto()

    agent_data = None

    if contexto and contexto.agent:
        agent_data = {
            "id": contexto.agent.id,
            "slug": contexto.agent.slug,
            "name": contexto.agent.name,
            "label": contexto.agent.label,
            "color": contexto.agent.color,
        }

    error_data = None

    if error is not None:
        error_data = {
            "type": type(error).__name__,
            "message": str(error),
        }

    return LogEvent(
        timestamp=datetime.now(UTC).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z"),
        level=level.value,
        event=event.value if isinstance(event, EventName) else event,
        message=message,

        trace_id=contexto.trace_id if contexto else None,
        span_id=contexto.span_id if contexto else None,
        parent_span_id=contexto.parent_span_id if contexto else None,
        run_id=contexto.run_id if contexto else None,

        tenant_id=contexto.tenant_id if contexto else None,
        agent=agent_data,

        component=component or (
            contexto.component if contexto else None
        ),
        operation=operation or (
            contexto.operation if contexto else None
        ),
        status=status,
        duration_ms=duration_ms,

        metadata=metadata or {},
        error=error_data,
    )
