
from types import SimpleNamespace

from lkthink_agent.orchestration.aggregator import TeamAggregator
from lkthink_agent.orchestration.context import TeamExecutionContext


def criar_contexto():
    return TeamExecutionContext(
        team_id="analise",
        team_name="Equipe de análise",
        prompt="Analise os dados de vendas.",
    )


def criar_resultado(
    agent_id="pesquisador",
    agent_name="Pesquisador",
    content="Dados encontrados.",
):
    return SimpleNamespace(
        agent_id=agent_id,
        agent_name=agent_name,
        content=content,
    )


def test_agrega_resultados_de_todas_as_etapas():
    context = criar_contexto()

    context.registrar_resultado(
        "pesquisa",
        criar_resultado(content="Foram encontrados 100 registros."),
    )
    context.registrar_resultado(
        "analise",
        criar_resultado(
            agent_id="analista",
            agent_name="Analista",
            content="O crescimento foi de 15%.",
        ),
    )

    resultado = TeamAggregator().agregar(context)

    assert "Analise os dados de vendas." in resultado
    assert "ETAPA: pesquisa" in resultado
    assert "ETAPA: analise" in resultado
    assert "Foram encontrados 100 registros." in resultado
    assert "O crescimento foi de 15%." in resultado


def test_agrega_apenas_etapas_selecionadas():
    context = criar_contexto()

    context.registrar_resultado(
        "pesquisa",
        criar_resultado(content="Resultado da pesquisa."),
    )
    context.registrar_resultado(
        "analise",
        criar_resultado(content="Resultado da análise."),
    )

    resultado = TeamAggregator().agregar(
        context,
        stage_names=("pesquisa",),
    )

    assert "Resultado da pesquisa." in resultado
    assert "Resultado da análise." not in resultado


def test_formata_conteudo_estruturado():
    context = criar_contexto()

    context.registrar_resultado(
        "pesquisa",
        criar_resultado(
            content={"total": 100, "status": "concluido"},
        ),
    )

    resultado = TeamAggregator().agregar(context)

    assert '"total": 100' in resultado
    assert '"status": "concluido"' in resultado


def test_contexto_sem_resultados():
    context = criar_contexto()

    resultado = TeamAggregator().agregar(context)

    assert "Nenhum resultado anterior" in resultado
    assert context.prompt in resultado


def test_preserva_identificacao_dos_agentes():
    context = criar_contexto()

    context.registrar_resultado(
        "pesquisa",
        criar_resultado(
            agent_id="agente-01",
            agent_name="Agente Pesquisador",
        ),
    )

    resultado = TeamAggregator().agregar(context)

    assert "Agente Pesquisador" in resultado
    assert "agente-01" in resultado
