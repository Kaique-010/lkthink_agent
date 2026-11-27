
from __future__ import annotations

from typing import Any

from lkthink_agent.orchestration.config import TeamStageConfig
from lkthink_agent.orchestration.context import TeamExecutionContext


class SequentialExecutor:
    """Executa agentes sequencialmente, respeitando a ordem configurada."""

    async def executar(
        self,
        manager: Any,
        stage: TeamStageConfig,
        context: TeamExecutionContext,
        *,
        fail_fast: bool = True,
    ) -> list[Any]:
        resultados = []

        for agent_id in stage.agent_ids:
            try:
                resultado = await manager.execute(
                    agent_id,
                    context.execution_prompt,
                    user_id=context.user_id,
                    session_id=context.session_id,
                    tenant_id=context.tenant_id,
                )

            except Exception as erro:
                context.registrar_falha(
                    stage.name,
                    agent_id,
                    erro,
                )

                if fail_fast:
                    raise

                continue

            context.registrar_resultado(
                stage.name,
                resultado,
            )

            resultados.append(resultado)

        return resultados
