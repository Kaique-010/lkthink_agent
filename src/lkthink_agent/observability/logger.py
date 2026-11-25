from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.events import (
    EventName,
    LogEvent,
    LogLevel,
    criar_evento,
)
from lkthink_agent.observability.exporters.console import ConsoleExporter
from lkthink_agent.observability.exporters.postgres import PostgresExporter
from lkthink_agent.observability.sanitization import sanitizar_valor


class EventLogger:
    """
    Logger central do LKThink Agent.

    Responsabilidades:
    - Criar eventos padronizados.
    - Capturar contexto da execução.
    - Sanitizar dados sensíveis.
    - Exportar logs para console e JSONL.
    """

    def __init__(
        self,
        config: ObservabilityConfig | None = None,
        console_exporter: ConsoleExporter | None = None,
        json_file: str | Path | None = None,
        postgres_exporter: PostgresExporter | None = None,
    ):
        self.config = config or ObservabilityConfig()

        if console_exporter is None and self.config.console_enabled:
            from lkthink_agent.observability.exporters.console import (
                ConsoleExporter,
            )

        if postgres_exporter is None and self.config.postgres_enabled:
            from lkthink_agent.observability.exporters.postgres import (
                PostgresExporter,
            )
            postgres_exporter = PostgresExporter(self.config)

        self.postgres_exporter = postgres_exporter

        if console_exporter is None and self.config.console_enabled:
            console_exporter = ConsoleExporter(self.config)

        self.console_exporter = console_exporter

        self.json_file = Path(
            json_file
            or getattr(
                self.config,
                "json_file",
                "logs/lkthink-agent.jsonl",
            )
        )

        self._lock = threading.RLock()

    def emit(
        self,
        event: EventName | str,
        message: str,
        *,
        level: LogLevel = LogLevel.INFO,
        status: str | None = None,
        component: str | None = None,
        operation: str | None = None,
        duration_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> dict[str, Any]:
        """Cria, sanitiza e distribui um evento."""

        log_event: LogEvent = criar_evento(
            event=event,
            message=message,
            level=level,
            status=status,
            component=component,
            operation=operation,
            duration_ms=duration_ms,
            metadata=metadata,
            error=error,
        )

        evento = sanitizar_valor(log_event.to_dict())

        evento["message"] = sanitizar_valor(
            message,
            limite=self.config.max_message_length,
        )

        evento["metadata"] = sanitizar_valor(
            metadata or {},
            limite=self.config.max_metadata_length,
        )

        self._exportar(evento)

        return evento

    def _exportar(self, evento: dict[str, Any]) -> None:
        """Encaminha o evento para as saídas habilitadas."""

        with self._lock:
            if self.config.console_enabled:
                self._exportar_console(evento)

            if self.config.json_enabled:
                self._exportar_json(evento)

            if (
                self.config.postgres_enabled
                and self.postgres_exporter is not None
            ):
                self.postgres_exporter.export(evento)

    def _exportar_console(self, evento: dict[str, Any]) -> None:
        """Envia o evento para o renderizador do terminal."""

        if self.console_exporter is None:
            return

        self.console_exporter.export(evento)

    def _exportar_json(self, evento: dict[str, Any]) -> None:
        """Grava o evento em formato JSON Lines."""

        self.json_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        registro = json.dumps(
            evento,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )

        with self.json_file.open(
            "a",
            encoding="utf-8",
        ) as arquivo:
            arquivo.write(registro + "\n")

    def debug(self, event: EventName | str, message: str, **kwargs):
        return self.emit(
            event,
            message,
            level=LogLevel.DEBUG,
            **kwargs,
        )

    def info(self, event: EventName | str, message: str, **kwargs):
        return self.emit(
            event,
            message,
            level=LogLevel.INFO,
            **kwargs,
        )

    def warning(self, event: EventName | str, message: str, **kwargs):
        return self.emit(
            event,
            message,
            level=LogLevel.WARNING,
            **kwargs,
        )

    def error(self, event: EventName | str, message: str, **kwargs):
        return self.emit(
            event,
            message,
            level=LogLevel.ERROR,
            **kwargs,
        )

    def critical(self, event: EventName | str, message: str, **kwargs):
        return self.emit(
            event,
            message,
            level=LogLevel.CRITICAL,
            **kwargs,
        )
