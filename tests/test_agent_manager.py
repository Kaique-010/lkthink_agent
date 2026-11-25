
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from lkthink_agent.agents.agent import LKThinkAgent
from lkthink_agent.agents.manager import AgentManager


@pytest.fixture
def runtime():
    runtime = Mock()
    runtime.executar = AsyncMock()
    return runtime


@pytest.fixture
def manager(runtime):
    return AgentManager(runtime=runtime)


def criar_agente(agent_id="agent-001", slug="agente-teste"):
    agent = Mock(spec=LKThinkAgent)
    agent.identity = SimpleNamespace(
        id=agent_id,
        slug=slug,
    )
    return agent


def test_registra_agente(manager):
    agent = criar_agente()

    resultado = manager.register(agent)

    assert resultado is agent
    assert len(manager) == 1


def test_busca_agente_por_id(manager):
    agent = criar_agente()

    manager.register(agent)

    assert manager.get("agent-001") is agent


def test_busca_agente_por_slug(manager):
    agent = criar_agente()

    manager.register(agent)

    assert manager.get("agente-teste") is agent


def test_impede_id_duplicado(manager):
    manager.register(criar_agente())

    with pytest.raises(ValueError):
        manager.register(
            criar_agente(
                agent_id="agent-001",
                slug="outro-slug",
            )
        )


def test_impede_slug_duplicado(manager):
    manager.register(criar_agente())

    with pytest.raises(ValueError):
        manager.register(
            criar_agente(
                agent_id="agent-002",
                slug="agente-teste",
            )
        )


def test_remove_agente_por_id(manager):
    agent = criar_agente()
    manager.register(agent)

    resultado = manager.remove("agent-001")

    assert resultado is agent
    assert len(manager) == 0
    assert not manager.exists("agent-001")
    assert not manager.exists("agente-teste")


def test_lista_agentes(manager):
    agent_1 = criar_agente("agent-001", "agente-um")
    agent_2 = criar_agente("agent-002", "agente-dois")

    manager.register(agent_1)
    manager.register(agent_2)

    agentes = manager.list_agents()

    assert len(agentes) == 2
    assert agentes == (agent_1, agent_2)


def test_verifica_existencia(manager):
    agent = criar_agente()
    manager.register(agent)

    assert manager.exists("agent-001")
    assert manager.exists("agente-teste")
    assert "agent-001" in manager
    assert "agente-teste" in manager

    assert not manager.exists("inexistente")


def test_agente_inexistente(manager):
    with pytest.raises(KeyError):
        manager.get("inexistente")


def test_rejeita_objeto_que_nao_e_agente(manager):
    with pytest.raises(TypeError):
        manager.register(object())


@pytest.mark.asyncio
async def test_executa_agente(manager, runtime):
    agent = criar_agente()
    manager.register(agent)

    resultado_esperado = SimpleNamespace(content="Resposta do agente")
    runtime.executar.return_value = resultado_esperado

    resultado = await manager.execute(
        agent_id="agente-teste",
        prompt="Explique arquitetura de agentes.",
        user_id="usuario-001",
        session_id="sessao-001",
        tenant_id="empresa-001",
    )

    assert resultado is resultado_esperado

    runtime.executar.assert_awaited_once_with(
        agent,
        "Explique arquitetura de agentes.",
        user_id="usuario-001",
        session_id="sessao-001",
        tenant_id="empresa-001",
    )


@pytest.mark.asyncio
async def test_propagacao_de_erro_na_execucao(manager, runtime):
    agent = criar_agente()
    manager.register(agent)

    runtime.executar.side_effect = RuntimeError("Falha na execução")

    with pytest.raises(RuntimeError, match="Falha na execução"):
        await manager.execute(
            "agent-001",
            "Teste",
        )
