
from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from uuid import uuid4


def gerar_id() -> str:
    """Gera um identificador único."""
    return str(uuid4())


@dataclass(frozen=True, slots=True)
class AgentIdentity:
    id: str
    slug: str
    name: str
    label: str
    color: str


@dataclass(frozen=True, slots=True)
class ObservabilityContext:
    trace_id: str = field(default_factory=gerar_id)
    run_id: str = field(default_factory=gerar_id)
    span_id: str = field(default_factory=gerar_id)
    parent_span_id: str | None = None

    tenant_id: str | None = None
    agent: AgentIdentity | None = None

    component: str = "runtime"
    operation: str = "execution"

    metadata: dict = field(default_factory=dict)

    def criar_span(
        self,
        component: str,
        operation: str,
        metadata: dict | None = None,
    ) -> ObservabilityContext:
        """Cria um novo span mantendo o mesmo trace e execução."""

        return ObservabilityContext(
            trace_id=self.trace_id,
            run_id=self.run_id,
            span_id=gerar_id(),
            parent_span_id=self.span_id,
            tenant_id=self.tenant_id,
            agent=self.agent,
            component=component,
            operation=operation,
            metadata={
                **self.metadata,
                **(metadata or {}),
            },
        )


_contexto_atual: ContextVar[ObservabilityContext | None] = ContextVar(
    "lkthink_observability_context",
    default=None,
)


def obter_contexto() -> ObservabilityContext | None:
    """Retorna o contexto da execução atual."""
    return _contexto_atual.get()


def definir_contexto(
    contexto: ObservabilityContext,
) -> Token:
    """Define o contexto da execução atual."""
    return _contexto_atual.set(contexto)


def limpar_contexto(token: Token) -> None:
    """Restaura o contexto anterior."""
    _contexto_atual.reset(token)


def criar_contexto_execucao(
    *,
    tenant_id: str | None = None,
    agent: AgentIdentity | None = None,
    metadata: dict | None = None,
) -> ObservabilityContext:
    """Cria o contexto inicial de uma execução."""

    return ObservabilityContext(
        tenant_id=tenant_id,
        agent=agent,
        metadata=metadata or {},
    )
