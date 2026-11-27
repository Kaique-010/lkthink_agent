# Referência de API — inventário de código

Este inventário lista classes e funções encontradas em `src/lkthink_agent/`. Assinaturas foram extraídas do código-fonte enviado. Métodos com prefixo `_` são privados/internos e não constituem API estável.

## `lkthink_agent/agents/abstractions/base.py`
### `class AgentProtocol`
- `async executar(self, prompt: str, *, user_id: str | None=None, session_id: str | None=None)`
- `async close(self)`

## `lkthink_agent/agents/agent.py`
### `class LKThinkAgent`
- `__init__(self, config: AgentConfig, provider: BaseLLMProvider, tools: ToolRegistry | None=None)`
- `async criar_com_mcp(cls, config: AgentConfig, provider: BaseLLMProvider, *, mcp_servers: list[MCPServerConfig], allowed_tools: dict[str, list[str]], tools: ToolRegistry | None=None)`
- `async executar(self, prompt: str, *, user_id: str | None=None, session_id: str | None=None)`
- `async close(self)`

## `lkthink_agent/agents/config.py`
### `class AgentConfig`
- `__post_init__(self)`

## `lkthink_agent/agents/manager.py`
### `class AgentManager`
- `__init__(self, runtime: AgentRuntime | None=None)`
- `register(self, agent: AgentProtocol)`
- `get(self, identifier: str)`
- `remove(self, identifier: str)`
- `async remove_and_close(self, identifier: str)`
- `async close_all(self)`
- `list_agents(self)`
- `async execute(self, agent_id: str, prompt: str, *, user_id: str | None=None, session_id: str | None=None, tenant_id: str | None=None)`
- `exists(self, identifier: str)`
- `__len__(self)`
- `__contains__(self, identifier: str)`

## `lkthink_agent/embeddings/base.py`
### `class BaseEmbedder`
- `embed(self, text: str)`
- `embed_batch(self, texts: list[str])`
- `dimensions(self)`

## `lkthink_agent/embeddings/jina.py`
### `class JinaEmbeddingProvider`
- `__init__(self, config: KnowledgeConfig)`
- `dimensions(self)`
- `embed(self, text: str)`
- `embed_batch(self, texts: list[str])`

## `lkthink_agent/execution/runtime.py`
### `class AgentResult`
### `class AgentRuntime`
- `__init__(self, logger: EventLogger | None=None, metrics: MetricsRegistry | None=None, tracer: Tracer | None=None, memory_service: MemoryService | None=None, knowledge_service: KnowledgeService | None=None, knowledge_fail_open: bool=True)`
- `_extrair_metricas(resposta: Any)`
- `_labels(agent_id: str, model: str | None, provider: str | None)`
- `_registrar_metricas_sucesso(self, *, labels: dict[str, str], duration_ms: float, metricas: dict[str, Any])`
- `_montar_prompt_com_memorias(prompt: str, memorias: list[Any], limite: int)`
- `async _recuperar_memorias(self, *, agent: AgentProtocol, user_id: str | None, session_id: str | None)`
- `async _recuperar_conhecimento(self, *, prompt: str, agent: AgentProtocol)`
- `_montar_prompt_com_conhecimento(prompt: str, documentos: list[dict[str, Any]], limite: int=6000)`
- `async executar(self, agent: AgentProtocol, prompt: str, *, user_id: str | None=None, session_id: str | None=None, tenant_id: str | None=None)`
- `async remember(self, agent: AgentProtocol, *, user_id: str, content: str, session_id: str | None=None, category: str='general', metadata: dict[str, Any] | None=None)`

## `lkthink_agent/knowledge/chunking.py`
- `criar_estrategia_chunking(config: KnowledgeConfig)`

## `lkthink_agent/knowledge/config.py`
### `class KnowledgeConfig`
- `__post_init__(self)`
- `from_env(cls)`

## `lkthink_agent/knowledge/reader.py`
- `criar_text_reader(config: KnowledgeConfig)`

