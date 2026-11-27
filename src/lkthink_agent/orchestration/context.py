
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class TeamAgentFailure:
    """Representa a falha de um agente durante a execução da equipe."""

    stage_name: str
    agent_id: str
    error_type: str
    message: str


@dataclass(slots=True)
class TeamExecutionContext:
    """
    Contexto compartilhado durante uma execução de equipe.

    Mantém os resultados e falhas de cada etapa sem compartilhar
    estado entre execuções diferentes.
    """

    team_id: str
    team_name: str
    prompt: str

    tenant_id: str | None = None
    user_id: str | None = None
    session_id: str | None = None

    team_run_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    stage_prompt: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    stage_results: dict[str, list[Any]] = field(default_factory=dict)
    failures: list[TeamAgentFailure] = field(default_factory=list)

    def __post_init__(self) -> None:
        for field_name in ("team_id", "team_name", "prompt"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} não pode ser vazio."
                )

            setattr(self, field_name, value.strip())

        if not self.team_run_id.strip():
            raise ValueError("team_run_id não pode ser vazio.")

        self.metadata = dict(self.metadata)

    def registrar_resultado(
        self,
        stage_name: str,
        resultado: Any,
    ) -> None:
        """Registra o resultado de um agente em determinada etapa."""

        if not stage_name or not stage_name.strip():
            raise ValueError("O nome da etapa não pode ser vazio.")

        if not hasattr(resultado, "agent_id"):
            raise TypeError(
                "O resultado precisa possuir agent_id."
            )

        self.stage_results.setdefault(
            stage_name,
            [],
        ).append(resultado)

    def registrar_falha(
        self,
        stage_name: str,
        agent_id: str,
        erro: Exception,
    ) -> None:
        """Registra uma falha sem interromper o registro das demais."""

        if not stage_name or not stage_name.strip():
            raise ValueError("O nome da etapa não pode ser vazio.")

        if not agent_id or not agent_id.strip():
            raise ValueError("O ID do agente não pode ser vazio.")

        if not isinstance(erro, Exception):
            raise TypeError("A falha precisa ser uma Exception.")

        self.failures.append(
            TeamAgentFailure(
                stage_name=stage_name.strip(),
                agent_id=agent_id.strip(),
                error_type=type(erro).__name__,
                message=str(erro),
            )
        )

    def obter_resultados_etapa(
        self,
        stage_name: str,
    ) -> tuple[Any, ...]:
        """Retorna os resultados de uma etapa sem expor a lista interna."""

        return tuple(self.stage_results.get(stage_name, []))

    def obter_todos_resultados(self) -> tuple[Any, ...]:
        """Retorna todos os resultados na ordem de registro."""

        return tuple(
            resultado
            for resultados in self.stage_results.values()
            for resultado in resultados
        )

    @property
    def total_resultados(self) -> int:
        return sum(
            len(resultados)
            for resultados in self.stage_results.values()
        )

    @property
    def total_falhas(self) -> int:
        return len(self.failures)

    @property
    def execution_prompt(self) -> str:
        """Retorna o prompt específico da etapa ou o original."""
        return self.stage_prompt or self.prompt