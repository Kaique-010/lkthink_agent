
from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, ClassVar, TextIO

from lkthink_agent.observability.config import ObservabilityConfig


class ConsoleExporter:
    """
    Renderiza eventos do LKThink em formato humano e colorido.

    As cores são aplicadas somente na apresentação.
    Os dados originais permanecem intactos.
    """

    CORES_ANSI: ClassVar[dict[str, str]] = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "purple": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "orange": "\033[38;5;208m",
    }

    RESET: ClassVar[str] = "\033[0m"
    BOLD: ClassVar[str] = "\033[1m"
    DIM: ClassVar[str] = "\033[2m"

    COMPONENT_LABELS: ClassVar[dict[str, str]] = {
        "orchestrator": "ORCHESTRATOR",
        "runtime": "RUNTIME",
        "knowledge": "KNOWLEDGE",
        "rag": "RAG",
        "memory": "MEMORY",
        "tools": "TOOLS",
        "mcp": "MCP",
        "llm": "LLM",
        "embedding": "EMBEDDING",
        "error": "ERROR",
    }

    def __init__(
        self,
        config: ObservabilityConfig,
        stream=None,
        force_color: bool | None = None,
    ):
        self.config = config
        self.stream = stream or sys.stdout

        if force_color is None:
            self.use_colors = (
                config.console_colors
                and hasattr(self.stream, "isatty")
                and self.stream.isatty()
            )
        else:
            self.use_colors = (
                config.console_colors and force_color
            )
    def export(self, evento: dict[str, Any]) -> None:
        """Exibe um evento no terminal."""

        horario = self._formatar_horario(
            evento.get("timestamp")
        )

        agente = evento.get("agent")
        component = evento.get("component")

        identidade = self._obter_identidade(evento)
        nivel = str(evento.get("level", "INFO")).upper()

        mensagem = (
            evento.get("message", "")
            if self.config.console_human_messages
            else evento.get("event", "")
        )

        partes = [
            self._colorir(f"[{horario}]", "gray"),
            self._colorir(
                f"[{identidade['label']}]",
                identidade["color"],
                bold=True,
            ),
        ]

        # Com agente presente, o componente ganha identificação própria.
        if isinstance(agente, dict) and component:
            label_componente = self._obter_label_componente(
                component
            )

            partes.append(
                self._colorir(
                    f"[{label_componente}]",
                    self.config.obter_cor_componente(component),
                    bold=True,
                )
            )

        partes.append(
            self._colorir(
                f"[{nivel}]",
                self.config.obter_cor_nivel(nivel),
                bold=True,
            )
        )

        partes.append(str(mensagem))

        detalhes = self._obter_detalhes(evento)

        if detalhes:
            partes.append(
                self._colorir(
                    " | " + " | ".join(detalhes),
                    "gray",
                )
            )

        self.stream.write(" ".join(partes) + "\n")
        self.stream.flush()

    def _obter_identidade(
        self,
        evento: dict[str, Any],
    ) -> dict[str, str]:
        """Identifica o agente ou componente responsável."""

        agente = evento.get("agent")

        if isinstance(agente, dict):
            label = str(agente.get("label") or "AGENT")

            return {
                "label": label,
                "color": self.config.obter_cor_agente(label),
            }

        component = str(
            evento.get("component") or "system"
        )

        return {
            "label": self._obter_label_componente(component),
            "color": self.config.obter_cor_componente(component),
        }

    def _obter_label_componente(self, component: str) -> str:
        return self.COMPONENT_LABELS.get(
            component,
            component.upper(),
        )

    def _obter_detalhes(
        self,
        evento: dict[str, Any],
    ) -> list[str]:
        """Monta informações técnicas complementares."""

        detalhes: list[str] = []

        component = evento.get("component")
        operation = evento.get("operation")
        status = evento.get("status")
        duration = evento.get("duration_ms")

        if component:
            detalhes.append(
                self._colorir(
                    f"componente={component}",
                    self.config.obter_cor_componente(component),
                )
            )

        if operation:
            detalhes.append(f"operação={operation}")

        if status:
            detalhes.append(f"status={status}")

        if duration is not None:
            try:
                detalhes.append(f"duração={float(duration):.2f}ms")
            except (TypeError, ValueError):
                detalhes.append(f"duração={duration}")

        for campo, nome in (
            ("run_id", "run"),
            ("trace_id", "trace"),
            ("span_id", "span"),
            ("parent_span_id", "parent_span"),
        ):
            identificador = evento.get(campo)

            if identificador:
                detalhes.append(
                    f"{nome}={str(identificador)[:8]}"
                )

        erro = evento.get("error")

        if isinstance(erro, dict):
            tipo = erro.get("type", "Error")

            detalhes.append(
                self._colorir(
                    f"erro={tipo}",
                    self.config.obter_cor_nivel("ERROR"),
                    bold=True,
                )
            )

        return detalhes

    def _formatar_horario(
        self,
        timestamp: str | None,
    ) -> str:
        """Extrai o horário de um timestamp ISO."""

        if not timestamp:
            return "--:--:--"

        try:
            valor = str(timestamp)

            if valor.endswith("Z"):
                valor = valor[:-1] + "+00:00"

            return datetime.fromisoformat(valor).strftime(
                "%H:%M:%S"
            )

        except (ValueError, TypeError):
            return str(timestamp)[:8]

    def _colorir(
        self,
        texto: str,
        cor: str,
        bold: bool = False,
    ) -> str:
        """Aplica cor ANSI quando habilitada."""

        if not self.use_colors:
            return texto

        codigo_cor = self.CORES_ANSI.get(
            cor,
            self.CORES_ANSI["white"],
        )

        estilo = self.BOLD if bold else ""

        return f"{estilo}{codigo_cor}{texto}{self.RESET}"
