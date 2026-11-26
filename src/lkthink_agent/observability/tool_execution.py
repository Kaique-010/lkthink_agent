
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from lkthink_agent.observability.events import EventName
from lkthink_agent.observability.logger import EventLogger
from lkthink_agent.observability.tracing import Tracer


@dataclass(frozen=True, slots=True)
class ToolExecutionObserver:
    agent_id: str
    logger: EventLogger
    tracer: Tracer
    metrics: Any


_observador_atual: ContextVar[ToolExecutionObserver | None] = ContextVar(
    "lkthink_tool_execution_observer",
    default=None,
)


def obter_observador() -> ToolExecutionObserver | None:
    return _observador_atual.get()


def definir_observador(
    observador: ToolExecutionObserver,
) -> Token:
    return _observador_atual.set(observador)


def limpar_observador(token: Token) -> None:
    _observador_atual.reset(token)


def _registrar_metricas(
    observador: ToolExecutionObserver,
    nome: str,
    duracao_ms: float,
    *,
    sucesso: bool,
) -> None:
    labels = {
        "agent_id": observador.agent_id,
        "tool_name": nome,
    }

    if sucesso:
        observador.metrics.increment(
            "tool.calls.total",
            labels=labels,
        )
    else:
        observador.metrics.increment(
            "tool.calls.failures",
            labels=labels,
        )

    observador.metrics.observe(
        "tool.call.duration_ms",
        duracao_ms,
        labels=labels,
    )


@contextmanager
def observar_ferramenta(
    observador: ToolExecutionObserver,
    nome: str,
) -> Iterator[None]:
    metadata = {
        "tool_name": nome,
        "agent_id": observador.agent_id,
    }

    inicio = perf_counter()

    with observador.tracer.span(
        component="tool",
        operation="call",
        metadata=metadata,
    ):

        observador.logger.info(
            EventName.TOOL_CALL_STARTED,
            message=f"Ferramenta '{nome}' iniciou a execução.",
            status="started",
            component="tool",
            operation="call",
            metadata=metadata,
        )

        try:
            yield

        except BaseException as erro:
            duracao_ms = (perf_counter() - inicio) * 1000

            _registrar_metricas(
                observador,
                nome,
                duracao_ms,
                sucesso=False,
            )

            observador.logger.error(
                EventName.TOOL_CALL_FAILED,
                message=f"Falha na execução da ferramenta '{nome}'.",
                status="failed",
                component="tool",
                operation="call",
                duration_ms=duracao_ms,
                error=erro if isinstance(erro, Exception) else None,
                metadata={
                    **metadata,
                    "error_type": type(erro).__name__,
                },
            )

            raise

        else:
            duracao_ms = (perf_counter() - inicio) * 1000

            _registrar_metricas(
                observador,
                nome,
                duracao_ms,
                sucesso=True,
            )

            observador.logger.info(
                EventName.TOOL_CALL_COMPLETED,
                message=f"Ferramenta '{nome}' concluiu a execução.",
                status="completed",
                component="tool",
                operation="call",
                duration_ms=duracao_ms,
                metadata=metadata,
            )
