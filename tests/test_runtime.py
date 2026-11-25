
import asyncio
from types import SimpleNamespace

import pytest

from lkthink_agent.execution import AgentRuntime
from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.context import (
    AgentIdentity,
    obter_contexto,
)
from lkthink_agent.observability.logger import EventLogger


class FakeAgent:
    """Agente simulado para testes sem chamadas externas."""

    def __init__(
        self,
        agent_id="agent-001",
        name="Agente de teste",
        *,
        fail=False,
        delay=0,
    ):
        self.identity = AgentIdentity(
            id=agent_id,
            slug=agent_id,
            name=name,
            label=agent_id.upper(),
            color="blue",
        )
        self.fail = fail
        self.delay = delay
        self.contextos = []

    async def executar(
        self,
        prompt,
        *,
        user_id=None,
        session_id=None,
    ):
        contexto = obter_contexto()
        self.contextos.append(contexto)

        if self.delay:
            await asyncio.sleep(self.delay)

        if self.fail:
            raise RuntimeError("Erro simulado no agente.")

        return SimpleNamespace(
            content=f"Resposta para: {prompt}",
            run_id="provider-run-123",
            model="deepseek-chat",
            model_provider="DeepSeek",
        )


@pytest.fixture
def runtime():
    logger = EventLogger(
        config=ObservabilityConfig(
            console_enabled=False,
            json_enabled=False,
        )
    )
    return AgentRuntime(logger=logger)


@pytest.mark.asyncio
async def test_runtime_executa_agente_com_sucesso(runtime):
    agent = FakeAgent()

    resultado = await runtime.executar(
        agent,
        "Olá, LKThink!",
        user_id="user-001",
        session_id="session-001",
        tenant_id="tenant-001",
    )

    assert resultado.content == "Resposta para: Olá, LKThink!"
    assert resultado.agent_id == "agent-001"
    assert resultado.agent_name == "Agente de teste"
    assert resultado.run_id
    assert resultado.provider_run_id == "provider-run-123"
    assert resultado.model == "deepseek-chat"
    assert resultado.model_provider == "DeepSeek"
    assert resultado.duration_ms >= 0

    contexto = agent.contextos[0]

    assert contexto is not None
    assert contexto.tenant_id == "tenant-001"
    assert contexto.agent.id == "agent-001"
    assert contexto.component == "agent"
    assert contexto.parent_span_id is not None

    assert obter_contexto() is None


@pytest.mark.asyncio
async def test_runtime_propaga_erro_e_restabelece_contexto(runtime):
    agent = FakeAgent(fail=True)

    with pytest.raises(
        RuntimeError,
        match="Erro simulado no agente",
    ):
        await runtime.executar(
            agent,
            "Provocar erro",
        )

    assert obter_contexto() is None
    assert len(agent.contextos) == 1


@pytest.mark.asyncio
async def test_runtime_isola_execucoes_concorrentes(runtime):
    agent_a = FakeAgent(
        agent_id="agent-001",
        name="Agente A",
        delay=0.02,
    )

    agent_b = FakeAgent(
        agent_id="agent-002",
        name="Agente B",
        delay=0.02,
    )

    resultado_a, resultado_b = await asyncio.gather(
        runtime.executar(agent_a, "Pergunta A"),
        runtime.executar(agent_b, "Pergunta B"),
    )

    contexto_a = agent_a.contextos[0]
    contexto_b = agent_b.contextos[0]

    assert resultado_a.agent_id == "agent-001"
    assert resultado_b.agent_id == "agent-002"

    assert contexto_a.agent.id == "agent-001"
    assert contexto_b.agent.id == "agent-002"

    assert contexto_a.trace_id != contexto_b.trace_id
    assert contexto_a.run_id != contexto_b.run_id
    assert contexto_a.span_id != contexto_b.span_id

    assert obter_contexto() is None


@pytest.mark.asyncio
async def test_runtime_rejeita_prompt_vazio(runtime):
    agent = FakeAgent()

    with pytest.raises(
        ValueError,
        match="O prompt não pode ser vazio",
    ):
        await runtime.executar(agent, "   ")

    assert agent.contextos == []
    assert obter_contexto() is None


@pytest.mark.asyncio
async def test_runtime_gera_run_id_diferente_por_execucao(runtime):
    agent = FakeAgent()

    resultado_a = await runtime.executar(
        agent,
        "Primeira execução",
    )

    resultado_b = await runtime.executar(
        agent,
        "Segunda execução",
    )

    assert resultado_a.run_id != resultado_b.run_id
