
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from lkthink_agent.orchestration.config import (
    TeamConfig,
    TeamStageConfig,
)
from lkthink_agent.orchestration.orchestrator import TeamOrchestrator


@pytest.fixture
def manager():
    manager = Mock()
    manager.exists.return_value = True

    runtime = Mock()
    runtime.tracer = Mock()
    runtime.tracer.span.return_value = nullcontext()
    runtime.logger = Mock()

    manager.runtime = runtime
    manager.execute = AsyncMock()

    def executar(agent_id, prompt, **kwargs):
        return SimpleNamespace(
            agent_id=agent_id,
            agent_name=agent_id,
            content=f"Resultado de {agent_id}: {prompt}",
            run_id=f"run-{agent_id}",
            duration_ms=10.0,
        )

    manager.execute.side_effect = executar

    return manager


@pytest.fixture
def orchestrator(manager):
    return TeamOrchestrator(manager)


def criar_config(stages, fail_fast=True):
    return TeamConfig(
        id="equipe-analise",
        name="Equipe de análise",
        stages=tuple(stages),
        fail_fast=fail_fast,
    )


@pytest.mark.asyncio
async def test_executa_etapa_sequencial(orchestrator, manager):
    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador", "analista"),
            mode="sequential",
        ),
    ])

    resultado = await orchestrator.executar(
        config,
        "Analise os dados.",
        tenant_id="tenant-1",
        user_id="user-1",
    )

    assert resultado.total_resultados == 2
    assert resultado.total_falhas == 0
    assert resultado.team_id == "equipe-analise"
    assert resultado.prompt == "Analise os dados."
    assert manager.execute.await_count == 2


@pytest.mark.asyncio
async def test_execucao_hibrida_encaminha_resultados(
    orchestrator,
    manager,
):
    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador", "analista"),
            mode="parallel",
        ),
        TeamStageConfig(
            name="revisao",
            agent_ids=("revisor",),
            mode="sequential",
        ),
    ])

    await orchestrator.executar(
        config,
        "Analise as vendas.",
    )

    chamadas = manager.execute.await_args_list

    assert len(chamadas) == 3

    prompt_revisor = chamadas[2].args[1]

    assert "Analise as vendas." in prompt_revisor
    assert "Resultado de pesquisador" in prompt_revisor
    assert "Resultado de analista" in prompt_revisor


@pytest.mark.asyncio
async def test_preserva_prompt_original(orchestrator):
    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador",),
        ),
        TeamStageConfig(
            name="analise",
            agent_ids=("analista",),
        ),
    ])

    resultado = await orchestrator.executar(
        config,
        "Prompt original.",
    )

    assert resultado.prompt == "Prompt original."


@pytest.mark.asyncio
async def test_valida_agentes_antes_da_execucao(manager):
    manager.exists.side_effect = lambda agent_id: (
        agent_id == "pesquisador"
    )

    orchestrator = TeamOrchestrator(manager)

    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador", "inexistente"),
        ),
    ])

    with pytest.raises(KeyError):
        await orchestrator.executar(config, "Teste")

    manager.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejeita_prompt_vazio(orchestrator):
    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador",),
        ),
    ])

    with pytest.raises(ValueError):
        await orchestrator.executar(config, "  ")


@pytest.mark.asyncio
async def test_fail_fast_interrompe_proximas_etapas(manager):
    manager.execute.side_effect = RuntimeError("Falha simulada")

    orchestrator = TeamOrchestrator(manager)

    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador",),
        ),
        TeamStageConfig(
            name="analise",
            agent_ids=("analista",),
        ),
    ])

    with pytest.raises(RuntimeError):
        await orchestrator.executar(config, "Teste")

    assert manager.execute.await_count == 1


@pytest.mark.asyncio
async def test_sem_fail_fast_continua_apos_falha(manager):
    async def executar(agent_id, prompt, **kwargs):
        if agent_id == "pesquisador":
            raise RuntimeError("Falha na pesquisa")

        return SimpleNamespace(
            agent_id=agent_id,
            agent_name=agent_id,
            content="Resultado válido",
            run_id=f"run-{agent_id}",
            duration_ms=10.0,
        )

    manager.execute.side_effect = executar

    orchestrator = TeamOrchestrator(manager)

    config = criar_config([
        TeamStageConfig(
            name="pesquisa",
            agent_ids=("pesquisador",),
        ),
        TeamStageConfig(
            name="analise",
            agent_ids=("analista",),
        ),
    ], fail_fast=False)

    resultado = await orchestrator.executar(
        config,
        "Teste",
    )

    assert resultado.total_falhas == 1
    assert resultado.total_resultados == 1
    assert manager.execute.await_count == 2
