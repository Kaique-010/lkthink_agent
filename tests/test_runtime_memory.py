from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from lkthink_agent.execution.runtime import AgentRuntime
from lkthink_agent.observability.context import AgentIdentity


@dataclass
class FakeMemory:
    category: str
    content: str
    session_id: str | None = None
    metadata: dict[str, Any] | None = None


class FakeMemoryService:
    def __init__(
        self,
        memories: list[FakeMemory] | None = None,
        *,
        error: Exception | None = None,
        enabled: bool = True,
        fail_open: bool = True,
        max_items: int = 20,
        max_context_chars: int = 12_000,
    ) -> None:
        self.memories = memories or []
        self.error = error
        self.config = SimpleNamespace(
            enabled=enabled,
            fail_open=fail_open,
            max_items=max_items,
            max_context_chars=max_context_chars,
        )
        self.recall_calls: list[dict[str, Any]] = []
        self.remember_calls: list[dict[str, Any]] = []
        self.saved_memory = object()

    async def recall(
        self,
        *,
        agent_id: str,
        user_id: str,
        session_id: str | None = None,
        limit: int | None = None,
    ) -> list[FakeMemory]:
        self.recall_calls.append(
            {
                "agent_id": agent_id,
                "user_id": user_id,
                "session_id": session_id,
                "limit": limit,
            }
        )
        if self.error is not None:
            raise self.error
        # Memórias globais (session_id=None) e da sessão atual.
        return [
            memoria
            for memoria in self.memories
            if memoria.session_id is None or memoria.session_id == session_id
        ]

    async def remember(self, **kwargs: Any) -> object:
        self.remember_calls.append(kwargs)
        return self.saved_memory


