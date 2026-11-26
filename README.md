# LKThink Agent
## Software Design Document — SDD

**Versão:** 0.3.0  
**Data:** 26/11/2026  
**Status:** Em desenvolvimento  
**Progresso estimado:** 72% concluído  
**Trabalho restante:** 28%

---

# 1. Visão geral

O LKThink Agent é uma biblioteca Python para construção, configuração, execução e gerenciamento de agentes inteligentes especializados.

O projeto tem como objetivo oferecer uma infraestrutura reutilizável para aplicações que precisam trabalhar com múltiplos agentes, ferramentas, memória, conhecimento contextual, observabilidade e integração com modelos de linguagem.

A biblioteca deve funcionar de maneira independente, podendo ser instalada por meio de:

```bash
pip install lkthink-agent
```

A aplicação consumidora deve conseguir criar agentes especializados, compartilhar um runtime, configurar provedores, conectar ferramentas e executar tarefas sem precisar conhecer os detalhes internos do motor de agentes.

O Agno será utilizado como motor interno de execução, sem expor seus objetos como parte da API pública principal.

# 2. Objetivos do projeto

- Construir uma biblioteca Python modular e extensível.
- Permitir múltiplos agentes especializados em uma mesma aplicação.
- Isolar configurações, ferramentas, memória e conhecimento por agente.
- Permitir compartilhamento controlado de infraestrutura.
- Suportar provedores diferentes de LLM e embeddings.
- Integrar ferramentas externas por MCP.
- Implementar memória operacional e recuperação contextual.
- Implementar RAG com PostgreSQL e pgvector.
- Disponibilizar observabilidade de execução.
- Permitir execução independente da biblioteca e futura integração HTTP.
- Preparar o pacote para distribuição pública.

## Fora do escopo inicial

- LangGraph como orquestrador principal.
- Treinamento ou fine-tuning automático de modelos.
- Persistência automática de todas as conversas como memória.
- Dependência obrigatória de uma API HTTP para utilizar a biblioteca.

# 3. Decisões arquiteturais

| Componente | Decisão |
|---|---|
| Linguagem | Python |
| Motor interno | Agno 3.2.1 |
| Banco principal | PostgreSQL |
| Banco vetorial | PostgreSQL + pgvector |
| LLM inicial | DeepSeek |
| Embeddings inicial | Jina |
| Comunicação com ferramentas | MCP |
| API futura | FastAPI |
| Containerização | Docker |
| Runtime | Compartilhado |
| MCP | Compartilhado sob demanda |
| Times de agentes | Híbridos |
| Frontend futuro | React |

A arquitetura deve priorizar baixo acoplamento, interfaces bem definidas e componentes plug-and-play.

O Core não deve carregar automaticamente arquivos `.env`. A aplicação consumidora será responsável pela configuração do ambiente.

# 4. Arquitetura modular

Estrutura lógica prevista:

```text
lkthink_agent/
├── agents/
├── execution/
├── providers/
├── knowledge/
├── memory/
├── tools/
├── mcp/
├── observability/
├── vectorstore/
├── api/
└── core/
```

## 4.1 Agents

Responsável pela criação, identidade, configuração e ciclo de vida dos agentes.

## 4.2 Execution

Responsável pelo runtime compartilhado, execução, normalização dos resultados e gerenciamento de contexto.

## 4.3 Providers

Responsável pela abstração dos provedores de LLM e embeddings.

## 4.4 Knowledge

Responsável pela ingestão, processamento, indexação e recuperação de conhecimento.

## 4.5 Memory

Responsável pela memória operacional e persistência explícita de informações.

## 4.6 Tools e MCP

Responsáveis pelo registro, isolamento e execução de ferramentas internas e externas.

## 4.7 Observability

Responsável por eventos, logs, métricas e rastreamento.

## 4.8 VectorStore

Responsável pela integração com armazenamento vetorial PostgreSQL/pgvector.

## 4.9 API

Camada futura de exposição HTTP, sem duplicar as regras do Core.

# 5. Gerenciamento de agentes

Cada agente deverá possuir:

- ID único.
- Slug único.
- Nome e identificação visual.
- Instruções próprias.
- Configuração individual.
- Provedor configurável.
- Ferramentas próprias ou explicitamente compartilhadas.
- Memória contextual.
- Conhecimento especializado.
- Ciclo de vida independente.

O `AgentManager` será responsável por:

- Registrar agentes.
- Buscar por ID ou slug.
- Impedir identificadores duplicados.
- Remover agentes.
- Encerrar recursos.
- Executar agentes pelo runtime compartilhado.

**Status:** Concluído na camada unitária.

Critérios validados:
- Normalização de ID e slug no AgentConfig.
- Rejeição de valores inválidos.
- Imutabilidade da configuração.
- Prevenção de IDs e slugs duplicados.
- Busca por ID e slug.
- Remoção e encerramento.
- Tratamento de falhas no fechamento.

Última validação: 31 testes aprovados e Ruff sem erros.

Pendente: integração completa com agentes reais, provedores e execução concorrente.

# 6. Runtime e execução

