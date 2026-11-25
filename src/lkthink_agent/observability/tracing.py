
from __future__ import annotations

from contextvars import Token
from time import perf_counter
from types import TracebackType
from typing import Any, Self

from lkthink_agent.observability.context import (
    ObservabilityContext,
    criar_contexto_execucao,
    definir_contexto,
    limpar_contexto,
    obter_contexto,
)
from lkthink_agent.observability.events import LogLevel
from lkthink_agent.observability.logger import EventLogger


class Span:
    """Representa uma operação rastreável dentro de uma execução."""

    def __init__(
        self,
        *,
        logger: EventLogger,
        component: str,
        operation: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not component or not component.strip():
            raise ValueError("O componente do span não pode ser vazio.")

        if not operation or not operation.strip():
            raise ValueError("A operação do span não pode ser vazia.")

        self.logger = logger
        self.component = component
        self.operation = operation
        self.metadata = metadata or {}

        self.context: ObservabilityContext | None = None
        self._token: Token | None = None
        self._started_at: float | None = None
        self._finished_duration_ms: float | None = None
        self._active = False

    @property
    def duration_ms(self) -> float | None:
        """Retorna a duração congelada ou atual do span."""

        if self._finished_duration_ms is not None:
            return self._finished_duration_ms

        if self._started_at is None:
            return None

        return (perf_counter() - self._started_at) * 1000

    def _iniciar(self) -> None:
        if self._active:
            raise RuntimeError("Este span já está em execução.")

        parent = obter_contexto()

        if parent is not None:
            contexto = parent.criar_span(
                component=self.component,
                operation=self.operation,
                metadata=self.metadata,
            )
        else:
            contexto_base = criar_contexto_execucao(
                metadata=self.metadata,
            )

            contexto = ObservabilityContext(
                trace_id=contexto_base.trace_id,
                run_id=contexto_base.run_id,
                span_id=contexto_base.span_id,
                parent_span_id=None,
                tenant_id=contexto_base.tenant_id,
                agent=contexto_base.agent,
                component=self.component,
                operation=self.operation,
                metadata=contexto_base.metadata,
            )

        self.context = contexto
        self._finished_duration_ms = None
        self._token = definir_contexto(contexto)
        self._started_at = perf_counter()
        self._active = True

        try:
            self.logger.emit(
                event="trace.span.started",
                message="Span iniciado.",
                level=LogLevel.INFO,
                status="started",
                component=self.component,
                operation=self.operation,
                metadata=self.metadata,
            )
        except Exception:
            self._congelar_duracao()
            self._restaurar_contexto()
            raise

    def _congelar_duracao(self) -> float:
        if self._finished_duration_ms is None:
            self._finished_duration_ms = (
                (perf_counter() - self._started_at) * 1000
                if self._started_at is not None
                else 0.0
            )

        return self._finished_duration_ms

    def _finalizar(
        self,
        error: BaseException | None = None,
    ) -> None:
        if not self._active:
            return

        duracao_ms = self._congelar_duracao()

        try:
            if error is None:
                self.logger.emit(
                    event="trace.span.completed",
                    message="Span concluído.",
                    level=LogLevel.INFO,
                    status="completed",
                    component=self.component,
                    operation=self.operation,
                    duration_ms=duracao_ms,
                )
            else:
                self.logger.emit(
                    event="trace.span.failed",
                    message="Span finalizado com erro.",
                    level=LogLevel.ERROR,
                    status="failed",
                    component=self.component,
                    operation=self.operation,
                    duration_ms=duracao_ms,
                    error=error if isinstance(error, Exception) else None,
                    metadata={
                        **self.metadata,
                        "error_type": type(error).__name__,
                    },
                )
        finally:
            self._restaurar_contexto()

    def _restaurar_contexto(self) -> None:
        if self._token is not None:
            limpar_contexto(self._token)
            self._token = None

        self._active = False

    def __enter__(self) -> Self:
        self._iniciar()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self._finalizar(exc_value)
        return False

    async def __aenter__(self) -> Self:
        self._iniciar()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self._finalizar(exc_value)
        return False


class Tracer:
    """Gerenciador de spans do LKThink Agent."""

    def __init__(self, logger: EventLogger | None = None) -> None:
        self.logger = logger or EventLogger()

    def span(
        self,
        component: str,
        operation: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Span:
        """Cria um span síncrono ou assíncrono."""

        return Span(
            logger=self.logger,
            component=component,
            operation=operation,
            metadata=metadata,
        )
