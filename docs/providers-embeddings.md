# Provedores, embeddings e vector store

## Provedor LLM

`BaseLLMProvider` define o contrato `build_model()`. A implementação fornecida é `DeepSeekProvider`, que cria um modelo Agno compatível com a API OpenAI usando `DeepSeekConfig`.

A configuração aceita `api_key`, `model`, `base_url`, `temperature`, `max_tokens` e `timeout`. Valida credencial, modelo, temperatura entre 0 e 2 e timeout positivo.

## Embeddings

O pacote `lkthink_agent.embeddings` exporta `BaseEmbedder` e `JinaEmbeddingProvider`.

O provider Jina é criado a partir de `KnowledgeConfig` e implementa `dimensions()`, `embed(text)` e `embed_batch(texts)`. A dimensão deve corresponder à dimensão configurada no vector store e ao modelo de embeddings escolhido.

## PgVectorStore

`PgVectorStore(config, embedder)` encapsula o vector store Agno/pgvector. Métodos públicos: `create()`, `exists()`, `count(filters=..., user_id=...)` e `drop()`.

`count()` exige `filters` não vazio; o código utiliza metadados para filtrar registros e considera o `user_id` no escopo de propriedade quando aplicável. `drop()` remove a estrutura do vector store: use com cautela, nunca como rotina de inicialização de produção.

## Limites

O pacote inclui um provider LLM DeepSeek e um provider de embeddings Jina. A abstração base abre caminho para extensões, mas não significa que existam implementações concretas para todos os provedores.
