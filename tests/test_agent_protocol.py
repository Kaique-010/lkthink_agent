
from lkthink_agent.agents.abstractions import AgentProtocol


class FakeAgent:
    identity = object()

    async def executar(
        self,
        prompt: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
    ):
        return {"content": prompt}

    async def close(self) -> None:
        pass


def test_agente_implementa_contrato():
    agente: AgentProtocol = FakeAgent()

    assert agente.identity is not None
    assert callable(agente.executar)
    assert callable(agente.close)
