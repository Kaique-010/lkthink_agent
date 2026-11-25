from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)
from mcp.client.streamable_http import streamablehttp_client

from lkthink_agent.mcp.config import MCPServerConfig
from lkthink_agent.mcp.models import MCPTool


class MCPConnectionError(Exception):
    pass


class MCPToolExecutionError(Exception):
    pass


class MCPClient:

    def __init__(self, config: MCPServerConfig):
        self.config = config

        self._stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None

        self._tools: dict[str, MCPTool] = {}

    @property
    def connected(self) -> bool:
        return self._session is not None

    async def connect(self) -> None:
        if self.connected:
            return

        stack = AsyncExitStack()

        try:
            if self.config.transport == "stdio":
                server = StdioServerParameters(
                    command=self.config.command,
                    args=list(self.config.args),
                    env=self.config.env,
                    cwd=self.config.cwd,
                )

                read_stream, write_stream = (
                    await stack.enter_async_context(
                        stdio_client(server)
                    )
                )

            else:
                read_stream, write_stream, _ = (
                    await stack.enter_async_context(
                        streamablehttp_client(
                            url=self.config.url,
                            headers=self.config.headers,
                            timeout=self.config.timeout,
                            sse_read_timeout=self.config.sse_read_timeout,
                        )
                    )
                )

            session = ClientSession(
                read_stream,
                write_stream,
            )

            await stack.enter_async_context(session)
            await session.initialize()

            self._stack = stack
            self._session = session

        except Exception as exc:
            await stack.aclose()

            raise MCPConnectionError(
                f"Falha ao conectar ao servidor MCP "
                f"'{self.config.name}': {exc}"
            ) from exc

    async def list_tools(self) -> list[MCPTool]:
        session = self._require_session()

        result = await session.list_tools()

        ferramentas = []

        for tool in result.tools:
            ferramenta = MCPTool(
                server_name=self.config.name,
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema,
            )

            self._tools[tool.name] = ferramenta
            ferramentas.append(ferramenta)

        return ferramentas

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:

        session = self._require_session()

        if name not in self._tools:
            raise KeyError(
                f"Ferramenta MCP '{name}' não foi descoberta "
                f"no servidor '{self.config.name}'."
            )

        try:
            result = await session.call_tool(
                name=name,
                arguments=arguments or {},
            )

            if result.isError:
                raise MCPToolExecutionError(
                    f"Erro retornado pela ferramenta MCP '{name}'. "
                    f"Resultado: {self._serialize_result(result)}"
                )

            return self._serialize_result(result)

        except MCPToolExecutionError:
            raise

        except Exception as exc:
            raise MCPToolExecutionError(
                f"Falha ao executar ferramenta MCP '{name}': {exc}"
            ) from exc

    @staticmethod
    def _serialize_result(result: Any) -> Any:
        if result.structuredContent is not None:
            return result.structuredContent

        conteudos = []

        for item in result.content:
            if hasattr(item, "text"):
                conteudos.append(item.text)
            elif hasattr(item, "model_dump"):
                conteudos.append(item.model_dump(mode="json"))
            else:
                conteudos.append(str(item))

        if len(conteudos) == 1:
            return conteudos[0]

        return conteudos

    def _require_session(self) -> ClientSession:
        if self._session is None:
            raise MCPConnectionError(
                f"O servidor MCP '{self.config.name}' não está conectado."
            )

        return self._session

    async def close(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()

        self._stack = None
        self._session = None
        self._tools.clear()