import asyncio
import os

import pytest

from lkthink_agent.agents.agent import LKThinkAgent
from lkthink_agent.agents.config import AgentConfig
from lkthink_agent.agents.manager import AgentManager
from lkthink_agent.execution.runtime import AgentRuntime
from lkthink_agent.providers.deepseek import (
    DeepSeekConfig,
    DeepSeekProvider,
)


def test_integracao_real_deepseek():
    if not os.getenv("DEEPSEEK_API_KEY"):
        pytest.skip("DEEPSEEK_API_KEY não configurada.")

    async def scenario():
        provider = DeepSeekProvider(
            DeepSeekConfig.from_env()
        )

        config = AgentConfig(
            id="integration-deepseek",
            slug="integration-deepseek",
            name="Agente de integração DeepSeek",
            label="DeepSeek Integration",
            instructions=(
                "Você é um agente de teste. "
                "Responda exatamente conforme solicitado. "
                "Não acrescente explicações."
            ),
        )

        agent = LKThinkAgent(
            config=config,
            provider=provider,
        )

        runtime = AgentRuntime()
        manager = AgentManager(runtime=runtime)

        manager.register(agent)

        try:
            resultado = await manager.execute(
                "integration-deepseek",
                "Responda somente com: LKTHINK_OK",
                user_id="integration-user",
                session_id="integration-session",
                tenant_id="integration-tenant",
            )

            assert resultado.agent_id == "integration-deepseek"
            assert resultado.content
            assert "LKTHINK_OK" in str(resultado.content).upper()
            assert resultado.run_id
            assert resultado.provider_run_id
            assert resultado.model == provider.config.model

        finally:
            await manager.close_all()

    asyncio.run(
        scenario(),
        loop_factory=asyncio.SelectorEventLoop,
    )
