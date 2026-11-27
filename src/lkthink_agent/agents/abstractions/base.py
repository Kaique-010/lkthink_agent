
from __future__ import annotations

from typing import Any, Protocol

from lkthink_agent.observability.context import AgentIdentity


class AgentProtocol(Protocol):
    """
    Contrato estrutural para implementações de agentes.

    A compatibilidade é verificada pela tipagem estática.
    A validação em runtime fica sob responsabilidade do Manager.
    """

    identity: AgentIdentity

    async def executar(
        self,
        prompt: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> Any:
        ...

    async def close(self) -> None:
        ...