O `AgentRuntime` será compartilhado entre os agentes.

Responsabilidades:

- Executar agentes.
- Recuperar memórias antes da execução.
- Persistir memórias somente mediante solicitação explícita.
- Criar contexto de execução.
- Registrar logs.
- Registrar métricas.
- Criar spans de rastreamento.
- Normalizar resultados.
- Propagar erros de execução.

Cada execução deverá possuir contexto próprio, contendo:

- `trace_id`
- `run_id`
- `span_id`
- `tenant_id`
- `agent_id`
- `user_id`
- `session_id`

O isolamento deverá funcionar mesmo com múltiplas execuções concorrentes.

**Status:** Implementação principal existente.

Pendente:
- Testes de concorrência entre agentes.
- Testes de isolamento de ContextVar.
- Validação de ausência de vazamento de contexto.
- Testes de integração com agentes e provedores reais.

# 7. Providers

A camada Providers deverá abstrair os serviços de modelos de linguagem e embeddings.

## Implementação inicial

- DeepSeek para LLM.
- Jina para embeddings.

## Requisitos

- Interface comum para provedores.
- Configuração independente por agente.
- Possibilidade de adicionar novos provedores.
- Controle de parâmetros do modelo.
- Tratamento de erros.
- Controle de timeout.
- Normalização dos resultados.
- Métricas de tokens e custos quando disponibilizadas pelo provedor.

**Status:** Estrutura arquitetural definida.

Pendente:
- Validar criação de agente com DeepSeek.
- Executar chamadas reais.
- Validar retorno e métricas.
- Validar tratamento de falhas.
- Integrar o provider com o runtime.

# 8. Memory e Knowledge/RAG

## 8.1 Memory

A memória será operacional, persistente e separada do treinamento do modelo.

Escopos previstos:

- Agente.
- Usuário.
- Sessão.

A recuperação deverá respeitar os limites de contexto configurados.

A gravação será explícita, por meio de operações como `remember()`.

Não haverá gravação automática de todas as conversas inicialmente.

**Pendente de validação:** persistência e recuperação PostgreSQL ponta a ponta, isolamento de dados e testes de falha.

## 8.2 Knowledge/RAG

O módulo Knowledge deverá permitir:

- Ingestão de documentos.
- Extração e processamento de conteúdo.
- Divisão em chunks.
- Geração de embeddings com Jina.
- Armazenamento no PostgreSQL com pgvector.
- Busca por similaridade.
- Recuperação contextual.
- Associação de conhecimento aos agentes.

O RAG deverá funcionar de forma independente do provedor de LLM.

**Infraestrutura validada:** PostgreSQL 17 e pgvector 0.8.7.

**Pendente:**
- Fluxo completo de ingestão.
- Indexação vetorial.
- Recuperação semântica.
- Integração com o contexto do agente.
- Testes de isolamento por agente e tenant.

# 9. Tools e MCP

O sistema deverá permitir ferramentas locais e ferramentas externas via MCP.

## Tools

- Registro de ferramentas.
- Execução controlada.
- Isolamento por agente.
- Compartilhamento explícito.
- Observação de execução.
- Tratamento de falhas.

## MCP

- Conexão com servidores MCP.
- Descoberta de ferramentas.
- Lista de ferramentas permitidas.
- Registro no agente.
- Encerramento de conexões.
- Compartilhamento sob demanda.

**Status:** Estrutura e integração MCP existentes.

**Pendente:**
- Integração HTTP completa.
- Testes de reconexão.
- Testes de indisponibilidade.
- Políticas de timeout e falhas.
- Validação de ciclo de vida e compartilhamento.

# 10. Observabilidade

A observabilidade deverá ser parte nativa do runtime.

Componentes:

- EventLogger.
- MetricsRegistry.
- Tracer.
- ToolExecutionObserver.
- Contexto de execução.

Eventos importantes:

- Início e conclusão de execução.
- Falha de execução.
- Início e conclusão de ferramenta.
- Recuperação de memória.
- Persistência de memória.
- Falhas de integração.

## Persistência PostgreSQL

O exportador PostgreSQL foi implementado e validado.

Validações realizadas:
- Conexão com PostgreSQL.
- Persistência de eventos.
- Recuperação de eventos.
- Armazenamento de metadata JSONB.
- Armazenamento de payload JSONB.
- Emissão pelo EventLogger.
- Teste em container independente.

**Status:** Marco de persistência PostgreSQL validado.

Pendente:
- Cobertura ampliada de falhas.
- Testes de concorrência.
- Verificação de comportamento em produção.
- Integração de toda a telemetria ponta a ponta.

# 11. API, Docker e distribuição

## 11.1 API HTTP

A API será uma camada independente sobre o Core.

Tecnologia: FastAPI.

Funcionalidades previstas:
- Gerenciamento de agentes.
- Execução de agentes.
- Respostas em streaming.
- Controle de sessões.
- Autenticação e autorização.
- Identificação de tenants.
- Health checks.
- Observabilidade.

A API não deverá duplicar a lógica do runtime.

**Status:** Pendente de implementação e validação completa.

## 11.2 Docker

