import pytest

from lkthink_agent.mcp.adapter import MCPToolAdapter
from lkthink_agent.mcp.config import MCPServerConfig
from lkthink_agent.mcp.models import MCPTool
from lkthink_agent.tools import ToolRegistry
from lkthink_agent.tools.adapters.agno import AgnoToolAdapter


class FakeMCPClient:

    connected = True

    async def list_tools(self):
        return [
            MCPTool(
                server_name="postgres",
                name="consultar_cliente",
                description="Consulta um cliente pelo ID.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "cliente_id": {
                            "type": "integer",
                            "description": "ID do cliente.",
                        }
                    },
                    "required": ["cliente_id"],
                },
            ),
            MCPTool(
                server_name="postgres",
                name="listar_clientes",
                description="Lista clientes.",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    async def call_tool(self, name, arguments=None):
        return {
            "ferramenta": name,
            "argumentos": arguments or {},
        }


def test_config_stdio():
    config = MCPServerConfig(
        name="postgres",
        transport="stdio",
        command="python",
        args=("-m", "servidor_mcp"),
    )

    assert config.transport == "stdio"
    assert config.command == "python"


def test_config_http():
    config = MCPServerConfig(
        name="api",
        transport="http",
        url="http://localhost:8000/mcp",
    )

    assert config.url == "http://localhost:8000/mcp"


def test_config_stdio_sem_command():
    with pytest.raises(ValueError):
        MCPServerConfig(
            name="postgres",
            transport="stdio",
        )


def test_config_http_sem_url():
    with pytest.raises(ValueError):
        MCPServerConfig(
            name="api",
            transport="http",
        )


@pytest.mark.asyncio
async def test_registrar_ferramenta_mcp():
    registry = ToolRegistry()
    client = FakeMCPClient()

    adapter = MCPToolAdapter()

    registradas = await adapter.registrar(
        client,
        registry,
        allowed_tools=["consultar_cliente"],
    )

    assert registradas == ["postgres__consultar_cliente"]
    assert registry.exists("postgres__consultar_cliente")
    assert len(registry) == 1


@pytest.mark.asyncio
async def test_preservar_json_schema():
    registry = ToolRegistry()
    client = FakeMCPClient()

    adapter = MCPToolAdapter()

    await adapter.registrar(
        client,
        registry,
        allowed_tools=["consultar_cliente"],
    )

    definition = registry.get("postgres__consultar_cliente")

    assert definition.parameters["type"] == "object"
    assert "cliente_id" in definition.parameters["properties"]
    assert definition.parameters["required"] == ["cliente_id"]


@pytest.mark.asyncio
async def test_executar_ferramenta_mcp():
    registry = ToolRegistry()
    client = FakeMCPClient()

    adapter = MCPToolAdapter()

    await adapter.registrar(
        client,
        registry,
        allowed_tools=["consultar_cliente"],
    )

    definition = registry.get("postgres__consultar_cliente")

    resultado = await definition.func(cliente_id=42)

    assert resultado == {
        "ferramenta": "consultar_cliente",
        "argumentos": {"cliente_id": 42},
    }


@pytest.mark.asyncio
async def test_nao_registrar_ferramentas_nao_autorizadas():
    registry = ToolRegistry()
    client = FakeMCPClient()

    adapter = MCPToolAdapter()

    await adapter.registrar(
        client,
        registry,
        allowed_tools=["consultar_cliente"],
    )

    assert len(registry) == 1
    assert not registry.exists("postgres__listar_clientes")


@pytest.mark.asyncio
async def test_rejeitar_ferramenta_inexistente():
    registry = ToolRegistry()
    client = FakeMCPClient()

    adapter = MCPToolAdapter()

    with pytest.raises(ValueError):
        await adapter.registrar(
            client,
            registry,
            allowed_tools=["ferramenta_inexistente"],
        )


@pytest.mark.asyncio
async def test_converter_schema_mcp_para_agno():
    registry = ToolRegistry()
    client = FakeMCPClient()

    await MCPToolAdapter().registrar(
        client,
        registry,
        allowed_tools=["consultar_cliente"],
    )

    ferramentas = AgnoToolAdapter().adaptar(registry)

    assert len(ferramentas) == 1
    assert ferramentas[0].name == "postgres__consultar_cliente"
    assert ferramentas[0].parameters["properties"]["cliente_id"]["type"] == "integer"