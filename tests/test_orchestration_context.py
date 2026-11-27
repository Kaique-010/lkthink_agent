
from types import SimpleNamespace

import pytest

from lkthink_agent.orchestration.context import TeamExecutionContext


@pytest.fixture
def contexto():
    return TeamExecutionContext(
        team_id="analise",
        team_name="Equipe de análise",
        prompt="Analise os dados.",
        tenant_id="tenant-1",
        user_id="user-1",
        session_id="session-1",
    )


def test_cria_contexto_com_identificador_unico():
    primeiro = TeamExecutionContext(
        team_id="team",
        team_name="Equipe",
        prompt="Teste",
    )
    segundo = TeamExecutionContext(
        team_id="team",
        team_name="Equipe",
        prompt="Teste",
    )

    assert primeiro.team_run_id
    assert primeiro.team_run_id != segundo.team_run_id


def test_valida_campos_obrigatorios():
    with pytest.raises(ValueError):
        TeamExecutionContext(
            team_id="",
            team_name="Equipe",
            prompt="Teste",
        )


def test_registra_resultado(contexto):
    resultado = SimpleNamespace(
        agent_id="pesquisador",
        content="Resultado da pesquisa",
    )

    contexto.registrar_resultado("pesquisa", resultado)

    assert contexto.total_resultados == 1
    assert contexto.obter_resultados_etapa("pesquisa") == (resultado,)
    assert contexto.obter_todos_resultados() == (resultado,)


def test_registra_resultados_de_etapas_diferentes(contexto):
    primeiro = SimpleNamespace(agent_id="pesquisador")
    segundo = SimpleNamespace(agent_id="revisor")

    contexto.registrar_resultado("pesquisa", primeiro)
    contexto.registrar_resultado("revisao", segundo)

    assert contexto.total_resultados == 2
    assert contexto.obter_todos_resultados() == (primeiro, segundo)


def test_rejeita_resultado_invalido(contexto):
    with pytest.raises(TypeError):
        contexto.registrar_resultado("pesquisa", object())


def test_registra_falha(contexto):
    contexto.registrar_falha(
        "pesquisa",
        "pesquisador",
        RuntimeError("Falha na pesquisa"),
    )

    assert contexto.total_falhas == 1
    assert contexto.failures[0].agent_id == "pesquisador"
    assert contexto.failures[0].error_type == "RuntimeError"
    assert contexto.failures[0].message == "Falha na pesquisa"


def test_rejeita_falha_invalida(contexto):
    with pytest.raises(TypeError):
        contexto.registrar_falha(
            "pesquisa",
            "pesquisador",
            "erro",
        )


def test_contextos_nao_compartilham_estado():
    primeiro = TeamExecutionContext(
        team_id="team",
        team_name="Equipe",
        prompt="Teste",
    )
    segundo = TeamExecutionContext(
        team_id="team",
        team_name="Equipe",
        prompt="Teste",
    )

    primeiro.registrar_falha(
        "pesquisa",
        "agente",
        RuntimeError("Erro"),
    )

    assert primeiro.total_falhas == 1
    assert segundo.total_falhas == 0
