
from __future__ import annotations

from time import perf_counter
from typing import Any

from lkthink_agent.observability.events import EventName, LogLevel
from lkthink_agent.orchestration.aggregator import TeamAggregator
from lkthink_agent.orchestration.config import TeamConfig
from lkthink_agent.orchestration.context import TeamExecutionContext
from lkthink_agent.orchestration.executors.parallel import ParallelExecutor
from lkthink_agent.orchestration.executors.sequential import SequentialExecutor


class TeamOrchestrator:
    """Coordena equipes, etapas e execução dos agentes."""

    def __init__(
        self,
        manager: Any,
        *,
        aggregator: TeamAggregator | None = None,
    ) -> None:
        if manager is None or not callable(
            getattr(manager, "execute", None)
        ):
            raise TypeError("Informe um AgentManager válido.")

        runtime = getattr(manager, "runtime", None)
        tracer = getattr(runtime, "tracer", None)
        logger = getattr(runtime, "logger", None)

        if tracer is None or logger is None:
            raise ValueError(
                "O AgentManager precisa possuir Runtime com Tracer e Logger."
            )

        self.manager = manager
        self.aggregator = aggregator or TeamAggregator()
        self.tracer = tracer
        self.logger = logger

        self._executors = {
            "sequential": SequentialExecutor(),
            "parallel": ParallelExecutor(),
        }

    async def executar(
        self,
        config: TeamConfig,
        prompt: str,
        *,
        tenant_id: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> TeamExecutionContext:
        """Executa todas as etapas configuradas para uma equipe."""

        if not isinstance(config, TeamConfig):
            raise TypeError("config precisa ser TeamConfig.")

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("O prompt não pode ser vazio.")

        # Valida todos os agentes antes de iniciar a execução.
        for stage in config.stages:
            for agent_id in stage.agent_ids:
                if not self.manager.exists(agent_id):
                    raise KeyError(
                        f"Agente '{agent_id}' não encontrado "
                        f"na equipe '{config.id}'."
                    )

        context = TeamExecutionContext(
            team_id=config.id,
            team_name=config.name,
            prompt=prompt.strip(),
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            metadata=dict(config.metadata),
        )

        inicio = perf_counter()

        metadata = {
            "team_id": config.id,
            "team_run_id": context.team_run_id,
            "stages_count": len(config.stages),
        }

        self.logger.emit(
            event=EventName.ORCHESTRATOR_RUN_STARTED,
            message="Execução da equipe iniciada.",
            component="orchestrator",
            operation="execute",
            status="started",
            metadata=metadata,
        )

        try:
            with self.tracer.span(
                "orchestrator",
                "team.execute",
                metadata=metadata,
            ):
                for indice, stage in enumerate(config.stages):
                    # A primeira etapa recebe o prompt original.
                    # As seguintes recebem o contexto consolidado.
                    if indice == 0:
                        context.stage_prompt = context.prompt
                    else:
                        context.stage_prompt = self.aggregator.agregar(
                            context,
                        )

                    executor = self._executors[stage.mode]

                    await executor.executar(
                        self.manager,
                        stage,
                        context,
                        fail_fast=config.fail_fast,
                    )

            duration_ms = (perf_counter() - inicio) * 1000

            self.logger.emit(
                event=EventName.ORCHESTRATOR_RUN_COMPLETED,
                message="Execução da equipe concluída.",
                component="orchestrator",
                operation="execute",
                status="completed",
                duration_ms=duration_ms,
                metadata={
                    **metadata,
                    "total_results": context.total_resultados,
                    "total_failures": context.total_falhas,
                },
            )

            return context

        except Exception as erro:
            duration_ms = (perf_counter() - inicio) * 1000

            self.logger.emit(
                event=EventName.ORCHESTRATOR_RUN_FAILED,
                message="Falha na execução da equipe.",
                level=LogLevel.ERROR,
                component="orchestrator",
                operation="execute",
                status="failed",
                duration_ms=duration_ms,
                metadata={
                    **metadata,
                    "total_results": context.total_resultados,
                    "total_failures": context.total_falhas,
                },
                error=erro,
            )

            raise
