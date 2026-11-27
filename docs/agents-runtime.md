# Agentes, Runtime e gerenciamento

## AgentConfig

Configuração imutável de agente (`frozen=True`, `slots=True`). Campos obrigatórios: `id`, `slug`, `name`, `label` e `instructions`. Campos opcionais: `description=""`, `color="blue"` e `markdown=True`. Os campos obrigatórios devem ser strings não vazias; `id` e `slug` são normalizados com `strip()`.

## Criar um agente

```python
from lkthink_agent.agents import AgentConfig, LKThinkAgent
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider

agent_config = AgentConfig(
    id="assistente-vendas",
    slug="assistente-vendas",
    name="Assistente de Vendas",
    label="Vendas",
    instructions="Ajude a equipe com dúvidas sobre vendas.",
)
provider = DeepSeekProvider(DeepSeekConfig.from_env())
agent = LKThinkAgent(config=agent_config, provider=provider)
```

`LKThinkAgent` implementa o protocolo de agente da biblioteca e expõe `executar()` e `close()`. O método `criar_com_mcp()` é uma factory assíncrona que configura integração com servidores MCP e uma lista explícita de ferramentas permitidas por servidor.

## AgentManager

O gerenciador mantém agentes por identificador:

```python
from lkthink_agent.agents import AgentManager

manager = AgentManager()
manager.register(agent)
print(manager.list_agents())
resultado = await manager.execute(
    "assistente-vendas",
    "Resuma o papel deste agente.",
    user_id="usuario-123",
    session_id="sessao-abc",
)
await manager.close_all()
```

Operações disponíveis: `register`, `get`, `remove`, `remove_and_close`, `close_all`, `list_agents`, `execute`, `exists`, `len(manager)` e `identifier in manager`. `remove()` remove do registro; `remove_and_close()` também encerra o agente.

## AgentRuntime

O Runtime centraliza a execução e pode receber `EventLogger`, `MetricsRegistry`, `Tracer`, `MemoryService` e `KnowledgeService`. Também recebe `knowledge_fail_open`, que controla se uma falha na recuperação de Knowledge deve impedir a execução do agente.

```python
from lkthink_agent.execution import AgentRuntime

runtime = AgentRuntime()
resultado = await runtime.executar(
    agent,
    "Explique o processo de vendas.",
    user_id="usuario-123",
    session_id="sessao-abc",
    tenant_id="empresa-01",
)
```

`AgentRuntime.executar()` recebe a instância do agente, o prompt e os identificadores opcionais `user_id`, `session_id` e `tenant_id`. `AgentRuntime.remember()` grava memória explicitamente para um agente e usuário.

## Ciclo de vida

Encerre os recursos assíncronos que a aplicação criou. Se usar `MemoryService` ou agentes com conexões MCP, execute seus métodos de encerramento (`close()` / `close_all()`) no encerramento controlado da aplicação.
