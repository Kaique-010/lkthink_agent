
from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.context import (
    AgentIdentity,
    ObservabilityContext,
    criar_contexto_execucao,
    definir_contexto,
    limpar_contexto,
)
from lkthink_agent.observability.exporters.console import ConsoleExporter
from lkthink_agent.observability.logger import EventLogger


@contextmanager
def ativar_contexto(
    contexto: ObservabilityContext,
) -> Iterator[None]:
    """Ativa um contexto temporariamente e restaura o anterior."""
    token = definir_contexto(contexto)

    try:
        yield
    finally:
        limpar_contexto(token)


def test_visualizar_logs_observabilidade():
    arquivo_json = Path("logs/observability-demo.jsonl")

    arquivo_json.parent.mkdir(parents=True, exist_ok=True)

    if arquivo_json.exists():
        arquivo_json.unlink()

    config = ObservabilityConfig(
        service_name="lkthink-agent",
        environment="development",
        console_enabled=True,
        console_colors=True,
        json_enabled=True,
        json_file=str(arquivo_json),
        log_level="DEBUG",
    )

    console = ConsoleExporter(
        config=config,
        stream=sys.stdout,
        force_color=True,
    )

    logger = EventLogger(
        config=config,
        console_exporter=console,
        json_file=arquivo_json,
    )

    agente = AgentIdentity(
        id="agent-001",
        slug="python_developer",
        name="Python Developer",
        label="AGENT-01",
        color="blue",
    )

    # Trace raiz: representa toda a execução.
    contexto_raiz = criar_contexto_execucao(
        tenant_id="tenant-demo",
        metadata={"environment": "development"},
    )

    contexto_raiz = replace(
        contexto_raiz,
        component="orchestrator",
        operation="run",
    )

    # Span do agente: filho direto do orquestrador.
    contexto_agente = replace(
        contexto_raiz.criar_span(
            component="runtime",
            operation="agent_execution",
        ),
        agent=agente,
    )

    print("\n")
    print("=" * 85)
    print(" LKTHINK AGENT | DEMONSTRAÇÃO DE OBSERVABILIDADE")
    print("=" * 85)

    with ativar_contexto(contexto_raiz):

        # 1. Orquestrador: início.
        logger.info(
            event="orchestrator.run.started",
            message="Iniciando execução do fluxo de agentes.",
            component="orchestrator",
            operation="run",
            status="started",
        )

        # 2. Seleção do agente: filho do orquestrador.
        contexto_selecao = contexto_raiz.criar_span(
            component="runtime",
            operation="agent_selection",
        )

        with ativar_contexto(contexto_selecao):
            logger.info(
                event="agent.selection.completed",
                message="Agente Python Developer selecionado.",
                component="runtime",
                operation="agent_selection",
                status="completed",
                metadata={"agent_slug": agente.slug},
            )

        # 3. Execução do agente.
        with ativar_contexto(contexto_agente):

            logger.info(
                event="agent.run.started",
                message="Agente iniciou o processamento.",
                component="runtime",
                operation="agent_execution",
                status="started",
            )

            # 4. Runtime.
            contexto_runtime = contexto_agente.criar_span(
                component="runtime",
                operation="execute",
            )

            with ativar_contexto(contexto_runtime):
                logger.info(
                    event="runtime.execution.started",
                    message="Iniciando processamento da solicitação.",
                    component="runtime",
                    operation="execute",
                    status="started",
                )

                logger.info(
                    event="runtime.execution.completed",
                    message="Processamento inicial concluído.",
                    component="runtime",
                    operation="execute",
                    status="completed",
                    duration_ms=35.20,
                )

            # 5. Knowledge / RAG.
            contexto_rag = contexto_agente.criar_span(
                component="knowledge",
                operation="semantic_search",
            )

            with ativar_contexto(contexto_rag):
                logger.info(
                    event="rag.retrieval.started",
                    message="Consultando base de conhecimento vetorial.",
                    component="knowledge",
                    operation="semantic_search",
                    status="started",
                    metadata={
                        "provider": "pgvector",
                        "top_k": 5,
                    },
                )

                logger.info(
                    event="rag.retrieval.completed",
                    message="Documentos relevantes recuperados.",
                    component="knowledge",
                    operation="semantic_search",
                    status="completed",
                    duration_ms=125.45,
                    metadata={"documents_found": 5},
                )

            # 6. LLM.
            contexto_llm = contexto_agente.criar_span(
                component="llm",
                operation="completion",
            )

            with ativar_contexto(contexto_llm):
                logger.info(
                    event="llm.request.started",
                    message="Enviando solicitação para o modelo.",
                    component="llm",
                    operation="completion",
                    status="started",
                    metadata={
                        "provider": "deepseek",
                        "model": "deepseek-chat",
                    },
                )

                logger.info(
                    event="llm.request.completed",
                    message="Resposta recebida do modelo.",
                    component="llm",
                    operation="completion",
                    status="completed",
                    duration_ms=850.32,
                    metadata={
                        "model": "deepseek-chat",
                        "input_tokens": 1200,
                        "output_tokens": 350,
                    },
                )

            # 7. Ferramenta: execução bem-sucedida.
            contexto_tool = contexto_agente.criar_span(
                component="tools",
                operation="tool_execution",
            )

            with ativar_contexto(contexto_tool):
                logger.info(
                    event="tool.call.completed",
                    message="Ferramenta executada com sucesso.",
                    component="tools",
                    operation="tool_execution",
                    status="completed",
                    duration_ms=42.10,
                    metadata={"tool": "calculator"},
                )

            # 8. Ferramenta: falha simulada.
            contexto_tool_erro = contexto_agente.criar_span(
                component="tools",
                operation="tool_execution",
            )

            with ativar_contexto(contexto_tool_erro):
                logger.error(
                    event="tool.call.failed",
                    message="Falha simulada durante execução da ferramenta.",
                    component="tools",
                    operation="tool_execution",
                    status="failed",
                    error=RuntimeError("Erro demonstrativo"),
                    metadata={"tool": "external_api"},
                )

            # 9. Agente: conclusão.
            logger.info(
                event="agent.run.completed",
                message="Agente concluiu o processamento.",
                component="runtime",
                operation="agent_execution",
                status="completed",
                duration_ms=1017.87,
            )

        # 10. Orquestrador: conclusão.
        logger.info(
            event="orchestrator.run.completed",
            message="Fluxo de execução finalizado.",
            component="orchestrator",
            operation="run",
            status="completed",
        )

    # 11. Leitura dos registros estruturados.
    registros = [
        json.loads(linha)
        for linha in arquivo_json.read_text(
            encoding="utf-8",
        ).splitlines()
    ]

    print("\n")
    print("=" * 85)
    print(" JSONL | REGISTROS ESTRUTURADOS")
    print("=" * 85)

    print(
        json.dumps(
            registros,
            ensure_ascii=False,
            indent=2,
        )
    )

    # 12. Validações da demonstração.
    assert len(registros) == 13

    # Todos os eventos precisam pertencer ao mesmo trace e run.
    trace_ids = {evento["trace_id"] for evento in registros}
    run_ids = {evento["run_id"] for evento in registros}

    assert len(trace_ids) == 1
    assert None not in trace_ids
    assert len(run_ids) == 1
    assert None not in run_ids

    # Nenhum evento pode ficar sem span.
    assert all(evento["span_id"] for evento in registros)

    # Os spans precisam ser distintos por operação.
    spans = {evento["span_id"] for evento in registros}
    assert len(spans) == 8

    # Identifica eventos pelo nome.
    eventos = {
        evento["event"]: evento
        for evento in registros
    }

    # O orquestrador é a raiz.
    assert eventos["orchestrator.run.started"]["parent_span_id"] is None
    assert (
        eventos["orchestrator.run.completed"]["span_id"]
        == eventos["orchestrator.run.started"]["span_id"]
    )

    # A seleção e o agente são filhos do orquestrador.
    assert (
        eventos["agent.selection.completed"]["parent_span_id"]
        == contexto_raiz.span_id
    )

    assert (
        eventos["agent.run.started"]["parent_span_id"]
        == contexto_raiz.span_id
    )

    # As operações internas são filhas do agente.
    for nome in (
        "runtime.execution.started",
        "rag.retrieval.started",
        "llm.request.started",
        "tool.call.completed",
        "tool.call.failed",
    ):
        assert (
            eventos[nome]["parent_span_id"]
            == contexto_agente.span_id
        )

    # Início e conclusão compartilham o mesmo span.
    assert (
        eventos["runtime.execution.started"]["span_id"]
        == eventos["runtime.execution.completed"]["span_id"]
    )

    assert (
        eventos["rag.retrieval.started"]["span_id"]
        == eventos["rag.retrieval.completed"]["span_id"]
    )

    assert (
        eventos["llm.request.started"]["span_id"]
        == eventos["llm.request.completed"]["span_id"]
    )

    # A identidade do agente deve ser preservada.
    eventos_agente = [
        evento
        for evento in registros
        if evento["agent"] is not None
    ]

    assert eventos_agente
    assert all(
        evento["agent"]["slug"] == "python_developer"
        for evento in eventos_agente
    )

    # A falha precisa estar registrada como erro.
    evento_erro = eventos["tool.call.failed"]

    assert evento_erro["level"] == "ERROR"
    assert evento_erro["status"] == "failed"
    assert evento_erro["error"]["type"] == "RuntimeError"

    print("\n")
    print("=" * 85)
    print(" VALIDAÇÃO DA OBSERVABILIDADE")
    print("=" * 85)
    print(f"Total de eventos: {len(registros)}")
    print(f"Total de spans: {len(spans)}")
    print(f"Trace ID: {next(iter(trace_ids))}")
    print(f"Run ID: {next(iter(run_ids))}")
    print("Hierarquia: validada")
    print("Correlação: validada")
    print("Identidade dos agentes: validada")
    print("Erro simulado: validado")
    print(f"Arquivo JSONL: {arquivo_json.resolve()}")
