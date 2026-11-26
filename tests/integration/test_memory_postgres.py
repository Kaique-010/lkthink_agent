import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy.exc import OperationalError

from lkthink_agent.memory.service import MemoryService


def test_memory_postgres_persistence_and_isolation():
    database_url = os.getenv("LKTHINK_TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("LKTHINK_TEST_DATABASE_URL nao configurada.")

    async def scenario():
        suffix = uuid4().hex

        agent_id = f"integration-agent-{suffix}"
        user_id = f"integration-user-{suffix}"

        service = MemoryService(database_url)
        created_memories = []

        try:
            await service.initialize()

            # 1. Criar memorias globais e especificas de sessao.
            global_memory = await service.remember(
                agent_id=agent_id,
                user_id=user_id,
                content="Preferencia global do usuario",
                category="preference",
                metadata={"source": "integration_test"},
            )
            created_memories.append(global_memory)

            session_a_memory = await service.remember(
                agent_id=agent_id,
                user_id=user_id,
                session_id="session-a",
                content="Informacao exclusiva da sessao A",
            )
            created_memories.append(session_a_memory)

            session_b_memory = await service.remember(
                agent_id=agent_id,
                user_id=user_id,
                session_id="session-b",
                content="Informacao exclusiva da sessao B",
            )
            created_memories.append(session_b_memory)

            # 2. Fechar e recriar o servico para validar persistencia.
            await service.close()

            service = MemoryService(database_url)
            await service.initialize()

            # 3. Recuperar memorias da sessao A.
            memories_a = await service.recall(
                agent_id=agent_id,
                user_id=user_id,
                session_id="session-a",
            )

            contents_a = {item.content for item in memories_a}

            assert "Preferencia global do usuario" in contents_a
            assert "Informacao exclusiva da sessao A" in contents_a
            assert "Informacao exclusiva da sessao B" not in contents_a

            # 4. Recuperar memorias da sessao B.
            memories_b = await service.recall(
                agent_id=agent_id,
                user_id=user_id,
                session_id="session-b",
            )

            contents_b = {item.content for item in memories_b}

            assert "Preferencia global do usuario" in contents_b
            assert "Informacao exclusiva da sessao B" in contents_b
            assert "Informacao exclusiva da sessao A" not in contents_b

            # 5. Sem sessao, recuperar somente memorias globais.
            global_memories = await service.recall(
                agent_id=agent_id,
                user_id=user_id,
            )

            assert [item.content for item in global_memories] == [
                "Preferencia global do usuario"
            ]

            # 6. Validar isolamento entre agentes e usuarios.
            other_agent = await service.recall(
                agent_id=f"other-agent-{suffix}",
                user_id=user_id,
            )
            assert other_agent == []

            other_user = await service.recall(
                agent_id=agent_id,
                user_id=f"other-user-{suffix}",
            )
            assert other_user == []

            # 7. Validar persistencia dos metadados.
            persisted_global = next(
                item for item in global_memories
                if item.id == global_memory.id
            )
            assert persisted_global.metadata == {
                "source": "integration_test"
            }

            # 8. Validar protecao contra exclusao por outro usuario.
            deleted_by_other_user = await service.forget(
                memory_id=session_a_memory.id,
                agent_id=agent_id,
                user_id=f"other-user-{suffix}",
            )
            assert deleted_by_other_user is False

            # 9. Excluir memoria com o escopo correto.
            deleted = await service.forget(
                memory_id=session_a_memory.id,
                agent_id=agent_id,
                user_id=user_id,
            )
            assert deleted is True

            remaining = await service.recall(
                agent_id=agent_id,
                user_id=user_id,
                session_id="session-a",
            )

            assert all(
                item.id != session_a_memory.id
                for item in remaining
            )

        finally:
            # Limpar exclusivamente os registros deste teste.
            for memory in created_memories:
                try:
                    await service.forget(
                        memory_id=memory.id,
                        agent_id=agent_id,
                        user_id=user_id,
                    )
                except OperationalError:
                    pass

            await service.close()

    # SelectorEventLoop funciona no Windows e tambem no Linux.
    asyncio.run(
        scenario(),
        loop_factory=asyncio.SelectorEventLoop,
    )
