from __future__ import annotations

import sys
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

    def __init__(
        self,
        config: ObservabilityConfig | None = None,
        stream: TextIO | None = None,
        force_color: bool | None = None,
    ):
        self.config = config or ObservabilityConfig()
        self.stream = stream or sys.stdout

        if force_color is None:
            is_terminal = getattr(self.stream, "isatty", lambda: False)()
            self.use_colors = (
                self.config.console_colors and is_terminal
            )
        else:
            self.use_colors = (
                self.config.console_colors and force_color
            )

    def export(self, evento: dict[str, Any]) -> None:
        """Exibe um evento no terminal."""

        horario = self._formatar_horario(evento.get("timestamp"))
        identidade = self._obter_identidade(evento)
        nivel = evento.get("level", "INFO")

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
            self._colorir(
                f"[{nivel}]",
                self.config.obter_cor_nivel(nivel),
                bold=True,
            ),
            mensagem,
        ]

        detalhes = self._obter_detalhes(evento)

        if detalhes:
            partes.append(
                self._colorir(
                    " | " + " | ".join(detalhes),
                    "gray",
                )
            )

        linha = " ".join(partes)

        self.stream.write(linha + "\n")
        self.stream.flush()

    def _obter_identidade(
        self,
        evento: dict[str, Any],
    ) -> dict[str, str]:
        """Identifica quem está emitindo o evento."""

        agente = evento.get("agent")

        if agente:
            label = agente.get("label", "AGENT")
            cor = self.config.agent_colors.get(
                label,
                agente.get("color", "white"),
            )

            return {
                "label": label,
                "color": cor,
            }

        component = evento.get("component") or "system"

        label = {
            "orchestrator": "ORCHESTRATOR",
            "runtime": "RUNTIME",
            "knowledge": "KNOWLEDGE",
            "rag": "KNOWLEDGE",
            "memory": "MEMORY",
            "tools": "TOOLS",
            "mcp": "MCP",
            "llm": "LLM",
            "embedding": "EMBEDDING",
        }.get(component, component.upper())

        cor = self.config.obter_cor_componente(component)

        return {
            "label": label,
            "color": cor,
        }

    def _obter_detalhes(
        self,
        evento: dict[str, Any],
    ) -> list[str]:
        """Monta informações técnicas complementares."""

        detalhes = []

        component = evento.get("component")
        operation = evento.get("operation")
        status = evento.get("status")
        duration = evento.get("duration_ms")

        if component:
            detalhes.append(f"componente={component}")

        if operation:
            detalhes.append(f"operação={operation}")

        if status:
            detalhes.append(f"status={status}")

        if duration is not None:
            detalhes.append(f"duração={duration:.2f}ms")

        run_id = evento.get("run_id")

        if run_id:
            detalhes.append(f"run={run_id[:8]}")

        trace_id = evento.get("trace_id")

        if trace_id:
            detalhes.append(f"trace={trace_id[:8]}")

        erro = evento.get("error")

        if erro:
            tipo = erro.get("type", "Error")
            detalhes.append(f"erro={tipo}")

        return detalhes

    def _formatar_horario(self, timestamp: str | None) -> str:
        """Extrai o horário de um timestamp ISO."""

        if not timestamp:
            return "--:--:--"

        if "T" in timestamp:
            return timestamp.split("T")[-1][:8]

        return timestamp[:8]

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
