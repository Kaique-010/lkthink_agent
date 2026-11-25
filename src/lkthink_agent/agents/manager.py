
from __future__ import annotations

from typing import TYPE_CHECKING

from lkthink_agent.agents.agent import LKThinkAgent

if TYPE_CHECKING:
    from lkthink_agent.execution.runtime import AgentResult, AgentRuntime


class AgentManager:
    """Gerencia o registro e a execução de agentes."""

    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        if runtime is None:
            from lkthink_agent.execution.runtime import AgentRuntime

            runtime = AgentRuntime()

        self.runtime = runtime
        self._agents: dict[str, LKThinkAgent] = {}
        self._aliases: dict[str, str] = {}

    def register(self, agent: LKThinkAgent) -> LKThinkAgent:
        if not isinstance(agent, LKThinkAgent):
            raise TypeError("O agente precisa ser uma instância de LKThinkAgent.")

        identity = agent.identity
        agent_id = identity.id
        slug = identity.slug

        if not agent_id or not slug:
            raise ValueError("O agente precisa ter ID e slug válidos.")

        if agent_id in self._agents or agent_id in self._aliases:
            raise ValueError(f"Já existe um agente registrado com ID '{agent_id}'.")

        if slug in self._agents or slug in self._aliases:
            raise ValueError(f"Já existe um agente registrado com slug '{slug}'.")

        self._agents[agent_id] = agent
        self._aliases[slug] = agent_id

        return agent

    def get(self, identifier: str) -> LKThinkAgent:
        if not identifier:
            raise ValueError("Informe o ID ou slug do agente.")

        agent_id = self._aliases.get(identifier, identifier)
        agent = self._agents.get(agent_id)

        if agent is None:
            raise KeyError(f"Agente '{identifier}' não encontrado.")

        return agent

    def remove(self, identifier: str) -> LKThinkAgent:
        agent = self.get(identifier)
        identity = agent.identity

        del self._agents[identity.id]
        self._aliases.pop(identity.slug, None)

        return agent

    def list_agents(self) -> tuple[LKThinkAgent, ...]:
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
        return await self.runtime.executar(
            self.get(agent_id),
            prompt,
            user_id=user_id,
            session_id=session_id,
            tenant_id=tenant_id,
        )

    def exists(self, identifier: str) -> bool:
        return identifier in self._agents or identifier in self._aliases

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, identifier: str) -> bool:
        return self.exists(identifier)
