
from unittest.mock import AsyncMock

import pytest

from lkthink_agent.memory import MemoryConfig, MemoryService


class FakeMemoryStore:
    def __init__(self, database_url):
        self.database_url = database_url
        self.add = AsyncMock()
        self.list = AsyncMock(return_value=[])
        self.remove = AsyncMock(return_value=True)
        self.initialize = AsyncMock()
        self.close = AsyncMock()


@pytest.fixture
def memory_service(monkeypatch):
    import lkthink_agent.memory.service as service_module

    monkeypatch.setattr(
        service_module,
        "PostgresMemoryStore",
        FakeMemoryStore,
    )

    return MemoryService(
        database_url="postgresql+psycopg://test:test@localhost/test",
    )


@pytest.mark.asyncio
async def test_inicializa_store(memory_service):
    await memory_service.initialize()

    memory_service.store.initialize.assert_awaited_once()


@pytest.mark.asyncio
async def test_registra_memoria(memory_service):
    await memory_service.remember(
        agent_id="agent-01",
        user_id="user-01",
        content="Prefere relatórios em Excel.",
        category="preference",
    )

    memory_service.store.add.assert_awaited_once_with(
        agent_id="agent-01",
        user_id="user-01",
        content="Prefere relatórios em Excel.",
        session_id=None,
        category="preference",
        metadata=None,
    )


@pytest.mark.asyncio
async def test_remove_espacos_do_conteudo(memory_service):
    await memory_service.remember(
        agent_id=" agent-01 ",
        user_id=" user-01 ",
        content="  Informação importante.  ",
        category=" preference ",
    )

    memory_service.store.add.assert_awaited_once_with(
        agent_id="agent-01",
        user_id="user-01",
        content="Informação importante.",
        session_id=None,
        category="preference",
        metadata=None,
    )


@pytest.mark.asyncio
async def test_rejeita_identificadores_vazios(memory_service):
    with pytest.raises(ValueError):
        await memory_service.remember(
            agent_id="",
            user_id="user-01",
            content="Informação",
        )


@pytest.mark.asyncio
async def test_rejeita_conteudo_vazio(memory_service):
    with pytest.raises(ValueError):
        await memory_service.remember(
            agent_id="agent-01",
            user_id="user-01",
            content="   ",
        )


@pytest.mark.asyncio
async def test_rejeita_conteudo_acima_do_limite():
    service = MemoryService(
        database_url="postgresql+psycopg://test:test@localhost/test",
        config=MemoryConfig(max_content_length=10),
    )

    with pytest.raises(ValueError):
        await service.remember(
            agent_id="agent-01",
            user_id="user-01",
            content="Este conteúdo ultrapassa o limite.",
        )


@pytest.mark.asyncio
async def test_rejeita_categoria_vazia(memory_service):
    with pytest.raises(ValueError):
        await memory_service.remember(
            agent_id="agent-01",
            user_id="user-01",
            content="Informação",
            category="   ",
        )


@pytest.mark.asyncio
async def test_recupera_memorias(memory_service):
    await memory_service.recall(
        agent_id="agent-01",
        user_id="user-01",
        session_id="session-01",
    )

    memory_service.store.list.assert_awaited_once_with(
        agent_id="agent-01",
        user_id="user-01",
        session_id="session-01",
        limit=20,
    )


@pytest.mark.asyncio
async def test_permite_limite_personalizado(memory_service):
    await memory_service.recall(
        agent_id="agent-01",
        user_id="user-01",
        limit=5,
    )

    assert memory_service.store.list.await_args.kwargs["limit"] == 5


@pytest.mark.asyncio
async def test_remove_memoria(memory_service):
    resultado = await memory_service.forget(
        memory_id="memory-01",
        agent_id="agent-01",
        user_id="user-01",
    )

    assert resultado is True

    memory_service.store.remove.assert_awaited_once_with(
        memory_id="memory-01",
        agent_id="agent-01",
        user_id="user-01",
    )


@pytest.mark.asyncio
async def test_fecha_store(memory_service):
    await memory_service.close()

    memory_service.store.close.assert_awaited_once()
