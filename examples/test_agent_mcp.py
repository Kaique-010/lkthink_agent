
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# Diretório raiz do projeto
ROOT = Path(__file__).resolve().parents[1]

# Permite executar o exemplo diretamente da pasta examples
sys.path.insert(0, str(ROOT))

# O .env é carregado pelo exemplo, não pelo núcleo da biblioteca
load_dotenv(ROOT / ".env")

from lkthink_agent.agents.agent import LKThinkAgent
from lkthink_agent.agents.config import AgentConfig
from lkthink_agent.execution.runtime import AgentRuntime
from lkthink_agent.mcp.config import MCPServerConfig
from lkthink_agent.providers.deepseek import (
    DeepSeekConfig,
    DeepSeekProvider,
)


async def main() -> None:
    agente = None

    try:
        print("\n[1] Configurando o provider DeepSeek...")

        provider_config = DeepSeekConfig.from_env()
        provider = DeepSeekProvider(provider_config)

        print(f"Modelo: {provider_config.model}")

        print("\n[2] Configurando o servidor MCP...")

        servidor_mcp = MCPServerConfig(
            name="clientes",
            transport="stdio",
            command=sys.executable,
            args=(
                str(ROOT / "examples" / "mcp_server.py"),
            ),
            cwd=str(ROOT),
        )

        config_agente = AgentConfig(
            id="agent-clientes-001",
            slug="consultor-clientes",
            name="Consultor de Clientes",
            label="Clientes",
            description="Agente especializado em consultas de clientes.",
            instructions=(
                "Você é um agente especializado em consultas de clientes. "
                "Quando precisar consultar dados de clientes, utilize "
                "obrigatoriamente a ferramenta MCP "
                "'clientes__consultar_cliente'. "
                "Nunca invente dados. Responda somente com informações "
                "retornadas pela ferramenta."
            ),
            color="blue",
        )

        print("\n[3] Criando agente e conectando ao MCP...")

        agente = await LKThinkAgent.criar_com_mcp(
            config=config_agente,
            provider=provider,
            mcp_servers=[servidor_mcp],
            allowed_tools={
                "clientes": [
                    "consultar_cliente",
                    "listar_clientes",
                ]
            },
        )

        print("Agente conectado ao servidor MCP.")

        print("\n[4] Executando pelo AgentRuntime...")

        runtime = AgentRuntime()

        prompt = (
            "Consulte obrigatoriamente o cliente de ID 1 usando "
            "a ferramenta MCP clientes__consultar_cliente. "
            "Depois informe o nome da empresa e a cidade. "
            "Não responda sem consultar a ferramenta."
        )

        resultado = await runtime.executar(
            agente,
            prompt,
            user_id="teste-mcp",
            session_id="sessao-teste-mcp-001",
        )

        print("\n[5] Resultado da execução")
        print("=" * 60)
        print(resultado.content)
        print("=" * 60)

        conteudo = str(resultado.content)

        if "Empresa Exemplo" not in conteudo or "Curitiba" not in conteudo:
            raise AssertionError(
                "A resposta não contém os dados esperados. "
                "Verifique se o agente realmente utilizou a ferramenta MCP."
            )

        print("\n[6] Métricas")

        print(f"Agente: {resultado.agent_name}")
        print(f"Agent ID: {resultado.agent_id}")
        print(f"Run ID: {resultado.run_id}")
        print(f"Provider Run ID: {resultado.provider_run_id}")
        print(f"Modelo: {resultado.model}")
        print(f"Provider: {resultado.model_provider}")
        print(f"Duração: {resultado.duration_ms} ms")
        print(f"Input tokens: {resultado.input_tokens}")
        print(f"Output tokens: {resultado.output_tokens}")
        print(f"Total tokens: {resultado.total_tokens}")
        print(f"Custo: {resultado.cost}")

        print("\n[7] Validação concluída.")
        print("Os dados esperados foram encontrados na resposta.")

    finally:
        if agente is not None:
            print("\n[8] Encerrando agente e conexão MCP...")
            await agente.close()
            print("Conexão encerrada.")


if __name__ == "__main__":
    asyncio.run(main())
