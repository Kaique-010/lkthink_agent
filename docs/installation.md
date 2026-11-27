# Instalação e configuração

## Requisitos identificados

- Python `>=3.12` (definido em `pyproject.toml`).
- PostgreSQL para memória e Knowledge.
- Extensão `pgvector` para armazenamento vetorial.
- Credenciais do provedor de LLM e, se utilizar RAG, do serviço de embeddings Jina.

## Instalação

```bash
pip install lkthink-agent
```

Extras declarados pelo pacote:

```bash
pip install "lkthink-agent[postgres,knowledge,mcp,api]"
```

| Extra | Dependências declaradas | Uso |
|---|---|---|
| `postgres` | SQLAlchemy asyncio, asyncpg, psycopg, pgvector | Persistência PostgreSQL e vetores |
| `knowledge` | aiohttp, pypdf | Dependências auxiliares do domínio Knowledge |
| `mcp` | mcp | Cliente MCP |
| `api` | FastAPI e Uvicorn | Dependências para camada HTTP da aplicação consumidora |
| `dev` | pytest, pytest-asyncio, ruff, build, python-dotenv | Desenvolvimento e testes |

Para desenvolver a partir do repositório:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -e ".[postgres,knowledge,mcp,api,dev]"
```

## DeepSeek

`DeepSeekConfig` aceita configuração direta ou leitura do ambiente:

```python
import os
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider

config = DeepSeekConfig.from_env()
provider = DeepSeekProvider(config)
```

Variáveis lidas por `from_env()`:

| Variável | Padrão |
|---|---|
| `DEEPSEEK_API_KEY` | Obrigatória |
| `DEEPSEEK_MODEL` | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` |
| `DEEPSEEK_TEMPERATURE` | `0.2` |
| `DEEPSEEK_MAX_TOKENS` | Sem limite explícito (`None`) |
| `DEEPSEEK_TIMEOUT` | `60` segundos |

## PostgreSQL / memória

`MemoryService` recebe `database_url` diretamente:

```python
from lkthink_agent.memory import MemoryConfig, MemoryService

memory = MemoryService(
    database_url=os.environ["DATABASE_URL"],
    config=MemoryConfig(enabled=True, fail_open=True),
)
await memory.initialize()
```

A implementação de memória usa SQLAlchemy assíncrono. Utilize uma URL compatível com o driver assíncrono, normalmente `postgresql+asyncpg://...`.

## Knowledge / embeddings

`KnowledgeConfig.from_env()` lê:

| Variável | Padrão |
|---|---|
| `DATABASE_URL` | Obrigatória; PostgreSQL |
| `JINA_API_KEY` | Obrigatória |
| `JINA_EMBEDDING_MODEL` | `jina-embeddings-v3` |
| `JINA_EMBEDDING_DIMENSIONS` | `1024` |
| `KNOWLEDGE_CHUNK_SIZE` | `900` |
| `KNOWLEDGE_CHUNK_OVERLAP` | `100` |
| `KNOWLEDGE_TOP_K` | `5` |

Exemplo:

```python
from lkthink_agent.knowledge import KnowledgeConfig, KnowledgeService

knowledge = KnowledgeService(KnowledgeConfig.from_env())
knowledge.initialize()  # inicialização síncrona
```

A URL aceita pelo `KnowledgeConfig` deve começar com `postgresql://` ou `postgresql+psycopg://`.

## Segredos

Não versionar `.env` real, tokens, chaves ou URLs com senha. Versione apenas arquivos de exemplo sem valores reais. Em caso de exposição, revogue e gere novas credenciais.
