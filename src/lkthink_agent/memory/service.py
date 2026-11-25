from __future__ import annotations

from lkthink_agent.memory.config import MemoryConfig
from lkthink_agent.memory.models import MemoryItem
from lkthink_agent.memory.store import PostgresMemoryStore


class MemoryService:
    def __init__(
        self,
        database_url: str,
        config: MemoryConfig | None = None,
    ) -> None:
        self.config = config or MemoryConfig()
        self.store = PostgresMemoryStore(database_url)

    async def initialize(self) -> None:
        if self.config.enabled:
            await self.store.initialize()

    async def remember(
        self,
        *,
        agent_id: str,
        user_id: str,
        content: str,
        session_id: str | None = None,
        category: str = "general",
        metadata: dict | None = None,
    ) -> MemoryItem:
        if not self.config.enabled:
            raise RuntimeError("A memória está desabilitada.")

        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id é obrigatório.")

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id é obrigatório.")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("O conteúdo da memória não pode ser vazio.")

        if not isinstance(category, str) or not category.strip():
            raise ValueError("A categoria não pode ser vazia.")

        agent_id = agent_id.strip()
        user_id = user_id.strip()
        content = content.strip()
        category = category.strip()

        if session_id is not None:
            if not isinstance(session_id, str):
                raise ValueError("session_id precisa ser uma string.")
            session_id = session_id.strip() or None

        if len(content) > self.config.max_content_length:
            raise ValueError(
                "Conteúdo da memória excede o limite permitido."
            )

        return await self.store.add(
            agent_id=agent_id,
            user_id=user_id,
            content=content,
            session_id=session_id,
            category=category,
            metadata=metadata,
        )

    async def recall(
        self,
        *,
        agent_id: str,
        user_id: str,
        session_id: str | None = None,
        limit: int | None = None,
    ) -> list[MemoryItem]:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id é obrigatório.")

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id é obrigatório.")

        if not self.config.enabled:
            return []

        limite = self.config.max_items if limit is None else limit

        if not isinstance(limite, int) or isinstance(limite, bool) or limite < 1:
            raise ValueError("limit precisa ser um inteiro maior que zero.")

        if session_id is not None:
            if not isinstance(session_id, str):
                raise ValueError("session_id precisa ser uma string.")
            session_id = session_id.strip() or None

        return await self.store.list(
            agent_id=agent_id.strip(),
            user_id=user_id.strip(),
            session_id=session_id,
            limit=limite,
        )

    async def forget(
        self,
        *,
        memory_id: str,
        agent_id: str,
        user_id: str,
    ) -> bool:
        if not self.config.enabled:
            raise RuntimeError("A memória está desabilitada.")

        if not isinstance(memory_id, str) or not memory_id.strip():
            raise ValueError("memory_id é obrigatório.")

        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id é obrigatório.")

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id é obrigatório.")

        return await self.store.remove(
            memory_id=memory_id.strip(),
            agent_id=agent_id.strip(),
            user_id=user_id.strip(),
        )

    async def close(self) -> None:
        await self.store.close()
