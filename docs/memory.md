# Memória persistente

O módulo `lkthink_agent.memory` exporta `MemoryConfig`, `MemoryItem` e `MemoryService`.

## Configuração

`MemoryConfig`:

- `enabled=True`: habilita o recurso.
- `fail_open=True`: indica a política de tolerância a falhas usada pelo Runtime.
- `max_items=20`: limite padrão de itens recuperados.
- `max_content_length=4000`: tamanho máximo configurado para conteúdo.
- `max_context_chars=12000`: limite de caracteres para contexto montado.

Os limites devem ser positivos.

## Inicialização e uso

```python
from lkthink_agent.memory import MemoryConfig, MemoryService

memory = MemoryService(
    database_url="postgresql+asyncpg://usuario:senha@localhost:5432/app",
    config=MemoryConfig(max_items=20),
)
await memory.initialize()

item = await memory.remember(
    agent_id="assistente-vendas",
    user_id="usuario-123",
    content="O usuário prefere relatórios resumidos.",
    session_id="sessao-abc",
    category="preference",
    metadata={"source": "chat"},
)

memorias = await memory.recall(
    agent_id="assistente-vendas",
    user_id="usuario-123",
    session_id="sessao-abc",
)

await memory.close()
```

## Operações

- `initialize()`: prepara o armazenamento.
- `remember(...)`: grava conteúdo com agente, usuário, sessão opcional, categoria e metadados.
- `recall(...)`: recupera memórias para agente/usuário, com sessão e limite opcionais.
- `forget(memory_id=..., agent_id=..., user_id=...)`: remove uma memória respeitando os identificadores informados.
- `close()`: encerra os recursos de banco.

O escopo de acesso da memória é baseado em `agent_id` e `user_id`; `session_id` pode restringir a consulta a uma sessão. A aplicação deve autenticar o usuário e fornecer IDs confiáveis, não aceitar esses identificadores cegamente do cliente.
