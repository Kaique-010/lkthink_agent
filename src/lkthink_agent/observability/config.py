
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


def _cores_agentes() -> Mapping[str, str]:
    return MappingProxyType({
        "AGENT-01": "blue",
        "AGENT-02": "green",
        "AGENT-03": "yellow",
    })


def _cores_componentes() -> Mapping[str, str]:
    return MappingProxyType({
        "orchestrator": "magenta",
        "runtime": "cyan",
        "knowledge": "purple",
        "rag": "purple",
        "memory": "bright_blue",
        "tools": "orange",
        "mcp": "white",
        "llm": "bright_cyan",
        "embedding": "bright_magenta",
        "error": "red",
    })


def _cores_niveis() -> Mapping[str, str]:
    return MappingProxyType({
        "DEBUG": "gray",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bright_red",
    })


@dataclass(frozen=True, slots=True)
class ObservabilityConfig:
    # Identificação da aplicação
    service_name: str = "lkthink-agent"
    environment: str = "development"
    version: str = "0.1.0"

    # Saídas
    console_enabled: bool = True
    json_enabled: bool = True
    postgres_enabled: bool = False
    postgres_url: str | None = None
    json_file: str = "logs/lkthink-agent.jsonl"

    # Formato e apresentação
    console_colors: bool = True
    console_human_messages: bool = True
    console_force_colors: bool = True
    json_pretty: bool = False

    # Controle de volume
    log_level: str = "INFO"
    max_message_length: int = 12_000
    max_metadata_length: int = 12_000

    # Identidade visual dos agentes
    agent_colors: Mapping[str, str] = field(
        default_factory=_cores_agentes
    )

    # Identidade visual dos componentes
    component_colors: Mapping[str, str] = field(
        default_factory=_cores_componentes
    )

    # Identidade visual por nível
    level_colors: Mapping[str, str] = field(
        default_factory=_cores_niveis
    )

    def __post_init__(self) -> None:
        niveis_validos = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        nivel = self.log_level.upper()

        if nivel not in niveis_validos:
            raise ValueError(
                f"Nível de log inválido: {self.log_level}"
            )

        object.__setattr__(self, "log_level", nivel)

        if self.max_message_length <= 0:
            raise ValueError(
                "max_message_length deve ser maior que zero."
            )

        if self.max_metadata_length <= 0:
            raise ValueError(
                "max_metadata_length deve ser maior que zero."
            )

        if self.postgres_enabled and not self.postgres_url:
            raise ValueError(
                "postgres_url é obrigatória quando "
                "postgres_enabled=True."
            )

        # Protege também configurações fornecidas externamente.
        object.__setattr__(
            self,
            "agent_colors",
            MappingProxyType(dict(self.agent_colors)),
        )
        object.__setattr__(
            self,
            "component_colors",
            MappingProxyType(dict(self.component_colors)),
        )
        object.__setattr__(
            self,
            "level_colors",
            MappingProxyType(dict(self.level_colors)),
        )

    def obter_cor_agente(self, label: str) -> str:
        return self.agent_colors.get(label, "white")

    def obter_cor_componente(self, component: str) -> str:
        return self.component_colors.get(component, "white")

    def obter_cor_nivel(self, level: str) -> str:
        return self.level_colors.get(level.upper(), "white")
