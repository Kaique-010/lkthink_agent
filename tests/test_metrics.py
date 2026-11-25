
from lkthink_agent.observability.metrics import MetricsRegistry


def test_incrementa_contador():
    metrics = MetricsRegistry()

    assert metrics.increment("agent.executions") == 1
    assert metrics.increment("agent.executions") == 2


def test_separa_metricas_por_agente():
    metrics = MetricsRegistry()

    metrics.increment(
        "agent.executions",
        labels={"agent_id": "agent-01"},
    )
    metrics.increment(
        "agent.executions",
        labels={"agent_id": "agent-02"},
    )

    assert metrics.get_counter(
        "agent.executions",
        labels={"agent_id": "agent-01"},
    ) == 1


def test_calcula_estatisticas():
    metrics = MetricsRegistry()

    metrics.observe("agent.duration_ms", 100)
    metrics.observe("agent.duration_ms", 200)
    metrics.observe("agent.duration_ms", 300)

    snapshot = metrics.snapshot()[0]

    assert snapshot.count == 3
    assert snapshot.total == 600
    assert snapshot.minimum == 100
    assert snapshot.maximum == 300
    assert snapshot.mean == 200


def test_nao_confunde_ausencia_com_zero_observado():
    metrics = MetricsRegistry()

    assert metrics.get_observations("llm.total_tokens") == ()

    metrics.observe("llm.total_tokens", 0)

    assert metrics.get_observations("llm.total_tokens") == (0.0,)


def test_reset():
    metrics = MetricsRegistry()

    metrics.increment("agent.executions")
    metrics.observe("agent.duration_ms", 100)

    metrics.reset()

    assert metrics.get_counter("agent.executions") == 0
    assert metrics.snapshot() == ()
