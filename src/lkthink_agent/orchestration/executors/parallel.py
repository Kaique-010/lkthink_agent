
from __future__ import annotations

import asyncio
from typing import Any

from lkthink_agent.orchestration.config import TeamStageConfig
from lkthink_agent.orchestration.context import TeamExecutionContext


class ParallelExecutor:
    """Executa agentes simultaneamente com limite de concorrência."""

    async def executar(
        self,
        manager: Any,
        stage: TeamStageConfig,
        context: TeamExecutionContext,
        *,
        fail_fast: bool = True,
    ) -> list[Any]:
        limite = stage.max_concurrency or len(stage.agent_ids)
        semaphore = asyncio.Semaphore(limite)

        async def executar_agente(agent_id: str) -> Any:
            async with semaphore:
                return await manager.execute(
                    agent_id,
                    context.execution_prompt,
                    user_id=context.user_id,
                    session_id=context.session_id,
                    tenant_id=context.tenant_id,
                )

        tarefas = [
            executar_agente(agent_id)
            for agent_id in stage.agent_ids
        ]

        resultados_brutos = await asyncio.gather(
            *tarefas,
            return_exceptions=True,
        )

        resultados = []
        primeira_falha = None

        # gather preserva a ordem original dos agentes.
        for agent_id, resultado in zip(
            stage.agent_ids,
            resultados_brutos,
            strict=True,
        ):
            if isinstance(resultado, BaseException):
                if isinstance(resultado, asyncio.CancelledError):
                    raise resultado

                context.registrar_falha(
                    stage.name,
                    agent_id,
                    resultado,
                )

                if primeira_falha is None:
                    primeira_falha = resultado

                continue

            context.registrar_resultado(
                stage.name,
                resultado,
            )

            resultados.append(resultado)

        if fail_fast and primeira_falha is not None:
            raise primeira_falha

        return resultados
