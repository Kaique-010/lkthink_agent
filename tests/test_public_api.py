
import lkthink_agent
from lkthink_agent import (
    AgentConfig,
    AgentManager,
    AgentResult,
    AgentRuntime,
    LKThinkAgent,
)


def test_exports_publicos():
    assert lkthink_agent.AgentConfig is AgentConfig
    assert lkthink_agent.AgentManager is AgentManager
    assert lkthink_agent.AgentResult is AgentResult
    assert lkthink_agent.AgentRuntime is AgentRuntime
    assert lkthink_agent.LKThinkAgent is LKThinkAgent


def test_nao_expoe_engine_agno():
    assert not hasattr(lkthink_agent, "Agent")
