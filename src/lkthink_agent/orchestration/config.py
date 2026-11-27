
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ExecutionMode = Literal["sequential", "parallel"]


@dataclass(frozen=True, slots=True)
class TeamStageConfig:
    """Define uma etapa de execução de uma equipe."""

    name: str
    agent_ids: tuple[str, ...]
    mode: ExecutionMode = "sequential"
    max_concurrency: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("O nome da etapa não pode ser vazio.")

        if self.mode not in ("sequential", "parallel"):
            raise ValueError("Modo de execução inválido.")

        agent_ids = tuple(self.agent_ids)

        if not agent_ids:
            raise ValueError("A etapa precisa ter pelo menos um agente.")

        if any(
            not isinstance(agent_id, str) or not agent_id.strip()
            for agent_id in agent_ids
        ):
            raise ValueError("Todos os IDs dos agentes devem ser válidos.")

        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("A etapa não pode repetir agentes.")

        if self.max_concurrency is not None and self.max_concurrency < 1:
            raise ValueError("max_concurrency deve ser maior que zero.")

        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "agent_ids", agent_ids)


@dataclass(frozen=True, slots=True)
class TeamConfig:
    """Configuração declarativa de uma equipe de agentes."""

    id: str
    name: str
    stages: tuple[TeamStageConfig, ...]
    fail_fast: bool = True
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("O ID da equipe não pode ser vazio.")

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("O nome da equipe não pode ser vazio.")

        stages = tuple(self.stages)

        if not stages:
            raise ValueError("A equipe precisa ter pelo menos uma etapa.")

        if not all(isinstance(stage, TeamStageConfig) for stage in stages):
            raise TypeError("Todas as etapas devem ser TeamStageConfig.")

        names = [stage.name for stage in stages]

        if len(names) != len(set(names)):
            raise ValueError("Os nomes das etapas devem ser únicos.")

        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "stages", stages)
        object.__setattr__(self, "metadata", dict(self.metadata))
