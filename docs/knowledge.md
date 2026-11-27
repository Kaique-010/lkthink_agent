# Knowledge e RAG

O módulo `lkthink_agent.knowledge` exporta `KnowledgeConfig` e `KnowledgeService`.

## Configuração

`KnowledgeConfig` recebe `database_url` e `jina_api_key` obrigatórios. Configurações opcionais: `embedding_model="jina-embeddings-v3"`, `embedding_dimensions=1024`, `chunk_size=900`, `chunk_overlap=100`, `top_k=5`, `schema="public"`, `vector_table="lkthink_vectors"`, `knowledge_table="lkthink_knowledge"` e `distance="cosine"`.

A configuração valida PostgreSQL, credencial Jina, dimensão, chunk size, overlap e top-k.

## Inicialização

```python
from lkthink_agent.knowledge import KnowledgeConfig, KnowledgeService

knowledge = KnowledgeService(KnowledgeConfig.from_env())
knowledge.initialize()
```

`initialize()` é síncrono e cria a estrutura do vector store quando necessário. Os métodos `add_text`, `search` e `count` também são síncronos nesta implementação.

## Inserir conteúdo

```python
knowledge.add_text(
    "Política de devolução: o prazo padrão é de 7 dias.",
    name="Politica de devolucao",
    metadata={"origem": "manual"},
    tenant_id="empresa-01",
    agent_id="suporte",
    user_id=None,
)
```

`add_text()` recebe o texto, nome opcional, metadados e escopo. Os campos `tenant_id` e `agent_id` são obrigatórios fora do contexto do Runtime. `user_id` é opcional.

## Consultar conteúdo

```python
documentos = knowledge.search(
    "Qual o prazo para devolução?",
    limit=5,
    tenant_id="empresa-01",
    agent_id="suporte",
)
```

Retorna uma lista de dicionários com `id`, `content` e `metadata`. `limit` deve ser positivo quando informado. Sem limite, utiliza `top_k`.

## Contagem

```python
total = knowledge.count(
    tenant_id="empresa-01",
    agent_id="suporte",
)
```

## Isolamento de escopo

O serviço filtra por `tenant_id` e `agent_id`; também repassa `user_id` ao mecanismo Knowledge/Vector Store. Quando existe contexto do Runtime, ele prevalece. Se o chamador informar um ID diferente do contexto, o serviço levanta `ValueError`. Fora do Runtime, `tenant_id` e `agent_id` precisam ser informados explicitamente.

Os campos `tenant_id` e `agent_id` são metadados reservados e são sobrescritos pelos valores resolvidos pelo serviço. Isso reduz o risco de um consumidor injetar escopo arbitrário por meio de `metadata`.