A biblioteca deverá funcionar em aplicações containerizadas.

A API deverá possuir container próprio e compartilhar o Core com a biblioteca Python.

Requisitos:
- Dockerfile.
- Docker Compose.
- PostgreSQL.
- pgvector.
- Configuração por variáveis de ambiente.
- Health checks.
- Persistência de dados.
- Inicialização e encerramento controlados.

**Validado:** imagem de verificação do pacote, imports públicos, conexão PostgreSQL, pgvector e persistência de eventos.

**Pendente:** Docker independente da API e validação de implantação completa.

## 11.3 Distribuição

O pacote deverá ser distribuível por PyPI.

Requisitos:
- `pyproject.toml`.
- Build de wheel.
- Build de sdist.
- Instalação em ambiente limpo.
- Imports públicos.
- Dependências corretas.
- Documentação.
- Versionamento semântico.
- Publicação e instalação via PyPI.

**Validado:** build e instalação de wheel em ambiente Docker isolado.

**Pendente:** validação completa do sdist, instalação final, documentação e publicação no PyPI.

# 12. Roadmap, critérios de aceite e acompanhamento

## 12.1 Marcos concluídos

- [x] Estrutura modular inicial.
- [x] Biblioteca instalável em modo editável.
- [x] Motor Agno integrado como dependência interna.
- [x] API pública com imports verificados.
- [x] PostgreSQL conectado.
- [x] pgvector disponível.
- [x] Exportador PostgreSQL de observabilidade validado.
- [x] Persistência e leitura de eventos validadas.
- [x] AgentConfig validado.
- [x] AgentManager validado.
- [x] Testes de ciclo de vida do AgentManager.
- [x] Ruff aprovado.
- [x] Wheel instalado em container independente.

## 12.2 Pendências prioritárias

### Fase 1 — Isolamento e integração do runtime
- [ ] Testes concorrentes de ContextVar.
- [ ] Isolamento de tenant, agente, usuário e sessão.
- [ ] Integração real AgentManager + AgentRuntime + LKThinkAgent.
- [ ] Execução real com DeepSeek.
- [ ] Validação de métricas e resultados do provider.

### Fase 2 — Memória e conhecimento
- [ ] Validar MemoryService com PostgreSQL.
- [ ] Validar persistência e recuperação de memória.
- [ ] Concluir ingestão de documentos.
- [ ] Concluir embeddings Jina.
- [ ] Implementar busca vetorial.
- [ ] Integrar RAG ao agente.

### Fase 3 — Ferramentas e integrações
- [ ] Finalizar MCP HTTP.
- [ ] Validar reconexão e falhas.
- [ ] Validar isolamento e compartilhamento de ferramentas.
- [ ] Testar execução de ferramentas com agentes reais.

### Fase 4 — API e infraestrutura
- [ ] Implementar API FastAPI.
- [ ] Implementar streaming.
- [ ] Implementar autenticação e autorização.
- [ ] Implementar isolamento de tenants na API.
- [ ] Criar Docker independente da API.
- [ ] Validar Docker Compose completo.

### Fase 5 — Qualidade e distribuição
- [ ] Testes de integração ponta a ponta.
- [ ] Testes de segurança.
- [ ] Ampliar cobertura de testes.
- [ ] Validar wheel e sdist.
- [ ] Documentação de instalação e uso.
- [ ] Exemplos funcionais.
- [ ] Publicação no PyPI.

## 12.3 Critérios finais de aceite

O projeto será considerado pronto para a primeira versão quando:

1. Uma aplicação conseguir instalar e importar a biblioteca.
2. Conseguir criar múltiplos agentes especializados.
3. Executar agentes com provedores reais.
4. Executar agentes simultaneamente sem mistura de contexto.
5. Utilizar ferramentas locais e MCP.
6. Recuperar conhecimento por RAG.
7. Persistir e recuperar memória com isolamento.
8. Registrar eventos, métricas e rastreamento.
9. Disponibilizar API HTTP com streaming e autenticação.
10. Executar a infraestrutura por Docker.
11. Passar nos testes automatizados e verificações estáticas.
12. Ser distribuível e instalável pelo PyPI.

---

## Acompanhamento geral

| Área | Situação |
|---|---|
| Arquitetura e estrutura | Implementada |
| AgentConfig / AgentManager | Validado |
| Runtime | Implementado; concorrência pendente |
| Providers | Integração real pendente |
| Memory | Integração final pendente |
| Knowledge/RAG | Integração pendente |
| Tools | Parcial |
| MCP | Parcial |
| Observabilidade PostgreSQL | Validada |
| API FastAPI | Pendente |
| Docker da biblioteca | Validado |
| Docker da API | Pendente |
| Distribuição | Parcial |
| Testes finais e segurança | Pendentes |

**Progresso estimado: 72% concluído — 28% restante.**

A estimativa será atualizada conforme cada marco passar pelos respectivos critérios de aceite. Implementação sem teste de integração não será contabilizada como concluída.

**Próximo marco obrigatório:** comprovar isolamento de contexto em execuções concorrentes no AgentRuntime compartilhado.