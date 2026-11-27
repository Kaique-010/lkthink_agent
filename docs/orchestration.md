# Orquestração de equipes

O módulo `lkthink_agent.orchestration` exporta `TeamStageConfig`, `TeamConfig`, `TeamExecutionContext`, `TeamAgentFailure`, `TeamAggregator` e `TeamOrchestrator`.

## Etapas

`TeamStageConfig` contém:

- `name`: nome único da etapa dentro da equipe.
- `agent_ids`: tupla não vazia de IDs registrados no `AgentManager`; não pode repetir IDs.
- `mode`: `"sequential"` ou `"parallel"`.
- `max_concurrency`: limite opcional maior que zero, relevante para paralelismo.

## Equipe

`TeamConfig` contém `id`, `name`, `stages`, `fail_fast=True` e `metadata={}`. Deve possuir ao menos uma etapa e nomes de etapas únicos.

## Exemplo

```python
from lkthink_agent.orchestration import (
    TeamConfig, TeamStageConfig, TeamOrchestrator,
)

team = TeamConfig(
    id="analise-pedido",
    name="Análise de Pedido",
    stages=(
        TeamStageConfig(
            name="analise",
            agent_ids=("comercial", "financeiro"),
            mode="parallel",
            max_concurrency=2,
        ),
        TeamStageConfig(
            name="consolidacao",
            agent_ids=("sintetizador",),
            mode="sequential",
        ),
    ),
    fail_fast=False,
)

orchestrator = TeamOrchestrator(manager)
resultado = await orchestrator.executar(
    team,
    "Analise o pedido 123.",
    tenant_id="empresa-01",
    user_id="usuario-123",
    session_id="sessao-abc",
)
```

O exemplo pressupõe que os três agentes já estejam registrados no `manager`. A equipe é composta por etapas ordenadas; cada etapa escolhe execução sequencial ou paralela. `fail_fast` define a política de interrupção diante de falhas. O contexto registra resultados e falhas por etapa; `TeamAggregator` consolida resultados.

## Observação

A implementação declara dois modos de etapa: `sequential` e `parallel`. Uma equipe pode combinar etapas desses dois modos. Não documentar isso como execução paralela distribuída: o código entregue implementa coordenação assíncrona dentro do processo.
