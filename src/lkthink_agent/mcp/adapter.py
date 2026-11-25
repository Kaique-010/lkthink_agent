from lkthink_agent.mcp.client import MCPClient
from lkthink_agent.tools.registry import ToolRegistry


class MCPToolAdapter:

    async def registrar(
        self,
        client: MCPClient,
        registry: ToolRegistry,
        *,
        allowed_tools: list[str],
    ) -> list[str]:

        discovered = await client.list_tools()
        available = {tool.name: tool for tool in discovered}

        desconhecidas = set(allowed_tools) - set(available)

        if desconhecidas:
            raise ValueError(
                "Ferramentas MCP não encontradas: "
                + ", ".join(sorted(desconhecidas))
            )

        registradas = []

        for tool_name in allowed_tools:
            tool = available[tool_name]

            nome_publico = f"{tool.server_name}__{tool.name}"

            async def executar(
                _tool_name: str = tool.name,
                **kwargs,
            ):
                return await client.call_tool(
                    name=_tool_name,
                    arguments=kwargs,
                )

            executar.__name__ = nome_publico
            executar.__doc__ = tool.description or (
                f"Ferramenta MCP {tool.name}."
            )

            registry.register(
                executar,
                name=nome_publico,
                description=tool.description or None,
                parameters=tool.input_schema,
            )

            registradas.append(nome_publico)

        return registradas