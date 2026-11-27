# Notas e limites da versão 0.1.1

Este documento foi escrito após inspeção do ZIP enviado em 27/11/2026. A versão declarada no `pyproject.toml` é `0.1.1` e o arquivo `dist/` contém artefatos `0.1.1`.

## Correções de alinhamento feitas nesta documentação

- O README original ainda menciona `0.1.0` ao descrever a combinação de etapas sequenciais e paralelas. O código atual permite configurar uma lista de etapas, cada uma com `sequential` ou `parallel`; esta documentação descreve o comportamento observado no código.
- `KnowledgeService.add_text`, `search` e `count` são síncronos. Não devem ser documentados como `async`.
- Fora do Runtime, `KnowledgeService` exige `tenant_id` e `agent_id`. Dentro do Runtime, o contexto prevalece e IDs divergentes geram `ValueError`.
- `MemoryService` é assíncrono e escopa operações por `agent_id` e `user_id`.
- O `MetricsRegistry` fornecido mantém métricas em memória; não é, por si só, um serviço de métricas distribuído.

## Validação executada durante a documentação

A suíte de testes não pôde ser executada neste ambiente. A primeira tentativa não encontrou o pacote no `sys.path`; com `PYTHONPATH=src`, a coleta parou porque a dependência `agno` não está instalada. Portanto, não há declaração de que os testes passaram nesta revisão.

Para validar no ambiente do projeto:

```bash
pip install -e ".[postgres,knowledge,mcp,dev]"
python -m pytest -q
python -m ruff check src tests
python -m build
```

## Itens para revisão futura

- Incluir docstrings de parâmetros/retornos/exceções diretamente nas classes e métodos públicos; a documentação externa não substitui docstrings no código.
- Definir e documentar uma política única de inicialização e encerramento para `KnowledgeService`, `MemoryService`, agentes e MCP.
- Adicionar testes de integração executáveis em CI com PostgreSQL/pgvector e servidores MCP de teste.
- Revisar dependências opcionais: confirmar que cada extra instala todas as dependências necessárias para o módulo correspondente.
- Evitar incluir `.env`, logs, caches, `.git` e artefatos locais em arquivos ZIP de distribuição/compartilhamento.