class FakeAgent:
    def __init__(self, *, agent_id: str = "agent-01", name: str = "Agente de teste") -> None:
        self.identity = AgentIdentity(
            id=agent_id,
            slug=agent_id,
            name=name,
            label=name,
            color="blue",
        )
        self.calls: list[dict[str, Any]] = []

    async def executar(
        self,
        prompt: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> SimpleNamespace:
        self.calls.append(
            {
                "prompt": prompt,
                "user_id": user_id,
                "session_id": session_id,
            }
        )
        return SimpleNamespace(
            content="Resposta simulada",
            run_id="provider-run-01",
            model="modelo-teste",
            model_provider="teste",
            metrics=None,
        )


@pytest.mark.asyncio
async def test_runtime_recupera_memorias_antes_de_executar_agente() -> None:
    memoria = FakeMemory(
        category="preferencias",
        content="O usuário prefere respostas em português.",
    )
    memory_service = FakeMemoryService([memoria])
    agent = FakeAgent()
    runtime = AgentRuntime(memory_service=memory_service)

    resultado = await runtime.executar(
        agent=agent,
        prompt="Como você deve responder?",
        user_id="user-01",
        session_id="session-01",
    )

    assert resultado.content == "Resposta simulada"
    assert len(memory_service.recall_calls) == 1
    assert memory_service.recall_calls[0] == {
        "agent_id": "agent-01",
        "user_id": "user-01",
        "session_id": "session-01",
        "limit": 20,
    }

    prompt_enviado = agent.calls[0]["prompt"]
    assert "O usuário prefere respostas em português." in prompt_enviado
    assert "Como você deve responder?" in prompt_enviado
    assert len(agent.calls) == 1


@pytest.mark.asyncio
async def test_runtime_isola_memorias_por_agente_usuario_e_sessao() -> None:
    class IsolatedMemoryService(FakeMemoryService):
        async def recall(
            self,
            *,
            agent_id: str,
            user_id: str,
            session_id: str | None = None,
            limit: int | None = None,
        ) -> list[FakeMemory]:
            await super().recall(
                agent_id=agent_id,
                user_id=user_id,
                session_id=session_id,
                limit=limit,
            )
            chave = (agent_id, user_id, session_id)
            return memorias_por_contexto[chave]

    memorias_por_contexto = {
        ("agent-a", "user-a", "session-a"): [
            FakeMemory(category="contexto", content="Dado exclusivo A")
        ],
        ("agent-b", "user-b", "session-b"): [
            FakeMemory(category="contexto", content="Dado exclusivo B")
        ],
    }
    memory_service = IsolatedMemoryService()
    runtime = AgentRuntime(memory_service=memory_service)
    agent_a = FakeAgent(agent_id="agent-a")
    agent_b = FakeAgent(agent_id="agent-b")

    await runtime.executar(
        agent=agent_a,
        prompt="Pergunta A",
        user_id="user-a",
        session_id="session-a",
    )
    await runtime.executar(
        agent=agent_b,
        prompt="Pergunta B",
        user_id="user-b",
        session_id="session-b",
    )

    prompt_a = agent_a.calls[0]["prompt"]
    prompt_b = agent_b.calls[0]["prompt"]

    assert "Dado exclusivo A" in prompt_a
    assert "Dado exclusivo B" not in prompt_a
    assert "Dado exclusivo B" in prompt_b
    assert "Dado exclusivo A" not in prompt_b
    assert [call["agent_id"] for call in memory_service.recall_calls] == [
        "agent-a",
        "agent-b",
    ]
    assert [call["user_id"] for call in memory_service.recall_calls] == [
        "user-a",
        "user-b",
    ]
    assert [call["session_id"] for call in memory_service.recall_calls] == [
        "session-a",
        "session-b",
    ]


@pytest.mark.asyncio
async def test_runtime_continua_sem_memoria_quando_fail_open_esta_ativo() -> None:
    memory_service = FakeMemoryService(
        error=RuntimeError("Banco de memória indisponível"),
        fail_open=True,
    )
    agent = FakeAgent()
    runtime = AgentRuntime(memory_service=memory_service)

    await runtime.executar(
        agent=agent,
        prompt="Prompt original",
        user_id="user-01",
        session_id="session-01",
    )

    assert len(agent.calls) == 1
    assert agent.calls[0]["prompt"] == "Prompt original"


@pytest.mark.asyncio
async def test_runtime_interrompe_execucao_quando_fail_open_esta_desativado() -> None:
    memory_service = FakeMemoryService(
        error=RuntimeError("Banco de memória indisponível"),
        fail_open=False,
    )
    agent = FakeAgent()
    runtime = AgentRuntime(memory_service=memory_service)

    with pytest.raises(RuntimeError, match="Banco de memória indisponível"):
        await runtime.executar(
            agent=agent,
            prompt="Prompt original",
            user_id="user-01",
            session_id="session-01",
        )

    assert agent.calls == []


@pytest.mark.asyncio
async def test_runtime_nao_consulta_memoria_quando_recurso_esta_desabilitado() -> None:
    memory_service = FakeMemoryService(enabled=False)
    agent = FakeAgent()
    runtime = AgentRuntime(memory_service=memory_service)

    await runtime.executar(
        agent=agent,
        prompt="Prompt sem memória",
        user_id="user-01",
        session_id="session-01",
    )

    assert memory_service.recall_calls == []
    assert len(agent.calls) == 1
    assert agent.calls[0]["prompt"] == "Prompt sem memória"


@pytest.mark.asyncio
async def test_runtime_remember_delega_persistencia_com_identidade_do_agente() -> None:
    memory_service = FakeMemoryService()
    agent = FakeAgent(agent_id="agent-financeiro")
    runtime = AgentRuntime(memory_service=memory_service)

    resultado = await runtime.remember(
        agent=agent,
        user_id="user-77",
        content="O cliente prefere receber cobranças por e-mail.",
        category="preferencia",
        session_id="session-77",
        metadata={"origem": "atendimento"},
    )

    assert resultado is memory_service.saved_memory
    assert len(memory_service.remember_calls) == 1
    chamada = memory_service.remember_calls[0]
    assert chamada["agent_id"] == "agent-financeiro"
    assert chamada["user_id"] == "user-77"
    assert chamada["content"] == "O cliente prefere receber cobranças por e-mail."
    assert chamada["category"] == "preferencia"
    assert chamada["session_id"] == "session-77"
    assert chamada["metadata"] == {"origem": "atendimento"}


@pytest.mark.asyncio
async def test_runtime_injeta_memorias_globais_e_da_sessao_atual() -> None:
    memorias = [
        FakeMemory(
            category="contexto",
            content="Memória global do usuário",
            session_id=None,
        ),
        FakeMemory(
            category="contexto",
            content="Memória da sessão atual",
            session_id="session-atual",
        ),
        FakeMemory(
            category="contexto",
            content="Memória de outra sessão",
            session_id="session-diferente",
        ),
    ]
    memory_service = FakeMemoryService(memorias)
    agent = FakeAgent()
    runtime = AgentRuntime(memory_service=memory_service)

    await runtime.executar(
        agent=agent,
        prompt="Pergunta atual",
        user_id="user-atual",
        session_id="session-atual",
    )

    prompt_enviado = agent.calls[0]["prompt"]

    assert "Memória global do usuário" in prompt_enviado
    assert "Memória da sessão atual" in prompt_enviado
    assert "Memória de outra sessão" not in prompt_enviado
    assert memory_service.recall_calls[0]["user_id"] == "user-atual"
    assert memory_service.recall_calls[0]["session_id"] == "session-atual"
