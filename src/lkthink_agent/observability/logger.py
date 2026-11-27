
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.events import (
    EventName,
    LogEvent,
    LogLevel,
    criar_evento,
)
from lkthink_agent.observability.exporters.console import ConsoleExporter
from lkthink_agent.observability.sanitization import sanitizar_valor

if TYPE_CHECKING:
    from lkthink_agent.observability.exporters.postgres import PostgresExporter


class EventLogger:
    """
    Logger central do LKThink Agent.

    Responsabilidades:
    - Criar eventos padronizados.
    - Capturar contexto da execução.
    - Sanitizar dados sensíveis.
    - Distribuir eventos para exporters independentes.
    """

    _NIVEIS: dict[str, int] = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    def __init__(
        self,
        config: ObservabilityConfig | None = None,
        console_exporter: ConsoleExporter | None = None,
        json_file: str | Path | None = None,
        postgres_exporter: PostgresExporter | None = None,
    ) -> None:
        self.config = config or ObservabilityConfig()
        self._lock = threading.RLock()

        self.console_exporter = console_exporter
        self.postgres_exporter = postgres_exporter

        if self.console_exporter is None and self.config.console_enabled:
            self.console_exporter = ConsoleExporter(
                self.config,
                force_color=self.config.console_force_colors,
            )

        if self.postgres_exporter is None and self.config.postgres_enabled:
            self._inicializar_postgres()

        self.json_file = Path(json_file or self.config.json_file)

    def _inicializar_postgres(self) -> None:
        """Carrega o exporter PostgreSQL somente quando solicitado."""

        if not self.config.postgres_url:
            raise ValueError(
                "postgres_url é obrigatória quando "
                "postgres_enabled=True."
            )

        try:
            from lkthink_agent.observability.exporters.postgres import (
                PostgresExporter,
            )
        except ImportError as erro:
            raise ImportError(
                "O exporter PostgreSQL exige dependências adicionais. "
                "Instale com: pip install lkthink-agent[postgres]"
            ) from erro

        exporter = PostgresExporter(
            database_url=self.config.postgres_url,
        )
        exporter.initialize()
        self.postgres_exporter = exporter

    def _deve_emitir(self, level: LogLevel) -> bool:
        """Verifica se o nível do evento está habilitado."""

        nivel_evento = self._NIVEIS.get(level.value)
        nivel_configurado = self._NIVEIS[self.config.log_level]

        return (
            nivel_evento is not None
            and nivel_evento >= nivel_configurado
        )

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

        if self._deve_emitir(level):
            self._exportar(evento)

        return evento

    def _exportar(self, evento: dict[str, Any]) -> None:
        """Distribui o evento sem deixar uma saída bloquear as demais."""

        with self._lock:
            if self.config.console_enabled:
                self._executar_exporter(
                    nome="console",
                    executar=self._exportar_console,
                    evento=evento,
                )

            if self.config.json_enabled:
                self._executar_exporter(
                    nome="jsonl",
                    executar=self._exportar_json,
                    evento=evento,
                )

            if (
                self.config.postgres_enabled
                and self.postgres_exporter is not None
            ):
                self._executar_exporter(
                    nome="postgres",
                    executar=self._exportar_postgres,
                    evento=evento,
                )

    def _executar_exporter(
        self,
        *,
        nome: str,
        executar: Callable[[dict[str, Any]], None],
        evento: dict[str, Any],
    ) -> None:
        """Isola falhas individuais dos exporters."""

        try:
            executar(evento)
        except Exception as erro:
            self._reportar_falha_exporter(nome, erro)

    @staticmethod
    def _reportar_falha_exporter(
        nome: str,
        erro: Exception,
    ) -> None:
        """Reporta falhas sem utilizar o próprio EventLogger."""

        try:
            sys.stderr.write(
                f"[LKTHINK-OBSERVABILITY] "
                f"Falha no exporter {nome}: "
                f"{type(erro).__name__}: {erro}\n"
            )
            sys.stderr.flush()
        except Exception:
            pass

    def _exportar_console(self, evento: dict[str, Any]) -> None:
        if not self.config.console_enabled:
            return

        if self.console_exporter is None:
            self.console_exporter = ConsoleExporter(
                self.config,
                force_color=self.config.console_force_colors,
            )

        self.console_exporter.export(evento)

    def _exportar_json(self, evento: dict[str, Any]) -> None:
        self.json_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        registro = json.dumps(
            evento,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
            allow_nan=False,
        )

        with self.json_file.open(
            "a",
            encoding="utf-8",
            newline="\n",
        ) as arquivo:
            arquivo.write(registro + "\n")

    def _exportar_postgres(self, evento: dict[str, Any]) -> None:
        if self.postgres_exporter is not None:
            self.postgres_exporter.export(evento)

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
