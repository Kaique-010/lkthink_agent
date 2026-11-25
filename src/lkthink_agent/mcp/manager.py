
from lkthink_agent.mcp.adapter import MCPToolAdapter
from lkthink_agent.mcp.client import MCPClient
from lkthink_agent.mcp.config import MCPServerConfig
from lkthink_agent.tools.registry import ToolRegistry


class MCPManager:

    def __init__(self) -> None:
        self._clients: dict[str, MCPClient] = {}
        self._adapters: dict[str, MCPToolAdapter] = {}

    def register_adapter(
        self,
        name: str,
        adapter: MCPToolAdapter,
    ) -> None:
        self._adapters[name] = adapter

    def register_server(
        self,
        config: MCPServerConfig,
    ) -> None:
        if config.name in self._clients:
            raise ValueError(
                f"Servidor MCP '{config.name}' já registrado."
            )

        self._clients[config.name] = MCPClient(config)

    def get_client(self, name: str) -> MCPClient:
        try:
            return self._clients[name]
        except KeyError:
            raise KeyError(
                f"Servidor MCP '{name}' não encontrado."
            ) from None

    async def connect_server(
        self,
        config: MCPServerConfig,
    ) -> MCPClient:

        # Registra o servidor antes de conectar.
        if config.name not in self._clients:
            self.register_server(config)

        client = self.get_client(config.name)

        if not client.connected:
            await client.connect()

        return client

    async def connect_all(self) -> None:
        conectados = []

        try:
            for client in self._clients.values():
                if not client.connected:
                    await client.connect()
                    conectados.append(client)

        except Exception:
            for client in reversed(conectados):
                await client.close()

            raise

    async def list_tools(
        self,
        config: MCPServerConfig,
    ):
        client = self.get_client(config.name)
        return await client.list_tools()

    
    async def register_tools(
        self,
        registry: ToolRegistry,
        *,
        config: MCPServerConfig,
        allowed_tools: list[str],
    ) -> list[str]:

        server_name = config.name
        client = self.get_client(server_name)

        if not client.connected:
            raise RuntimeError(
                f"Servidor MCP '{server_name}' não está conectado."
            )

        adapter = self._adapters.get(server_name)

        if adapter is None:
            adapter = MCPToolAdapter()
            self.register_adapter(server_name, adapter)

        return await adapter.registrar(
            client=client,
            registry=registry,
            allowed_tools=allowed_tools,
        )


    async def close_server(
        self,
        config: MCPServerConfig,
    ) -> None:
        client = self.get_client(config.name)
        await client.close()

    async def close_all(self) -> None:
        for client in reversed(list(self._clients.values())):
            if client.connected:
                await client.close()

    def list_servers(self) -> list[str]:
        return list(self._clients.keys())
