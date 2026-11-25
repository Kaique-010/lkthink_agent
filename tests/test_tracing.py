import asyncio

import pytest

from lkthink_agent.observability.context import obter_contexto
from lkthink_agent.observability.tracing import Tracer


class FakeLogger:
    def __init__(self):
        self.events = []

    def emit(self, **kwargs):
        self.events.append(kwargs)
        return kwargs

@pytest.fixture
def logger():
    return FakeLogger()

@pytest.fixture
def tracer(logger):
    return Tracer(logger=logger)

def test_cria_span_raiz(tracer):
    with tracer.span("runtime", "execute") as span:
        contexto = obter_contexto()

        assert contexto is not None
        assert contexto.component == "runtime"
        assert contexto.operation == "execute"
        assert contexto.parent_span_id is None
        assert span.context == contexto

    assert obter_contexto() is None

def test_cria_hierarquia_de_spans(tracer):
    with tracer.span("runtime", "execute"):
        contexto_pai = obter_contexto()

        with tracer.span("agent", "run") as filho:
            contexto_filho = obter_contexto()

            assert contexto_filho.trace_id == contexto_pai.trace_id
            assert contexto_filho.run_id == contexto_pai.run_id
            assert contexto_filho.parent_span_id == contexto_pai.span_id
            assert filho.context == contexto_filho

        assert obter_contexto() == contexto_pai

    assert obter_contexto() is None

def test_emite_eventos_de_inicio_e_conclusao(tracer, logger):
    with tracer.span("agent", "run"):
        pass

    assert [event["event"] for event in logger.events] == [
        "trace.span.started",
        "trace.span.completed",
    ]

    assert logger.events[0]["status"] == "started"
    assert logger.events[1]["status"] == "completed"

def test_registra_falha_e_restauracao_de_contexto(tracer, logger):
    with pytest.raises(ValueError), tracer.span("agent", "run"):
        raise ValueError("Erro simulado")

    assert obter_contexto() is None
    assert logger.events[-1]["event"] == "trace.span.failed"
    assert logger.events[-1]["status"] == "failed"
    assert logger.events[-1]["error"].args == ("Erro simulado",)

def test_duracao_fica_congelada_apos_finalizacao(tracer):
    with tracer.span("agent", "run") as span:
        pass

    duracao = span.duration_ms

    assert duracao is not None
    assert duracao >= 0
    assert span.duration_ms == duracao

@pytest.mark.asyncio
async def test_span_assincrono(tracer):
    async with tracer.span("llm", "request"):
        contexto = obter_contexto()

        assert contexto is not None
        assert contexto.component == "llm"

    assert obter_contexto() is None

@pytest.mark.asyncio
async def test_isolamento_de_spans_concorrentes(tracer):
    resultados = []

    async def executar(nome):
        async with tracer.span("agent", nome):
            contexto = obter_contexto()
            await asyncio.sleep(0.01)
            contexto_final = obter_contexto()

            resultados.append(
                (
                    nome,
                    contexto.trace_id,
                    contexto.span_id,
                    contexto_final.span_id,
                )
            )

    await asyncio.gather(
        executar("agent-01"),
        executar("agent-02"),
    )

    assert len(resultados) == 2

    assert resultados[0][1] != resultados[1][1]
    assert resultados[0][2] == resultados[0][3]
    assert resultados[1][2] == resultados[1][3]

def test_nao_permite_reentrada_no_mesmo_span(tracer):
    span = tracer.span("agent", "run")

    with span, pytest.raises(RuntimeError):
        span.__enter__()