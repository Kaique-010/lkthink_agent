
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from lkthink_agent.memory.models import (
    MemoryBase,
    MemoryItem,
    MemoryORM,
)


class PostgresMemoryStore:
    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise ValueError("database_url é obrigatório.")

        self.engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
        )

        self.sessions = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    async def initialize(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(
                MemoryBase.metadata.create_all
            )

    async def add(
        self,
        *,
        agent_id: str,
        user_id: str,
        content: str,
        session_id: str | None = None,
        category: str = "general",
        metadata: dict | None = None,
    ) -> MemoryItem:

        now = datetime.now(UTC)

        async with self.sessions() as session:
            record = MemoryORM(
                id=str(uuid4()),
                agent_id=agent_id,
                user_id=user_id,
                session_id=session_id,
                category=category,
                content=content,
                metadata_json=metadata or {},
                created_at=now,
                updated_at=now,
            )

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return self._to_item(record)

    async def list(
        self,
        *,
        agent_id: str,
        user_id: str,
        session_id: str | None = None,
        limit: int = 20,
    ) -> list[MemoryItem]:

        async with self.sessions() as session:
            query = select(MemoryORM).where(
                MemoryORM.agent_id == agent_id,
                MemoryORM.user_id == user_id,
            )

            if session_id is not None:
                query = query.where(
                    or_(
                        MemoryORM.session_id.is_(None),
                        MemoryORM.session_id == session_id,
                    )
                )
            else:
                query = query.where(
                    MemoryORM.session_id.is_(None)
                )

            query = (
                query
                .order_by(MemoryORM.updated_at.desc())
                .limit(limit)
            )

            result = await session.execute(query)

            return [
                self._to_item(record)
                for record in result.scalars().all()
            ]

    async def remove(
        self,
        *,
        memory_id: str,
        agent_id: str,
        user_id: str,
    ) -> bool:

        async with self.sessions() as session:
            result = await session.execute(
                delete(MemoryORM).where(
                    MemoryORM.id == memory_id,
                    MemoryORM.agent_id == agent_id,
                    MemoryORM.user_id == user_id,
                )
            )

            await session.commit()

            return bool(result.rowcount)

    async def close(self) -> None:
        await self.engine.dispose()

    @staticmethod
    def _to_item(record: MemoryORM) -> MemoryItem:
        return MemoryItem(
            id=record.id,
            agent_id=record.agent_id,
            user_id=record.user_id,
            session_id=record.session_id,
            category=record.category,
            content=record.content,
            metadata=record.metadata_json,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )