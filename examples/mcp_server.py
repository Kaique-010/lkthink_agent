from mcp.server.fastmcp import FastMCP

server = FastMCP(
    name="lkthink-demo",
    instructions="Servidor MCP de demonstração do LKThink Agent.",
)


@server.tool()
def consultar_cliente(cliente_id: int) -> dict:
    """Consulta os dados de um cliente pelo identificador."""

    clientes = {
        1: {
            "id": 1,
            "nome": "Empresa Exemplo",
            "cidade": "Curitiba",
        },
        2: {
            "id": 2,
            "nome": "Comercial Paraná",
            "cidade": "Campo Largo",
        },
    }

    cliente = clientes.get(cliente_id)

    if not cliente:
        return {
            "erro": "Cliente não encontrado",
            "cliente_id": cliente_id,
        }

    return cliente


@server.tool()
def listar_clientes() -> list[dict]:
    """Lista os clientes disponíveis."""

    return [
        {
            "id": 1,
            "nome": "Empresa Exemplo",
        },
        {
            "id": 2,
            "nome": "Comercial Paraná",
        },
    ]


if __name__ == "__main__":
    server.run(transport="stdio")