## `lkthink_agent/knowledge/service.py`
### `class KnowledgeService`
- `__init__(self, config: KnowledgeConfig)`
- `initialize(self)`
- `_resolver_escopo(self, *, tenant_id: str | None=None, agent_id: str | None=None, user_id: str | None=None)`
- `add_text(self, text: str, *, name: str | None=None, metadata: dict[str, Any] | None=None, tenant_id: str | None=None, agent_id: str | None=None, user_id: str | None=None)`
- `search(self, query: str, *, limit: int | None=None, tenant_id: str | None=None, agent_id: str | None=None, user_id: str | None=None)`
- `count(self, *, tenant_id: str | None=None, agent_id: str | None=None, user_id: str | None=None)`
- `_ensure_initialized(self)`

## `lkthink_agent/mcp/adapter.py`
### `class MCPToolAdapter`
- `async registrar(self, client: MCPClient, registry: ToolRegistry, *, allowed_tools: list[str])`

## `lkthink_agent/mcp/client.py`
### `class MCPConnectionError`
### `class MCPToolExecutionError`
### `class MCPClient`
- `__init__(self, config: MCPServerConfig)`
- `connected(self)`
- `async connect(self)`
- `async list_tools(self)`
- `async call_tool(self, name: str, arguments: dict[str, Any] | None=None)`
- `_serialize_result(result: Any)`
- `_require_session(self)`
- `async close(self)`

## `lkthink_agent/mcp/config.py`
### `class MCPServerConfig`
- `__post_init__(self)`

## `lkthink_agent/mcp/manager.py`
### `class MCPManager`
- `__init__(self)`
- `register_adapter(self, name: str, adapter: MCPToolAdapter)`
- `register_server(self, config: MCPServerConfig)`
- `get_client(self, name: str)`
- `async connect_server(self, config: MCPServerConfig)`
- `async connect_all(self)`
- `async list_tools(self, config: MCPServerConfig)`
- `async register_tools(self, registry: ToolRegistry, *, config: MCPServerConfig, allowed_tools: list[str])`
- `async close_server(self, config: MCPServerConfig)`
- `async close_all(self)`
- `list_servers(self)`

## `lkthink_agent/mcp/models.py`
### `class MCPTool`

## `lkthink_agent/memory/config.py`
### `class MemoryConfig`
- `__post_init__(self)`

## `lkthink_agent/memory/models.py`
### `class MemoryBase`
### `class MemoryORM`
### `class MemoryItem`

## `lkthink_agent/memory/service.py`
### `class MemoryService`
- `__init__(self, database_url: str, config: MemoryConfig | None=None)`
- `async initialize(self)`
- `async remember(self, *, agent_id: str, user_id: str, content: str, session_id: str | None=None, category: str='general', metadata: dict | None=None)`
- `async recall(self, *, agent_id: str, user_id: str, session_id: str | None=None, limit: int | None=None)`
- `async forget(self, *, memory_id: str, agent_id: str, user_id: str)`
- `async close(self)`

## `lkthink_agent/memory/store.py`
### `class PostgresMemoryStore`
- `__init__(self, database_url: str)`
- `async initialize(self)`
- `async add(self, *, agent_id: str, user_id: str, content: str, session_id: str | None=None, category: str='general', metadata: dict | None=None)`
- `async list(self, *, agent_id: str, user_id: str, session_id: str | None=None, limit: int=20)`
- `async remove(self, *, memory_id: str, agent_id: str, user_id: str)`
- `async close(self)`
- `_to_item(record: MemoryORM)`

## `lkthink_agent/observability/config.py`
- `_cores_agentes()`
- `_cores_componentes()`
- `_cores_niveis()`
### `class ObservabilityConfig`
- `__post_init__(self)`
- `obter_cor_agente(self, label: str)`
- `obter_cor_componente(self, component: str)`
- `obter_cor_nivel(self, level: str)`

## `lkthink_agent/observability/context.py`
- `gerar_id()`
### `class AgentIdentity`
### `class ObservabilityContext`
- `criar_span(self, component: str, operation: str, metadata: dict | None=None)`
- `obter_contexto()`
- `definir_contexto(contexto: ObservabilityContext)`
- `limpar_contexto(token: Token)`
- `criar_contexto_execucao(*, tenant_id: str | None=None, agent: AgentIdentity | None=None, metadata: dict | None=None)`

