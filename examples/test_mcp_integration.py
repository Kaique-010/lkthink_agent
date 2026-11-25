
import asyncio
import sys
from pathlib import Path

from lkthink_agent.mcp import MCPServerConfig, MCPManager


async def main():
    raiz = Path(__file__).resolve().parent

    config = MCPServerConfig(
        name="demo",
        transport="stdio",
        command=sys.executable,
        args=(str(raiz / "mcp_server.py"),),
    )

    manager = MCPManager()

    try:
        print("\n[1] Conectando ao servidor MCP...")
        client = await manager.connect_server(config)

        print("\n[2] Descobrindo ferramentas...")
        ferramentas = await client.list_tools()

        for ferramenta in ferramentas:
            print(f"- {ferramenta.name}: {ferramenta.description}")

        print("\n[3] Executando consultar_cliente...")
        resultado = await client.call_tool(
            "consultar_cliente",
            {"cliente_id": 1},
        )
        print("Resultado:", resultado)

        print("\n[4] Executando listar_clientes...")
        resultado = await client.call_tool("listar_clientes")
        print("Resultado:", resultado)

        print("\n[5] Encerrando conexão...")

    finally:
        await manager.close_all()

    print("\nIntegração concluída.")


if __name__ == "__main__":
    asyncio.run(main())
