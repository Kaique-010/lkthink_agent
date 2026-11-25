
import asyncio
import json

import pytest

from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.context import (
    AgentIdentity,
    criar_contexto_execucao,
    definir_contexto,
    limpar_contexto,
    obter_contexto,
)
from lkthink_agent.observability.events import (
    EventName,
    criar_evento,
)
from lkthink_agent.observability.exporters.console import ConsoleExporter
from lkthink_agent.observability.logger import EventLogger
from lkthink_agent.observability.sanitization import (
    sanitizar_metadata,
    sanitizar_texto,
    sanitizar_valor,
)


def criar_agente(
    label="AGENT-01",
    slug="python_developer",
):
    return AgentIdentity(
        id="agent-uuid-001",
        slug=slug,
        name="Python Developer",
        label=label,
        color="blue",
    )


def test_contexto_gera_identificadores():
    contexto = criar_contexto_execucao(
        tenant_id="tenant-001",
        agent=criar_agente(),
    )

    assert contexto.trace_id
    assert contexto.run_id
    assert contexto.span_id
    assert contexto.tenant_id == "tenant-001"
    assert contexto.agent.slug == "python_developer"


def test_span_preserva_trace_e_cria_hierarquia():
    contexto = criar_contexto_execucao(
        tenant_id="tenant-001",
        agent=criar_agente(),
    )

    span = contexto.criar_span(
        component="knowledge",
        operation="semantic_search",
    )

    assert span.trace_id == contexto.trace_id
    assert span.run_id == contexto.run_id
    assert span.span_id != contexto.span_id
    assert span.parent_span_id == contexto.span_id
    assert span.component == "knowledge"
    assert span.operation == "semantic_search"


def test_contexto_atual_e_restaurado():
    contexto = criar_contexto_execucao(
        tenant_id="tenant-001",
    )

    token = definir_contexto(contexto)

    try:
        assert obter_contexto() == contexto
    finally:
        limpar_contexto(token)

    assert obter_contexto() is None


@pytest.mark.asyncio
async def test_isolamento_entre_execucoes_concorrentes():
    async def executar(tenant_id):
        contexto = criar_contexto_execucao(
            tenant_id=tenant_id,
        )

        token = definir_contexto(contexto)

        try:
            await asyncio.sleep(0.01)
            contexto_atual = obter_contexto()

            return {
                "tenant_id": contexto_atual.tenant_id,
                "run_id": contexto_atual.run_id,
            }
        finally:
            limpar_contexto(token)

    resultado_a, resultado_b = await asyncio.gather(
        executar("tenant-A"),
        executar("tenant-B"),
    )

    assert resultado_a["tenant_id"] == "tenant-A"
    assert resultado_b["tenant_id"] == "tenant-B"
    assert resultado_a["run_id"] != resultado_b["run_id"]


def test_evento_herda_contexto():
    contexto = criar_contexto_execucao(
        tenant_id="tenant-001",
        agent=criar_agente(),
    )

    token = definir_contexto(contexto)

    try:
        evento = criar_evento(
            event=EventName.AGENT_RUN_STARTED,
            message="O agente começou a trabalhar.",
        )
    finally:
        limpar_contexto(token)

    dados = evento.to_dict()

    assert dados["trace_id"] == contexto.trace_id
    assert dados["run_id"] == contexto.run_id
    assert dados["tenant_id"] == "tenant-001"
    assert dados["agent"]["slug"] == "python_developer"


def test_sanitizacao_de_campos_sensiveis():
    metadata = {
        "provider": "jina",
        "api_key": "jina_secret_123",
        "password": "senha123",
        "temperature": 0.2,
        "request": {
            "authorization": "Bearer token123",
        },
    }

    resultado = sanitizar_metadata(metadata)

    assert resultado["provider"] == "jina"
    assert resultado["api_key"] == "[REDACTED]"
    assert resultado["password"] == "[REDACTED]"
    assert resultado["temperature"] == 0.2
    assert resultado["request"]["authorization"] == "[REDACTED]"


def test_sanitizacao_de_url_preserva_host():
    url = (
        "postgresql://lkthink:senha123"
        "@localhost:5442/lkthink"
    )

    resultado = sanitizar_texto(url)

    assert "senha123" not in resultado
    assert "lkthink" in resultado
    assert "@localhost:5442/lkthink" in resultado
    assert "[REDACTED]" in resultado


def test_sanitizacao_de_bearer_em_texto():
    resultado = sanitizar_texto(
        "Authorization: Bearer token_super_secreto"
    )

    assert "token_super_secreto" not in resultado
    assert "[REDACTED]" in resultado


def test_sanitizacao_de_texto_limita_tamanho():
    resultado = sanitizar_texto(
        "A" * 100,
        limite=20,
    )

    assert len(resultado) > 20
    assert resultado.endswith("... [TRUNCADO]")


def test_sanitizacao_de_valores_aninhados():
    resultado = sanitizar_valor({
        "items": [
            {"access_token": "token-123"},
            {"name": "Documento técnico"},
        ]
    })

    assert resultado["items"][0]["access_token"] == "[REDACTED]"
    assert resultado["items"][1]["name"] == "Documento técnico"


def test_logger_grava_jsonl(tmp_path):
    arquivo = tmp_path / "logs" / "lkthink.jsonl"

    config = ObservabilityConfig(
        console_enabled=False,
        json_enabled=True,
    )

    logger = EventLogger(
        config=config,
        json_file=arquivo,
    )

    logger.info(
        EventName.AGENT_RUN_STARTED,
        "O agente começou a trabalhar.",
        metadata={
            "model": "deepseek-chat",
            "api_key": "segredo-123",
        },
    )

    assert arquivo.exists()

    linhas = arquivo.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(linhas) == 1

    evento = json.loads(linhas[0])

    assert evento["event"] == "agent.run.started"
    assert evento["metadata"]["model"] == "deepseek-chat"
    assert evento["metadata"]["api_key"] == "[REDACTED]"


def test_console_exibe_identidade_colorida():
    from io import StringIO

    saida = StringIO()

    config = ObservabilityConfig(
        console_colors=True,
    )

    console = ConsoleExporter(
        config=config,
        stream=saida,
        force_color=True,
    )

    console.export({
        "timestamp": "2026-11-25T08:30:00.000Z",
        "level": "INFO",
        "event": "agent.run.started",
        "message": "O agente começou a trabalhar.",
        "component": "runtime",
        "status": "started",
        "run_id": "12345678-1234-1234-1234-123456789012",
        "trace_id": "87654321-1234-1234-1234-123456789012",
        "agent": {
            "id": "agent-001",
            "slug": "python_developer",
            "name": "Python Developer",
            "label": "AGENT-01",
            "color": "blue",
        },
    })

    resultado = saida.getvalue()

    assert "AGENT-01" in resultado
    assert "O agente começou a trabalhar." in resultado
    assert "\033[" in resultado


def test_logger_nao_exibe_cor_quando_desabilitada(tmp_path):
    from io import StringIO

    saida = StringIO()

    config = ObservabilityConfig(
        console_enabled=True,
        console_colors=False,
        json_enabled=False,
    )

    console = ConsoleExporter(
        config=config,
        stream=saida,
    )

    logger = EventLogger(
        config=config,
        console_exporter=console,
        json_file=tmp_path / "logs.jsonl",
    )

    logger.info(
        EventName.AGENT_RUN_STARTED,
        "Teste de terminal.",
    )

    resultado = saida.getvalue()

    assert "Teste de terminal." in resultado
    assert "\033[" not in resultado