## `lkthink_agent/observability/events.py`
### `class LogLevel`
### `class EventName`
### `class LogEvent`
- `to_dict(self)`
- `criar_evento(*, event: EventName | str, message: str, level: LogLevel=LogLevel.INFO, status: str | None=None, context: ObservabilityContext | None=None, component: str | None=None, operation: str | None=None, duration_ms: float | None=None, metadata: dict[str, Any] | None=None, error: Exception | None=None)`

## `lkthink_agent/observability/exporters/console.py`
### `class ConsoleExporter`
- `__init__(self, config: ObservabilityConfig, stream=None, force_color: bool | None=None)`
- `export(self, evento: dict[str, Any])`
- `_obter_identidade(self, evento: dict[str, Any])`
- `_obter_label_componente(self, component: str)`
- `_obter_detalhes(self, evento: dict[str, Any])`
- `_formatar_horario(self, timestamp: str | None)`
- `_colorir(self, texto: str, cor: str, bold: bool=False)`

## `lkthink_agent/observability/exporters/postgres.py`
### `class PostgresExporter`
- `__init__(self, database_url: str, *, engine: Engine | None=None, fail_silently: bool=True)`
- `initialize(self)`
- `_serializar(valor: Any)`
- `export(self, evento: dict[str, Any])`
- `close(self)`

## `lkthink_agent/observability/logger.py`
### `class EventLogger`
- `__init__(self, config: ObservabilityConfig | None=None, console_exporter: ConsoleExporter | None=None, json_file: str | Path | None=None, postgres_exporter: PostgresExporter | None=None)`
- `_inicializar_postgres(self)`
- `_deve_emitir(self, level: LogLevel)`
- `emit(self, event: EventName | str, message: str, *, level: LogLevel=LogLevel.INFO, status: str | None=None, component: str | None=None, operation: str | None=None, duration_ms: float | None=None, metadata: dict[str, Any] | None=None, error: Exception | None=None)`
- `_exportar(self, evento: dict[str, Any])`
- `_executar_exporter(self, *, nome: str, executar: Callable[[dict[str, Any]], None], evento: dict[str, Any])`
- `_reportar_falha_exporter(nome: str, erro: Exception)`
- `_exportar_console(self, evento: dict[str, Any])`
- `_exportar_json(self, evento: dict[str, Any])`
- `_exportar_postgres(self, evento: dict[str, Any])`
- `debug(self, event: EventName | str, message: str, **kwargs)`
- `info(self, event: EventName | str, message: str, **kwargs)`
- `warning(self, event: EventName | str, message: str, **kwargs)`
- `error(self, event: EventName | str, message: str, **kwargs)`
- `critical(self, event: EventName | str, message: str, **kwargs)`

## `lkthink_agent/observability/metrics.py`
### `class MetricSnapshot`
### `class MetricsRegistry`
- `__init__(self)`
- `_normalizar_labels(labels: Mapping[str, str] | None)`
- `_validar_nome(name: str)`
- `increment(self, name: str, value: float=1, *, labels: Mapping[str, str] | None=None)`
- `observe(self, name: str, value: float, *, labels: Mapping[str, str] | None=None)`
- `get_counter(self, name: str, *, labels: Mapping[str, str] | None=None)`
- `get_observations(self, name: str, *, labels: Mapping[str, str] | None=None)`
- `snapshot(self)`
- `reset(self)`

## `lkthink_agent/observability/sanitization.py`
- `_normalizar_chave(chave: str)`
- `_campo_sensivel(chave: str)`
- `sanitizar_texto(texto: str, limite: int=LIMITE_TEXTO)`
- `sanitizar_valor(valor: Any, chave: str | None=None, limite: int=LIMITE_TEXTO)`
- `sanitizar_metadata(metadata: dict[str, Any] | None)`
- `sanitizar_excecao(erro: BaseException)`

## `lkthink_agent/observability/tool_execution.py`
### `class ToolExecutionObserver`
- `obter_observador()`
- `definir_observador(observador: ToolExecutionObserver)`
- `limpar_observador(token: Token)`
- `_registrar_metricas(observador: ToolExecutionObserver, nome: str, duracao_ms: float, *, sucesso: bool)`
- `observar_ferramenta(observador: ToolExecutionObserver, nome: str)`

