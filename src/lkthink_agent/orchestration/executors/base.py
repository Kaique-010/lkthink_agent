
from __future__ import annotations

from typing import Any, Protocol

from lkthink_agent.orchestration.config import TeamStageConfig
from lkthink_agent.orchestration.context import TeamExecutionContext


class BaseExecutor(Protocol):
    """Contrato dos executores de etapas de uma equipe."""

    async def executar(
        self,
        manager: Any,
        stage: TeamStageConfig,
        context: TeamExecutionContext,
        *,
        fail_fast: bool = True,
    ) -> list[Any]:
        """Executa os agentes de uma etapa."""
        ...
