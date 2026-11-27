
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from lkthink_agent.agents.abstractions import AgentProtocol

if TYPE_CHECKING:
    from lkthink_agent.execution.runtime import AgentResult, AgentRuntime


class AgentManager:
    """Gerencia registro, execução e ciclo de vida dos agentes."""

    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        if runtime is None:
            from lkthink_agent.execution.runtime import AgentRuntime

            runtime = AgentRuntime()

        self.runtime = runtime
        self._agents: dict[str, AgentProtocol] = {}
        self._aliases: dict[str, str] = {}

    def register(self, agent: AgentProtocol) -> AgentProtocol:
        if not hasattr(agent, "identity"):
            raise TypeError(
                "O agente precisa possuir uma identidade válida."
            )

        if not callable(getattr(agent, "executar", None)):
            raise TypeError(
                "O agente precisa implementar executar()."
            )

        if not callable(getattr(agent, "close", None)):
            raise TypeError(
                "O agente precisa implementar close()."
            )

        identity = agent.identity
        agent_id = identity.id
        slug = identity.slug

        if not isinstance(agent_id, str) or not isinstance(slug, str):
            raise TypeError(
                "O ID e o slug do agente precisam ser strings."
            )

        if not agent_id.strip() or not slug.strip():
            raise ValueError(
                "O agente precisa ter ID e slug válidos."
            )

        if agent_id != agent_id.strip() or slug != slug.strip():
            raise ValueError(
                "O ID e o slug precisam estar normalizados, sem "
                "espaços nas extremidades."
            )

        if agent_id in self._agents or agent_id in self._aliases:
            raise ValueError(
                f"Já existe um agente registrado com ID '{agent_id}'."
            )

        if slug in self._agents or slug in self._aliases:
            raise ValueError(
                f"Já existe um agente registrado com slug '{slug}'."
            )

        self._agents[agent_id] = agent
        self._aliases[slug] = agent_id

        return agent

    def get(self, identifier: str) -> AgentProtocol:
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("Informe o ID ou slug do agente.")

        identifier = identifier.strip()
        agent_id = self._aliases.get(identifier, identifier)
        agent = self._agents.get(agent_id)

        if agent is None:
            raise KeyError(f"Agente '{identifier}' não encontrado.")

        return agent

    def remove(self, identifier: str) -> AgentProtocol:
        """
        Remove o agente do registro sem encerrar seus recursos.

        O agente retornado continua sob responsabilidade do chamador.
        Para remover e fechar conexões, utilize remove_and_close().
        """
        agent = self.get(identifier)
        identity = agent.identity

        del self._agents[identity.id]
        self._aliases.pop(identity.slug, None)

        return agent

    async def remove_and_close(
        self,
        identifier: str,
    ) -> AgentProtocol:
        """Fecha os recursos do agente e depois o remove do registro."""
        agent = self.get(identifier)

        await agent.close()

        self.remove(identifier)

        return agent

    async def close_all(self) -> None:
        """
        Fecha todos os agentes registrados.

        Todos os encerramentos são tentados, mesmo quando algum falha.
        O registro é esvaziado antes do encerramento.
        """
        agents = self.list_agents()

        self._agents.clear()
        self._aliases.clear()

        if not agents:
            return

        results = await asyncio.gather(
            *(agent.close() for agent in agents),
            return_exceptions=True,
        )

        errors = [
            result
            for result in results
            if isinstance(result, BaseException)
        ]

        if errors:
            raise BaseExceptionGroup(
                "Falha ao encerrar um ou mais agentes.",
                errors,
            )

    def list_agents(self) -> tuple[AgentProtocol, ...]:
        return tuple(self._agents.values())

    async def execute(
        self,
        agent_id: str,
        prompt: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        tenant_id: str | None = None,
    ) -> AgentResult:
        """Executa um agente identificado por ID ou slug."""
        return await self.runtime.executar(
            self.get(agent_id),
            prompt,
            user_id=user_id,
            session_id=session_id,
            tenant_id=tenant_id,
        )

    def exists(self, identifier: str) -> bool:
        if not isinstance(identifier, str) or not identifier.strip():
            return False

        identifier = identifier.strip()

        return (
            identifier in self._agents
            or identifier in self._aliases
        )

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, identifier: str) -> bool:
        return self.exists(identifier)
