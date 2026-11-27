# Observabilidade

O pacote `lkthink_agent.observability` contém eventos, contexto, logs, métricas, tracing, sanitização e exporters. Esses componentes podem ser injetados no `AgentRuntime`.

## Logger

`EventLogger` pode receber `ObservabilityConfig`, `ConsoleExporter`, caminho JSONL e `PostgresExporter`.

```python
from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.logger import EventLogger

logger = EventLogger(
    config=ObservabilityConfig(
        service_name="minha-api",
        environment="development",
        log_level="INFO",
        console_enabled=True,
        json_enabled=True,
        json_file="logs/minha-api.jsonl",
    )
)

logger.info("agent.started", "Agente iniciado", component="runtime")
```

Métodos de nível: `debug`, `info`, `warning`, `error` e `critical`. `emit()` é a operação central e aceita evento, mensagem, nível, status, componente, operação, duração, metadados e exceção.

## Configuração

`ObservabilityConfig` inclui `service_name`, `environment`, `version`, habilitação de console/JSON/PostgreSQL, `postgres_url`, `json_file`, cores, formatação, `log_level`, limites de mensagem/metadados e mapas de cores. Se `postgres_enabled=True`, `postgres_url` é obrigatória. Níveis válidos: `DEBUG`, `INFO`, `WARNING`, `ERROR` e `CRITICAL`.

## Métricas

`MetricsRegistry` mantém contadores e observações em memória:

```python
from lkthink_agent.observability.metrics import MetricsRegistry

metrics = MetricsRegistry()
metrics.increment("agent.requests", labels={"agent": "suporte"})
metrics.observe("agent.duration_ms", 125.4, labels={"agent": "suporte"})
print(metrics.snapshot())
```

Também oferece `get_counter`, `get_observations` e `reset`. Não confundir este registry em memória com um backend de métricas distribuído.

## Tracing

`Tracer.span(component, operation, metadata=...)` cria um `Span`, utilizável como context manager síncrono ou assíncrono (`with` / `async with`). O span registra duração e finalização, incluindo exceções.

## Exporters

- `ConsoleExporter`: saída humana/colorida.
- Export JSONL: configurado por `EventLogger(json_file=...)`.
- `PostgresExporter`: persistência PostgreSQL de eventos; inicialize e encerre conforme o ciclo de vida da aplicação.

## Sanitização e contexto

O módulo inclui funções para sanitizar texto, valores, metadados e exceções. O contexto usa helpers para obter, definir, limpar e criar contexto de execução. Evite registrar tokens, senhas, dados pessoais ou payloads sensíveis; sanitização não substitui classificação e política de dados da aplicação.
