# Ferramentas e MCP

## ToolRegistry

O módulo `lkthink_agent.tools` exporta `BaseTool`, `ToolDefinition` e `ToolRegistry`.

`ToolRegistry.register()` registra uma função ou instância de `BaseTool`. Pode receber `name`, `description`, `strict` e `parameters`. Também oferece `unregister`, `get`, `list_tools`, `exists`, `clear`, `len(registry)` e `name in registry`.

```python
from lkthink_agent.tools import ToolRegistry

registry = ToolRegistry()


def consultar_pedido(numero: str) -> dict:
    return {"numero": numero, "status": "em_separacao"}

registry.register(
    consultar_pedido,
    name="consultar_pedido",
    description="Consulta o status de um pedido.",
)
```

A adaptação para o formato de ferramentas do Agno é feita internamente por `AgnoToolAdapter` (`lkthink_agent.tools.adapters.agno`).

## Configuração MCP

`MCPServerConfig` exige `name` e `transport` (`"stdio"` ou `"http"`). Para `stdio`, informe `command` e opcionalmente `args`, `env` e `cwd`. Para `http`, informe `url` e opcionalmente `headers`. Os timeouts `timeout` e `sse_read_timeout` precisam ser positivos.

### Servidor STDIO

```python
from lkthink_agent.mcp import MCPServerConfig

config = MCPServerConfig(
    name="arquivos",
    transport="stdio",
    command="python",
    args=("./mcp_server.py",),
)
```

### Servidor HTTP

```python
config_http = MCPServerConfig(
    name="servico-remoto",
    transport="http",
    url="http://localhost:8001/mcp",
    headers={"Authorization": "Bearer <TOKEN>"},
)
```

## MCPManager

`MCPManager` registra adaptadores e configurações de servidores, conecta servidores, lista ferramentas, registra as ferramentas permitidas no `ToolRegistry` e encerra conexões.

Operações públicas: `register_adapter`, `register_server`, `get_client`, `connect_server`, `connect_all`, `list_tools`, `register_tools`, `close_server`, `close_all` e `list_servers`.

## Permissões

O fluxo de registro exige uma lista explícita `allowed_tools`. A factory `LKThinkAgent.criar_com_mcp(...)` também recebe `mcp_servers` e `allowed_tools` por servidor. Configure a allowlist no backend; não permita que o usuário final escolha ferramentas privilegiadas sem autorização.

## Tratamento de erros

`MCPClient` expõe `MCPConnectionError` e `MCPToolExecutionError`. Trate erros de conexão e de execução separadamente e encerre clientes em `finally` ou no lifecycle da aplicação.
