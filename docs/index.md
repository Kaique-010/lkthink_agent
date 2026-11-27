# Documentação do LKThink Agent

**Versão documentada:** `0.1.1` — conforme `pyproject.toml` e artefatos do pacote enviados.

Esta documentação descreve a implementação encontrada em `src/lkthink_agent/`. A API pública é a exportada pelos `__init__.py` dos módulos; classes internas e métodos iniciados por `_` são detalhes de implementação, salvo quando explicitamente citados.

## Guias

1. [Instalação e configuração](installation.md)
2. [Agentes, runtime e gerenciamento](agents-runtime.md)
3. [Orquestração de equipes](orchestration.md)
4. [Memória persistente](memory.md)
5. [Knowledge e RAG](knowledge.md)
6. [Ferramentas e MCP](tools-mcp.md)
7. [Observabilidade](observability.md)
8. [Provedores, embeddings e vector store](providers-embeddings.md)
9. [Referência completa da API](api-reference.md)
10. [Limites e notas da versão](version-notes.md)

## Caminho recomendado

- Comece pela instalação e configure apenas o provedor que pretende utilizar.
- Crie um `AgentConfig`, um `DeepSeekProvider` e um `LKThinkAgent`.
- Registre o agente em `AgentManager` e execute-o pelo `AgentRuntime`.
- Acrescente memória, Knowledge, ferramentas e MCP apenas quando necessários.
- Para múltiplos agentes, configure `TeamConfig` e `TeamOrchestrator`.

## Regra de escopo

O `KnowledgeService` exige `tenant_id` e `agent_id` quando chamado fora do contexto de execução do Runtime. Dentro do Runtime, o contexto de execução é a fonte de autoridade e valores divergentes são rejeitados. A memória utiliza `agent_id` e `user_id` nas operações.
