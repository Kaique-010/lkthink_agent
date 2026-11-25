
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agno.agent import Agent

from lkthink_agent.agents.config import AgentConfig
from lkthink_agent.observability.context import AgentIdentity
from lkthink_agent.providers.base import BaseLLMProvider
from lkthink_agent.tools import ToolRegistry
from lkthink_agent.tools.adapters.agno import AgnoToolAdapter

if TYPE_CHECKING:
    from lkthink_agent.mcp.config import MCPServerConfig
    from lkthink_agent.mcp.manager import MCPManager


class LKThinkAgent:

    def __init__(
        self,
        config: AgentConfig,
        provider: BaseLLMProvider,
        tools: ToolRegistry | None = None,
    ):
        self.config = config

        self.identity = AgentIdentity(
            id=config.id,
            slug=config.slug,
            name=config.name,
            label=config.label,
            color=config.color,
        )

        self.tools = tools if tools is not None else ToolRegistry()
        self._mcp_manager: MCPManager | None = None

        ferramentas_agno = AgnoToolAdapter().adaptar(self.tools)

        self._engine = Agent(
            id=config.id,
            name=config.name,
            description=config.description,
            instructions=config.instructions,
            model=provider.build_model(),
            tools=ferramentas_agno or None,
            markdown=config.markdown,
            telemetry=False,
        )

    @classmethod
    async def criar_com_mcp(
        cls,
        config: AgentConfig,
        provider: BaseLLMProvider,
        *,
        mcp_servers: list[MCPServerConfig],
        allowed_tools: dict[str, list[str]],
        tools: ToolRegistry | None = None,
    ) -> LKThinkAgent:

        from lkthink_agent.mcp.manager import MCPManager

        registry = tools if tools is not None else ToolRegistry()
        manager = MCPManager()

        try:
            for server_config in mcp_servers:

                server_name = server_config.name

                if server_name not in allowed_tools:
                    raise ValueError(
                        f"Não foi definida uma lista de ferramentas "
                        f"autorizadas para o servidor '{server_name}'."
                    )

                await manager.connect_server(server_config)

                await manager.register_tools(
                    registry,
                    config=server_config,
                    allowed_tools=allowed_tools[server_name],
                )

            agente = cls(
                config=config,
                provider=provider,
                tools=registry,
            )

            agente._mcp_manager = manager

            return agente

        except BaseException:
            await manager.close_all()
            raise

    async def executar(
        self,
        prompt: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> Any:

        if not prompt or not prompt.strip():
            raise ValueError("O prompt não pode ser vazio.")

        return await self._engine.arun(
            input=prompt,
            stream=False,
            user_id=user_id,
            session_id=session_id,
        )

    async def close(self) -> None:
        if self._mcp_manager is not None:
            await self._mcp_manager.close_all()
            self._mcp_manager = None