## `lkthink_agent/observability/tracing.py`
### `class Span`
- `__init__(self, *, logger: EventLogger, component: str, operation: str, metadata: dict[str, Any] | None=None)`
- `duration_ms(self)`
- `_iniciar(self)`
- `_congelar_duracao(self)`
- `_finalizar(self, error: BaseException | None=None)`
- `_restaurar_contexto(self)`
- `__enter__(self)`
- `__exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None)`
- `async __aenter__(self)`
- `async __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None)`
### `class Tracer`
- `__init__(self, logger: EventLogger | None=None)`
- `span(self, component: str, operation: str, *, metadata: dict[str, Any] | None=None)`

## `lkthink_agent/orchestration/aggregator.py`
### `class TeamAggregator`
- `agregar(self, context: TeamExecutionContext, *, stage_names: tuple[str, ...] | None=None)`
- `_formatar_conteudo(content: Any)`

## `lkthink_agent/orchestration/config.py`
### `class TeamStageConfig`
- `__post_init__(self)`
### `class TeamConfig`
- `__post_init__(self)`

## `lkthink_agent/orchestration/context.py`
### `class TeamAgentFailure`
### `class TeamExecutionContext`
- `__post_init__(self)`
- `registrar_resultado(self, stage_name: str, resultado: Any)`
- `registrar_falha(self, stage_name: str, agent_id: str, erro: Exception)`
- `obter_resultados_etapa(self, stage_name: str)`
- `obter_todos_resultados(self)`
- `total_resultados(self)`
- `total_falhas(self)`
- `execution_prompt(self)`

## `lkthink_agent/orchestration/executors/base.py`
### `class BaseExecutor`
- `async executar(self, manager: Any, stage: TeamStageConfig, context: TeamExecutionContext, *, fail_fast: bool=True)`

## `lkthink_agent/orchestration/executors/parallel.py`
### `class ParallelExecutor`
- `async executar(self, manager: Any, stage: TeamStageConfig, context: TeamExecutionContext, *, fail_fast: bool=True)`

## `lkthink_agent/orchestration/executors/sequential.py`
### `class SequentialExecutor`
- `async executar(self, manager: Any, stage: TeamStageConfig, context: TeamExecutionContext, *, fail_fast: bool=True)`

## `lkthink_agent/orchestration/orchestrator.py`
### `class TeamOrchestrator`
- `__init__(self, manager: Any, *, aggregator: TeamAggregator | None=None)`
- `async executar(self, config: TeamConfig, prompt: str, *, tenant_id: str | None=None, user_id: str | None=None, session_id: str | None=None)`

## `lkthink_agent/providers/base.py`
### `class BaseLLMProvider`
- `build_model(self)`

## `lkthink_agent/providers/deepseek.py`
### `class DeepSeekConfig`
- `__post_init__(self)`
- `from_env(cls)`
### `class DeepSeekProvider`
- `__init__(self, config: DeepSeekConfig)`
- `build_model(self)`

## `lkthink_agent/tools/adapters/agno.py`
### `class AgnoToolAdapter`
- `_instrumentar(func: Callable[..., Any], nome: str)`
- `adaptar(self, registry: ToolRegistry)`

## `lkthink_agent/tools/base.py`
### `class BaseTool`
- `execute(self, **kwargs: Any)`

## `lkthink_agent/tools/definition.py`
### `class ToolDefinition`
- `__post_init__(self)`

## `lkthink_agent/tools/registry.py`
### `class ToolRegistry`
- `__init__(self)`
- `register(self, func: Callable[..., Any] | BaseTool, *, name: str | None=None, description: str | None=None, strict: bool=False, parameters: dict[str, Any] | None=None)`
- `unregister(self, name: str)`
- `get(self, name: str)`
- `list_tools(self)`
- `exists(self, name: str)`
- `clear(self)`
- `__len__(self)`
- `__contains__(self, name: str)`

## `lkthink_agent/vectorstores/pgvector.py`
### `class PgVectorStore`
- `__init__(self, config: KnowledgeConfig, embedder: JinaEmbeddingProvider)`
- `create(self)`
- `exists(self)`
- `count(self, *, filters: dict, user_id: str | None=None)`
- `drop(self)`

## Exports públicos de pacote

O pacote raiz (`import lkthink_agent`) exporta `AgentConfig`, `AgentManager`, `AgentResult`, `AgentRuntime` e `LKThinkAgent`. Os exports de cada subpacote estão descritos nos guias e nos respectivos `__init__.py`.
