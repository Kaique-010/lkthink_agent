# LKThink Agent — Exemplos de uso

Este guia demonstra como utilizar o **LKThink Agent** em aplicações Python. Os exemplos usam a API pública presente na versão `0.1.0` do pacote.

> Requisitos: Python 3.12 ou superior. Os exemplos que acessam DeepSeek, PostgreSQL, Jina ou servidores MCP dependem de serviços externos e de suas respectivas credenciais.

## Índice

1. [Instalação](#1-instalação)
2. [Configuração do DeepSeek](#2-configuração-do-deepseek)
3. [Criando e executando um agente](#3-criando-e-executando-um-agente)
4. [AgentManager e AgentRuntime](#4-agentmanager-e-agentruntime)
5. [Memória persistente](#5-memória-persistente)
6. [Knowledge Base com pgvector e Jina](#6-knowledge-base-com-pgvector-e-jina)
7. [Ferramentas MCP](#7-ferramentas-mcp)
8. [Orquestração sequencial e paralela](#8-orquestração-sequencial-e-paralela)
9. [Observabilidade](#9-observabilidade)
10. [Execução integrada](#10-execução-integrada)
11. [Variáveis de ambiente](#11-variáveis-de-ambiente)
12. [Cuidados de produção](#12-cuidados-de-produção)

---

## 1. Instalação

Instalação básica:

```bash
pip install lkthink-agent
```

Instalação com os recursos opcionais:

```bash
pip install "lkthink-agent[postgres,knowledge,mcp]"
```

Para desenvolvimento e execução dos testes:

```bash
pip install "lkthink-agent[postgres,knowledge,mcp,dev]"
```

Os extras são opcionais:

| Extra | Finalidade |
|---|---|
| `postgres` | Persistência PostgreSQL e dependências SQLAlchemy/pgvector |
| `knowledge` | Recursos adicionais de leitura de conteúdo e PDF |
| `mcp` | Integração com servidores MCP |
| `api` | FastAPI e Uvicorn |
| `dev` | Testes, Ruff e build |

## 2. Configuração do DeepSeek

O provider DeepSeek utiliza a API compatível com OpenAI por meio do adaptador interno do pacote.

Configure as variáveis de ambiente:

```env
DEEPSEEK_API_KEY=sua-chave
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_TEMPERATURE=0.2
DEEPSEEK_TIMEOUT=60
```

O carregamento do arquivo `.env` é responsabilidade da aplicação. Uma opção é instalar `python-dotenv`:

```bash
pip install python-dotenv
```

Crie `config.py` ou carregue as variáveis no ponto de entrada:

```python
from dotenv import load_dotenv

load_dotenv()
```

Instancie o provider:

```python
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider

config_provider = DeepSeekConfig.from_env()
provider = DeepSeekProvider(config_provider)
```

Também é possível informar a configuração diretamente:

```python
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider

provider = DeepSeekProvider(
    DeepSeekConfig(
        api_key="SUA_CHAVE",
        model="deepseek-chat",
        temperature=0.2,
    )
)
```

Não coloque chaves de API diretamente no repositório. Use variáveis de ambiente ou um gerenciador de segredos.

## 3. Criando e executando um agente

A API pública principal está disponível no pacote `lkthink_agent`.

```python
import asyncio

from lkthink_agent import AgentConfig, LKThinkAgent
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider


async def main():
    provider = DeepSeekProvider(DeepSeekConfig.from_env())

    config = AgentConfig(
        id="agent-suporte-001",
        slug="suporte",
        name="Agente de Suporte",
        label="Suporte",
        description="Agente responsável pelo atendimento inicial.",
        instructions=(
            "Você é um assistente de suporte técnico. "
            "Responda em português, com clareza e objetividade. "
            "Se não souber uma informação, deixe isso explícito."
        ),
        color="blue",
        markdown=True,
    )

    agent = LKThinkAgent(
        config=config,
        provider=provider,
    )

    try:
        response = await agent.executar(
            "Explique a diferença entre Django e FastAPI."
        )
        print(response.content)
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Campos do AgentConfig

| Campo | Descrição |
|---|---|
| `id` | Identificador único do agente |
| `slug` | Identificador legível para consulta no manager |
| `name` | Nome do agente |
| `label` | Rótulo usado na identificação/observabilidade |
| `instructions` | Instruções de comportamento |
| `description` | Descrição opcional |
| `color` | Cor identificadora |
| `markdown` | Habilita ou desabilita Markdown na resposta |

O método `executar()` retorna a resposta do mecanismo Agno. Quando a execução passa pelo `AgentRuntime`, o retorno é normalizado em `AgentResult`.

## 4. AgentManager e AgentRuntime

O `AgentManager` registra agentes, permite recuperá-los por ID ou slug e centraliza sua execução por meio do runtime.

```python
import asyncio

from lkthink_agent import (
    AgentConfig,
    AgentManager,
    LKThinkAgent,
)
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider


async def main():
    provider = DeepSeekProvider(DeepSeekConfig.from_env())

    agent = LKThinkAgent(
        config=AgentConfig(
            id="agent-analise-001",
            slug="analise",
            name="Analista",
            label="Analista",
            instructions="Analise solicitações técnicas e responda em português.",
        ),
        provider=provider,
    )

    manager = AgentManager()
    manager.register(agent)

    try:
        result = await manager.execute(
            "analise",  # Pode ser o slug ou o ID.
            "Liste três boas práticas para APIs Django REST.",
            user_id="usuario-123",
            session_id="sessao-456",
            tenant_id="empresa-001",
        )

        print("Conteúdo:", result.content)
        print("Agente:", result.agent_name)
        print("Run ID:", result.run_id)
        print("Duração (ms):", result.duration_ms)
        print("Tokens:", result.total_tokens)
    finally:
        await manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
```

`AgentManager()` cria um `AgentRuntime` padrão automaticamente. Também é possível injetar um runtime configurado, por exemplo, com memória e Knowledge:

```python
from lkthink_agent import AgentManager, AgentRuntime

runtime = AgentRuntime(
    memory_service=memory_service,
    knowledge_service=knowledge_service,
)

manager = AgentManager(runtime=runtime)
```

O runtime oferece:

- Contexto de execução por agente, usuário, sessão e tenant.
- Recuperação de memória antes da execução, quando configurada.
- Recuperação de conhecimento, quando configurada.
- Normalização do resultado em `AgentResult`.
- Logs, métricas e tracing.

A persistência de memória é explícita: o runtime recupera memórias, mas não grava automaticamente cada conversa. Use `MemoryService.remember()` para registrar informações deliberadamente.

## 5. Memória persistente

A memória utiliza PostgreSQL com SQLAlchemy assíncrono. Instale o extra:

```bash
pip install "lkthink-agent[postgres]"
```

A URL usada pelo serviço de memória deve ser compatível com o driver assíncrono, por exemplo:

```env
MEMORY_DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/lkthink
```

Exemplo completo:

```python
import asyncio
import os

from lkthink_agent.memory import MemoryConfig, MemoryService


async def main():
    memory = MemoryService(
        database_url=os.environ["MEMORY_DATABASE_URL"],
        config=MemoryConfig(
            enabled=True,
            fail_open=True,
            max_items=20,
            max_content_length=4000,
            max_context_chars=12000,
        ),
    )

    agent_id = "agent-suporte-001"
    user_id = "usuario-123"
    session_id = "sessao-456"

    try:
        await memory.initialize()

        item = await memory.remember(
            agent_id=agent_id,
            user_id=user_id,
            session_id=session_id,
            category="preferencia",
            content="O usuário prefere exemplos de código em Python.",
            metadata={"origem": "onboarding"},
        )

        print("Memória criada:", item.id)

        memorias = await memory.recall(
            agent_id=agent_id,
            user_id=user_id,
            session_id=session_id,
            limit=10,
        )

        for memoria in memorias:
            print(memoria.id, memoria.category, memoria.content)

        removida = await memory.forget(
            memory_id=item.id,
            agent_id=agent_id,
            user_id=user_id,
        )
        print("Memória removida:", removida)
    finally:
        await memory.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Integrando memória ao runtime

O `AgentRuntime` recupera as memórias do usuário antes de chamar o agente. Para isso, passe o serviço no construtor e informe `user_id` na execução:

```python
from lkthink_agent import AgentManager, AgentRuntime

runtime = AgentRuntime(memory_service=memory)
manager = AgentManager(runtime=runtime)

# Depois de registrar o agente:
result = await manager.execute(
    "suporte",
    "Qual linguagem de programação eu prefiro?",
    user_id="usuario-123",
    session_id="sessao-456",
)
```

O escopo da memória considera `agent_id`, `user_id` e `session_id`. Memórias globais do usuário (sem sessão) também podem ser recuperadas quando uma sessão é informada.

## 6. Knowledge Base com pgvector e Jina

O módulo Knowledge utiliza PostgreSQL, pgvector e embeddings da Jina. Instale os extras:

```bash
pip install "lkthink-agent[postgres,knowledge]"
```

Configure:

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/lkthink
JINA_API_KEY=sua-chave-jina
JINA_EMBEDDING_MODEL=jina-embeddings-v3
JINA_EMBEDDING_DIMENSIONS=1024
KNOWLEDGE_CHUNK_SIZE=900
KNOWLEDGE_CHUNK_OVERLAP=100
KNOWLEDGE_TOP_K=5
```

A configuração do Knowledge aceita `postgresql://` ou `postgresql+psycopg://`. Não use aqui a URL `postgresql+asyncpg://` do serviço de memória.

### Inicializar e inserir conhecimento

```python
import os

from lkthink_agent.knowledge import KnowledgeConfig, KnowledgeService

knowledge = KnowledgeService(
    KnowledgeConfig(
        database_url=os.environ["DATABASE_URL"],
        jina_api_key=os.environ["JINA_API_KEY"],
        embedding_model=os.getenv(
            "JINA_EMBEDDING_MODEL",
            "jina-embeddings-v3",
        ),
        embedding_dimensions=1024,
        chunk_size=900,
        chunk_overlap=100,
        top_k=5,
    )
)

knowledge.initialize()

knowledge.add_text(
    """
    A política de suporte estabelece que solicitações críticas
    devem ser encaminhadas imediatamente à equipe responsável.
    """
    ,
    name="Politica de suporte",
    tenant_id="empresa-001",
    agent_id="agent-suporte-001",
    user_id="usuario-123",
)

documentos = knowledge.search(
    "Qual é o procedimento para solicitações críticas?",
    tenant_id="empresa-001",
    agent_id="agent-suporte-001",
    user_id="usuario-123",
    limit=5,
)

for documento in documentos:
    print(documento["content"])
    print(documento["metadata"])
```

O método `add_text()` e a busca `search()` exigem `tenant_id` e `agent_id`. O `user_id` é opcional para essas operações diretas. Esses campos fazem parte do isolamento dos dados: mantenha os valores vinculados ao usuário autenticado e ao tenant correto.

### Integrando Knowledge ao runtime

Quando a busca é feita pelo runtime, o contexto de execução fornece `tenant_id`, `user_id` e identidade do agente. Portanto, passe os três identificadores na execução:

```python
from lkthink_agent import AgentManager, AgentRuntime

runtime = AgentRuntime(
    knowledge_service=knowledge,
    knowledge_fail_open=True,
)
manager = AgentManager(runtime=runtime)

# Depois de registrar o agente:
result = await manager.execute(
    "suporte",
    "Qual é o procedimento para solicitações críticas?",
    tenant_id="empresa-001",
    user_id="usuario-123",
)
```

O runtime injeta os documentos recuperados no prompt antes de executar o agente. `knowledge_fail_open=True` permite continuar a execução sem contexto recuperado caso a busca falhe. Para propagar a falha, use `False`.

## 7. Ferramentas MCP

O LKThink Agent pode conectar agentes a servidores MCP por `stdio` ou `http`. A criação com MCP é assíncrona e exige uma lista explícita de ferramentas autorizadas por servidor.

Instale:

```bash
pip install "lkthink-agent[mcp]"
```

### Servidor MCP via HTTP

```python
import asyncio

from lkthink_agent import AgentConfig, LKThinkAgent
from lkthink_agent.mcp import MCPServerConfig
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider


async def main():
    provider = DeepSeekProvider(DeepSeekConfig.from_env())

    servidor = MCPServerConfig(
        name="servico-clientes",
        transport="http",
        url="http://localhost:8000/mcp",
        timeout=30,
    )

    config = AgentConfig(
        id="agent-clientes-001",
        slug="clientes",
        name="Agente de Clientes",
        label="Clientes",
        instructions=(
            "Você consulta informações de clientes usando as ferramentas "
            "disponíveis. Não invente dados."
        ),
    )

    agent = await LKThinkAgent.criar_com_mcp(
        config=config,
        provider=provider,
        mcp_servers=[servidor],
        allowed_tools={
            "servico-clientes": [
                "consultar_cliente",
                "listar_clientes",
            ]
        },
    )

    try:
        resposta = await agent.executar(
            "Consulte o cliente de ID 10 e apresente os dados retornados."
        )
        print(resposta.content)
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Servidor MCP via STDIO

Para um servidor iniciado como processo local, configure `command`, `args` e, se necessário, `cwd`:

```python
import sys

from lkthink_agent.mcp import MCPServerConfig

servidor = MCPServerConfig(
    name="meu-servidor",
    transport="stdio",
    command=sys.executable,
    args=("caminho/para/servidor_mcp.py",),
    cwd="caminho/do/projeto",
)
```

O nome da chave em `allowed_tools` deve corresponder ao `name` do servidor. A lista deve conter somente ferramentas que o agente está autorizado a chamar. Sempre encerre o agente com `await agent.close()` para fechar as conexões MCP.

O repositório também contém um exemplo executável de integração MCP em `examples/test_agent_mcp.py` e um servidor de demonstração em `examples/mcp_server.py`.

## 8. Orquestração sequencial e paralela

A orquestração usa agentes previamente registrados em `AgentManager`. Cada etapa aceita `sequential` ou `parallel`.

```python
import asyncio

from lkthink_agent import (
    AgentConfig,
    AgentManager,
    AgentRuntime,
    LKThinkAgent,
)
from lkthink_agent.orchestration import (
    TeamConfig,
    TeamOrchestrator,
    TeamStageConfig,
)
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider


async def main():
    provider = DeepSeekProvider(DeepSeekConfig.from_env())
    manager = AgentManager(runtime=AgentRuntime())

    agentes = [
        LKThinkAgent(
            AgentConfig(
                id="pesquisador",
                slug="pesquisador",
                name="Pesquisador",
                label="Pesquisa",
                instructions="Pesquise e liste os fatos relevantes para a solicitação.",
            ),
            provider,
        ),
        LKThinkAgent(
            AgentConfig(
                id="analista",
                slug="analista",
                name="Analista",
                label="Análise",
                instructions="Analise o problema e identifique riscos e oportunidades.",
            ),
            provider,
        ),
        LKThinkAgent(
            AgentConfig(
                id="revisor",
                slug="revisor",
                name="Revisor",
                label="Revisão",
                instructions="Consolide os resultados anteriores em uma resposta final.",
            ),
            provider,
        ),
    ]

    for agent in agentes:
        manager.register(agent)

    equipe = TeamConfig(
        id="equipe-produto",
        name="Equipe de Produto",
        stages=(
            TeamStageConfig(
                name="levantamento",
                agent_ids=("pesquisador", "analista"),
                mode="parallel",
                max_concurrency=2,
            ),
            TeamStageConfig(
                name="consolidacao",
                agent_ids=("revisor",),
                mode="sequential",
            ),
        ),
        fail_fast=True,
    )

    orchestrator = TeamOrchestrator(manager)

    try:
        resultado = await orchestrator.executar(
            equipe,
            "Avalie os riscos de migrar um sistema monolítico para microsserviços.",
            tenant_id="empresa-001",
            user_id="usuario-123",
            session_id="sessao-equipe-001",
        )

        print("Resultados:", resultado.total_resultados)
        print("Falhas:", resultado.total_falhas)

        for etapa, resultados in resultado.stage_results.items():
            print(f"\nEtapa: {etapa}")
            for item in resultados:
                print(item.agent_name)
                print(item.content)
    finally:
        await manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
```

### Modos disponíveis

- `sequential`: executa os agentes da etapa em sequência.
- `parallel`: executa os agentes da etapa em paralelo, respeitando `max_concurrency` quando configurado.

Uma equipe pode ter várias etapas, combinando esses modos. Isso permite, por exemplo, uma primeira etapa paralela de pesquisa e análise seguida de uma etapa sequencial de revisão. Não existe um modo literal `hybrid`: o comportamento combinado é definido pela composição de etapas sequenciais e paralelas.

Com `fail_fast=True`, uma falha interrompe a execução das próximas etapas. Com `fail_fast=False`, o orquestrador registra falhas e tenta continuar.

## 9. Observabilidade

O `AgentRuntime` cria automaticamente um `EventLogger`, um `MetricsRegistry` e um `Tracer`. Eles também podem ser configurados e injetados.

### Consultar métricas

```python
from lkthink_agent import AgentRuntime

runtime = AgentRuntime()

runtime.metrics.increment(
    "app.requests",
    labels={"route": "/chat"},
)
runtime.metrics.observe(
    "app.response_time_ms",
    125.4,
    labels={"route": "/chat"},
)

print(
    runtime.metrics.get_counter(
        "app.requests",
        labels={"route": "/chat"},
    )
)

for snapshot in runtime.metrics.snapshot():
    print(snapshot)
```

### Emitir eventos

```python
runtime.logger.info(
    event="application.started",
    message="Aplicação iniciada.",
    component="application",
    operation="startup",
    metadata={"environment": "development"},
)
```

O logger pode exportar eventos para console e JSONL. Para configurar:

```python
from lkthink_agent import AgentRuntime
from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.logger import EventLogger

observability = ObservabilityConfig(
    service_name="minha-api",
    environment="production",
    console_enabled=True,
    json_enabled=True,
    json_file="logs/agentes.jsonl",
)

logger = EventLogger(config=observability)
runtime = AgentRuntime(logger=logger)
```

### Tracing manual

```python
with runtime.tracer.span(
    component="application",
    operation="processar-pedido",
    metadata={"pedido_id": "PED-100"},
):
    # Execute aqui a operação que deseja rastrear.
    processar_pedido()
```

O tracer também suporta contexto assíncrono:

```python
async with runtime.tracer.span(
    component="application",
    operation="processar-evento",
):
    await processar_evento()
```

### Persistir eventos no PostgreSQL

O logger possui integração opcional com PostgreSQL. Instale o extra `postgres` e configure:

```python
from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.logger import EventLogger

config = ObservabilityConfig(
    console_enabled=True,
    json_enabled=False,
    postgres_enabled=True,
    postgres_url="postgresql+psycopg://usuario:senha@localhost:5432/lkthink",
)

logger = EventLogger(config=config)
```

A inicialização do exporter cria a tabela `lkthink_agent_events` e seus índices. A URL deve usar um driver síncrono compatível com SQLAlchemy, como `postgresql+psycopg://`.

## 10. Execução integrada

Este exemplo reúne DeepSeek, agente, memória, Knowledge e observabilidade. Ele pressupõe que PostgreSQL, pgvector, as credenciais DeepSeek e Jina estejam configurados.

```python
import asyncio
import os

from dotenv import load_dotenv

from lkthink_agent import (
    AgentConfig,
    AgentManager,
    AgentRuntime,
    LKThinkAgent,
)
from lkthink_agent.knowledge import KnowledgeConfig, KnowledgeService
from lkthink_agent.memory import MemoryConfig, MemoryService
from lkthink_agent.observability.config import ObservabilityConfig
from lkthink_agent.observability.logger import EventLogger
from lkthink_agent.providers import DeepSeekConfig, DeepSeekProvider


async def main():
    load_dotenv()

    memory = MemoryService(
        database_url=os.environ["MEMORY_DATABASE_URL"],
        config=MemoryConfig(enabled=True, fail_open=True),
    )
    await memory.initialize()

    knowledge = KnowledgeService(
        KnowledgeConfig(
            database_url=os.environ["DATABASE_URL"],
            jina_api_key=os.environ["JINA_API_KEY"],
        )
    )
    knowledge.initialize()

    # Insira documentos no escopo correto antes da execução.
    knowledge.add_text(
        "O prazo padrão de atendimento é de dois dias úteis.",
        name="Politica de atendimento",
        tenant_id="empresa-001",
        agent_id="agent-atendimento-001",
        user_id="usuario-123",
    )

    logger = EventLogger(
        config=ObservabilityConfig(
            service_name="demo-lkthink",
            environment="development",
            console_enabled=True,
            json_enabled=True,
            json_file="logs/demo.jsonl",
        )
    )

    runtime = AgentRuntime(
        logger=logger,
        memory_service=memory,
        knowledge_service=knowledge,
    )
    manager = AgentManager(runtime=runtime)

    agent = LKThinkAgent(
        config=AgentConfig(
            id="agent-atendimento-001",
            slug="atendimento",
            name="Atendimento",
            label="Atendimento",
            instructions=(
                "Responda com base no conhecimento recuperado. "
                "Se a informação não estiver disponível, informe isso."
            ),
        ),
        provider=DeepSeekProvider(DeepSeekConfig.from_env()),
    )
    manager.register(agent)

    try:
        await memory.remember(
            agent_id="agent-atendimento-001",
            user_id="usuario-123",
            content="O usuário prefere respostas objetivas.",
            category="preferencia",
        )

        resultado = await manager.execute(
            "atendimento",
            "Qual é o prazo padrão de atendimento?",
            tenant_id="empresa-001",
            user_id="usuario-123",
            session_id="sessao-001",
        )

        print(resultado.content)
        print("Run ID:", resultado.run_id)
        print("Duração:", resultado.duration_ms)
        print("Tokens:", resultado.total_tokens)
    finally:
        await manager.close_all()
        await memory.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## 11. Variáveis de ambiente

Exemplo de `.env` para os recursos apresentados:

```env
# DeepSeek
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_TEMPERATURE=0.2
DEEPSEEK_TIMEOUT=60

# PostgreSQL para Knowledge (driver síncrono)
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/lkthink

# PostgreSQL para Memory (driver assíncrono)
MEMORY_DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/lkthink

# Jina
JINA_API_KEY=
JINA_EMBEDDING_MODEL=jina-embeddings-v3
JINA_EMBEDDING_DIMENSIONS=1024

# Knowledge
KNOWLEDGE_CHUNK_SIZE=900
KNOWLEDGE_CHUNK_OVERLAP=100
KNOWLEDGE_TOP_K=5
```

Use um `.env` local e mantenha-o fora do controle de versão. O arquivo `.env.example` pode ser versionado desde que contenha somente valores fictícios ou vazios.

## 12. Cuidados de produção

- **Segredos:** não grave API keys, senhas ou tokens no código, nos logs ou no Git.
- **Isolamento:** derive `tenant_id` e `user_id` da identidade autenticada; não confie em valores enviados livremente pelo cliente.
- **Knowledge:** as operações exigem escopo de tenant e agente. O runtime também exige `user_id` para realizar a recuperação automática.
- **Memória:** a recuperação automática não grava conversas. Persista somente informações selecionadas com `remember()`.
- **MCP:** autorize explicitamente as ferramentas em `allowed_tools` e encerre o agente com `await close()`.
- **Ciclo de vida:** feche `AgentManager` e `MemoryService` no encerramento da aplicação.
- **Falhas:** escolha conscientemente `fail_open` da memória e `knowledge_fail_open` do runtime conforme a criticidade da aplicação.
- **Banco:** configure backups, usuários com privilégios mínimos, TLS quando aplicável e políticas de retenção.
- **Versões:** fixe e valide versões das dependências em ambientes de produção.

---

## Referência da API pública

Imports centrais da versão `0.1.0`:

```python
from lkthink_agent import (
    AgentConfig,
    AgentManager,
    AgentResult,
    AgentRuntime,
    LKThinkAgent,
)

from lkthink_agent.providers import (
    DeepSeekConfig,
    DeepSeekProvider,
)

from lkthink_agent.memory import (
    MemoryConfig,
    MemoryItem,
    MemoryService,
)

from lkthink_agent.knowledge import (
    KnowledgeConfig,
    KnowledgeService,
)

from lkthink_agent.mcp import MCPServerConfig

from lkthink_agent.orchestration import (
    TeamConfig,
    TeamOrchestrator,
    TeamStageConfig,
)
```

Este documento descreve a API e os comportamentos presentes no pacote `0.1.0`. Consulte o README principal para visão geral, arquitetura, roadmap e informações do projeto.
