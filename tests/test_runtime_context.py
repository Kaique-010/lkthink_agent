import asyncio
from types import SimpleNamespace

import pytest

from lkthink_agent.execution.runtime import AgentRuntime
from lkthink_agent.observability.context import (
    AgentIdentity,
    criar_contexto_execucao,
    definir_contexto,
    obter_contexto,
)


class BarreiraConcorrente:
    def __init__(self, participantes: int):
        self.participantes = participantes
        self.quantidade = 0
        self.evento = asyncio.Event()

    async def esperar(self):
        self.quantidade += 1

        if self.quantidade == self.participantes:
            self.evento.set()

        await self.evento.wait()


class AgenteStub:
    def __init__(self, agent_id, slug, barreira=None, capturas=None):
        self.identity = AgentIdentity(
            id=agent_id,
            slug=slug,
            name=f"Agente {agent_id}",
            label=slug,
            color="blue",
        )
        self.barreira = barreira
        self.capturas = capturas

    async def executar(self, prompt, *, user_id=None, session_id=None):
        if self.barreira:
            await self.barreira.esperar()

        contexto = obter_contexto()

        self.capturas[self.identity.id] = contexto

        return SimpleNamespace(
            content=f"Resposta de {self.identity.id}",
            model="modelo-teste",
            model_provider="provider-teste",
            run_id=f"run-{self.identity.id}",
            metrics=None,
        )


class AgenteComFalha:
    def __init__(self):
        self.identity = AgentIdentity(
            id="agente-erro",
            slug="agente-erro",
            name="Agente com erro",
            label="Erro",
            color="red",
        )

    async def executar(self, prompt, *, user_id=None, session_id=None):
        raise RuntimeError("Falha simulada no agente.")


@pytest.mark.asyncio
async def test_isola_contextos_de_execucoes_concorrentes():
    runtime = AgentRuntime()
    barreira = BarreiraConcorrente(participantes=2)
    capturas = {}

    agente_a = AgenteStub(
        "agente-a",
        "agente-a",
        barreira,
        capturas,
    )
    agente_b = AgenteStub(
        "agente-b",
        "agente-b",
        barreira,
        capturas,
    )

    resultados = await asyncio.gather(
        runtime.executar(
            agente_a,
            "Executar tarefa A",
            user_id="usuario-a",
            session_id="sessao-a",
            tenant_id="empresa-a",
        ),
        runtime.executar(
            agente_b,
            "Executar tarefa B",
            user_id="usuario-b",
            session_id="sessao-b",
            tenant_id="empresa-b",
        ),
    )

    contexto_a = capturas["agente-a"]
    contexto_b = capturas["agente-b"]

    assert contexto_a is not None
    assert contexto_b is not None

    assert contexto_a.agent.id == "agente-a"
    assert contexto_b.agent.id == "agente-b"

    assert contexto_a.tenant_id == "empresa-a"
    assert contexto_b.tenant_id == "empresa-b"

    assert contexto_a.metadata["user_id"] == "usuario-a"
    assert contexto_b.metadata["user_id"] == "usuario-b"

    assert contexto_a.metadata["session_id"] == "sessao-a"
    assert contexto_b.metadata["session_id"] == "sessao-b"

    assert contexto_a.run_id != contexto_b.run_id

    assert resultados[0].agent_id == "agente-a"
    assert resultados[1].agent_id == "agente-b"

    assert obter_contexto() is None


@pytest.mark.asyncio
async def test_runtime_restaurar_contexto_apos_sucesso():
    runtime = AgentRuntime()
    capturas = {}

    agente = AgenteStub(
        "agente-sucesso",
        "agente-sucesso",
        capturas=capturas,
    )

    contexto_externo = criar_contexto_execucao(
        tenant_id="contexto-externo",
    )
    token = definir_contexto(contexto_externo)

    try:
        await runtime.executar(
            agente,
            "Teste de sucesso",
            tenant_id="empresa-interna",
        )

        assert obter_contexto() is contexto_externo
        assert contexto_externo.tenant_id == "contexto-externo"
    finally:
        from lkthink_agent.observability.context import limpar_contexto

        limpar_contexto(token)


@pytest.mark.asyncio
async def test_runtime_restaurar_contexto_apos_excecao():
    runtime = AgentRuntime()
    agente = AgenteComFalha()

    contexto_externo = criar_contexto_execucao(
        tenant_id="contexto-externo",
    )
    token = definir_contexto(contexto_externo)

    try:
        with pytest.raises(
            RuntimeError,
            match="Falha simulada",
        ):
            await runtime.executar(
                agente,
                "Teste de falha",
                tenant_id="empresa-interna",
            )

        assert obter_contexto() is contexto_externo
    finally:
        from lkthink_agent.observability.context import limpar_contexto

        limpar_contexto(token)
