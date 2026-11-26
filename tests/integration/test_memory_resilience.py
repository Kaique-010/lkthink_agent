import asyncio
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import OperationalError

from lkthink_agent.execution.runtime import AgentRuntime
from lkthink_agent.memory.config import MemoryConfig
from lkthink_agent.memory.service import MemoryService
from lkthink_agent.observability.context import AgentIdentity


class FakeAgent:
    def __init__(self):
        self.identity = AgentIdentity(
            id="resilience-agent",
            slug="resilience-agent",
            name="Agente de resiliencia",
            label="Agente de resiliencia",
            color="blue",
        )
        self.calls = []

    async def executar(self, prompt, *, user_id=None, session_id=None):
        self.calls.append(prompt)

        return SimpleNamespace(
            content="Resposta sem memoria",
            run_id="resilience-run",
            model="test-model",
            model_provider="test",
            metrics=None,
        )


def test_runtime_memory_database_failure():
    async def scenario():
        database_url = (
            "postgresql+psycopg://lkthink:lkthink_dev"
            "@127.0.0.1:59999/lkthink?connect_timeout=2"
        )

        # Teste 1: fail_open=True permite continuar.
        service_open = MemoryService(
            database_url,
            config=MemoryConfig(fail_open=True),
        )
        agent_open = FakeAgent()
        runtime_open = AgentRuntime(memory_service=service_open)

        try:
            result = await runtime_open.executar(
                agent=agent_open,
                prompt="Prompt original",
                user_id="user-resilience",
            )

            assert result.content == "Resposta sem memoria"
            assert agent_open.calls == ["Prompt original"]

        finally:
            await service_open.close()

        # Teste 2: fail_open=False interrompe a execução.
        service_closed = MemoryService(
            database_url,
            config=MemoryConfig(fail_open=False),
        )
        agent_closed = FakeAgent()
        runtime_closed = AgentRuntime(memory_service=service_closed)

        try:
            with pytest.raises(OperationalError):
                await runtime_closed.executar(
                    agent=agent_closed,
                    prompt="Prompt original",
                    user_id="user-resilience",
                )

            assert agent_closed.calls == []

        finally:
            await service_closed.close()

    asyncio.run(
        scenario(),
        loop_factory=asyncio.SelectorEventLoop,
    )
