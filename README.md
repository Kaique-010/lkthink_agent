# LKThink Agent

**Modular Agent Engineering — Framework Python para construção, execução e orquestração de agentes de Inteligência Artificial.**

[![PyPI version](https://img.shields.io/pypi/v/lkthink-agent)](https://pypi.org/project/lkthink-agent/)
[![Python](https://img.shields.io/pypi/pyversions/lkthink-agent)](https://pypi.org/project/lkthink-agent/)
[![License](https://img.shields.io/pypi/l/lkthink-agent)](LICENSE)

O **LKThink Agent** é um framework modular desenvolvido em Python para facilitar a construção de aplicações baseadas em agentes de Inteligência Artificial.

Construído sobre Python e Agno, oferece uma arquitetura própria para gerenciamento de agentes, execução controlada, orquestração de equipes, memória persistente, recuperação contextual de conhecimento (RAG), integração com ferramentas externas e observabilidade.

O objetivo é fornecer uma base de engenharia extensível e independente do provedor de modelos de linguagem, permitindo que diferentes componentes sejam utilizados individualmente ou combinados em arquiteturas multiagentes.

O Agno funciona como mecanismo interno de execução. O LKThink Agent disponibiliza sua própria camada de gerenciamento, contexto, orquestração e integração.

---

## Índice

- [Visão geral](#visão-geral)
- [Principais recursos](#principais-recursos)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Extras opcionais](#extras-opcionais)
- [Configuração](#configuração)
- [Componentes](#componentes)
- [Gerenciamento de agentes](#gerenciamento-de-agentes)
- [Orquestração](#orquestração)
- [Memória persistente](#memória-persistente)
- [Knowledge e RAG](#knowledge-e-rag)
- [Ferramentas e MCP](#ferramentas-e-mcp)
- [Observabilidade](#observabilidade)
- [Isolamento de contexto](#isolamento-de-contexto)
- [Testes](#testes)
- [Build e distribuição](#build-e-distribuição)
- [Atualizações e versionamento](#atualizações-e-versionamento)
- [Roadmap](#roadmap)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Visão geral

O LKThink Agent foi projetado para resolver desafios comuns no desenvolvimento de aplicações baseadas em agentes de IA:

- Gerenciamento centralizado de agentes.
- Execução isolada e controlada.
- Orquestração de múltiplos agentes.
- Compartilhamento controlado de ferramentas.
- Memória persistente por escopo.
- Recuperação contextual de conhecimento.
- Integração com servidores MCP.
- Rastreamento de execuções e eventos.
- Isolamento de contexto entre usuários, agentes e organizações.

A biblioteca utiliza uma arquitetura modular, permitindo que os recursos sejam utilizados separadamente, sem obrigar a aplicação a adotar uma estrutura monolítica.

## Principais recursos

| Recurso | Descrição |
|---|---|
| Agent Manager | Registro, consulta, execução e remoção de agentes |
| Agent Runtime | Ambiente controlado de execução |
| Agent Protocol | Contrato estrutural para agentes |
| Orchestration | Coordenação de múltiplos agentes |
| Sequential Execution | Execução sequencial |
| Parallel Execution | Execução paralela |
| Memory | Persistência de memória em PostgreSQL |
| Knowledge | Gerenciamento de conhecimento e RAG |
| Embeddings | Integração com modelos de embeddings |
| Vector Store | Armazenamento vetorial com pgvector |
| Tool Registry | Registro e execução de ferramentas |
| MCP | Integração com servidores MCP |
| Observability | Eventos, logs e rastreamento |
| Context Isolation | Isolamento de contexto por execução |

---

## Arquitetura

O LKThink Agent utiliza uma arquitetura modular organizada por responsabilidades.

```text
LKThink Agent
│
├── agents/
│   ├── protocols
│   ├── config
│   ├── manager
│   └── runtime
│
├── orchestration/
│   ├── config
│   ├── context
│   ├── orchestrator
│   ├── aggregator
│   └── executors/
│       ├── base
│       ├── sequential
│       └── parallel
│
├── memory/
│   ├── config
│   └── service
│
├── knowledge/
│   ├── config
│   ├── reader
│   ├── chunking
│   └── service
│
├── embeddings/
│   ├── base
│   └── jina
│
├── vectorstores/
│   └── pgvector
│
├── tools/
│   ├── registry
│   └── adapters
│
├── mcp/
│   ├── clients
│   ├── discovery
│   └── permissions
│
└── observability/
    ├── context
    ├── events
    └── exporters/
        └── postgres
```

### Princípios arquiteturais

**Modularidade**

Cada domínio possui responsabilidades próprias e pode evoluir independentemente.

**Baixo acoplamento**

A aplicação não precisa depender diretamente do Agno para acessar os recursos de gerenciamento e orquestração do LKThink Agent.

**Extensibilidade**

Novos provedores, agentes, ferramentas, executores e mecanismos de armazenamento podem ser incorporados à arquitetura.

**Execução controlada**

O Runtime centraliza a execução dos agentes e propaga o contexto operacional.

**Isolamento**

Os contextos de execução permitem separar informações de diferentes agentes, usuários e organizações.

## Tecnologias

| Tecnologia | Finalidade |
|---|---|
| Python 3.12+ | Linguagem principal |
| Agno 3.2.x | Engine interna de agentes |
| PostgreSQL | Persistência |
| pgvector | Armazenamento vetorial |
| SQLAlchemy | Acesso e gerenciamento de banco |
| DeepSeek | Provedor de modelos de linguagem |
| Jina | Embeddings |
| MCP | Integração com ferramentas externas |
| Ruff | Qualidade e padronização do código |
| Pytest | Testes automatizados |

---

## Instalação

### Requisitos

- Python 3.12 ou superior.
- PostgreSQL para recursos de persistência.
- Extensão pgvector para funcionalidades vetoriais.
- Docker opcional, recomendado para infraestrutura local.

### Instalação básica pelo PyPI

```bash
pip install lkthink-agent
```

### Instalação com todas as integrações

```bash
pip install "lkthink-agent[postgres,knowledge,mcp,api]"
```

### Instalação por funcionalidades

PostgreSQL e memória:

```bash
pip install "lkthink-agent[postgres]"
```

Knowledge e RAG:

```bash
pip install "lkthink-agent[knowledge]"
```

Integração MCP:

```bash
pip install "lkthink-agent[mcp]"
```

API com FastAPI:

```bash
pip install "lkthink-agent[api]"
```

### Instalação para desenvolvimento

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd lkthink-agent
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux:

```bash
source .venv/bin/activate
```

Instale o pacote em modo editável com as dependências de desenvolvimento:

```bash
pip install -e ".[postgres,knowledge,mcp,api,dev]"
```

---

## Configuração

As credenciais devem ser fornecidas por variáveis de ambiente ou mecanismos seguros de configuração da aplicação.

Exemplo conceitual:

```env
# Model Provider
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=

# PostgreSQL
DATABASE_URL=

# Vector Database
VECTOR_DATABASE_URL=

# Embeddings
JINA_API_KEY=
```

Não armazene credenciais diretamente no código-fonte ou no controle de versão.

**Observação:** as URLs de conexão devem respeitar o driver esperado por cada componente. A memória assíncrona utiliza SQLAlchemy com asyncpg; o armazenamento de conhecimento utiliza o driver PostgreSQL compatível com sua implementação.

---

## Componentes

### Agent Protocol

Define o contrato estrutural esperado para os agentes gerenciados pela biblioteca.

O protocolo permite trabalhar com diferentes implementações, desde que respeitem as operações necessárias para identificação, execução e encerramento.

### AgentConfig

Responsável por representar a configuração de um agente.

Utiliza uma estrutura imutável (`frozen slots dataclass`) e valida os identificadores e dados de configuração.

### AgentManager

Responsável pelo ciclo de vida dos agentes:

- Registro.
- Consulta.
- Listagem.
- Verificação de existência.
- Execução.
- Remoção.
- Encerramento individual.
- Encerramento de todos os agentes.

### AgentRuntime

Centraliza a execução controlada dos agentes.

Responsabilidades:

- Preparar o contexto de execução.
- Propagar identificadores operacionais.
- Integrar observabilidade.
- Executar o agente.
- Restaurar o contexto anterior após a execução, inclusive em caso de erro.

---

## Gerenciamento de agentes

O gerenciamento de agentes é independente da estratégia de orquestração.

O `AgentManager` mantém o registro dos agentes disponíveis e permite que o Runtime seja utilizado para executar suas operações.

Cada agente possui identidade própria, permitindo que a aplicação trabalhe com diferentes especialistas.

## Orquestração

O módulo `orchestration` permite coordenar múltiplos agentes em uma mesma operação.

Uma equipe pode conter diferentes etapas, cada uma com sua própria estratégia de execução.

### Execução sequencial

Os agentes são executados em sequência. O resultado de uma etapa pode ser utilizado como entrada da próxima.

```text
Solicitação
    |
    v
Agente 1
    |
    v
Agente 2
    |
    v
Agente 3
    |
    v
Resultado final
```

### Execução paralela

Múltiplos agentes são executados simultaneamente.

```text
             Solicitação
                  |
          +-------+-------+
          |       |       |
          v       v       v
       Agente 1 Agente 2 Agente 3
          |       |       |
          +-------+-------+
                  |
                  v
              Agregação
                  |
                  v
               Resultado
```

### Recursos de orquestração

- Configuração de equipes.
- Configuração de etapas.
- Execução sequencial.
- Execução paralela.
- Agregação de resultados.
- Identificação de falhas por agente.
- Estratégia de interrupção por falha (`fail_fast`).
- Contexto compartilhado da execução.
- Eventos e rastreamento operacional.

A execução híbrida, combinando etapas sequenciais e paralelas, não faz parte da versão 0.1.0.

---

## Memória persistente

O módulo de memória permite armazenar informações operacionais em PostgreSQL.

A implementação utiliza persistência assíncrona e separação de escopos.

Entre os recursos estão:

- Persistência de memórias.
- Recuperação de informações.
- Isolamento por escopo.
- Metadados.
- Separação por usuário, agente e organização.
- Exclusão autorizada.
- Encerramento dos recursos de conexão.

A memória operacional não representa treinamento ou ajuste dos pesos do modelo.

Ela permite que informações sejam armazenadas e recuperadas durante diferentes execuções, de acordo com as regras de escopo e autorização.

**Importante:** o armazenamento de memória é explícito. A biblioteca não salva automaticamente todas as conversas sem uma operação definida pela aplicação.

---

## Knowledge e RAG

O módulo Knowledge disponibiliza uma camada de gerenciamento de conhecimento e recuperação contextual.

O fluxo de recuperação utiliza:

1. Entrada de uma consulta.
2. Geração ou utilização de embeddings.
3. Busca vetorial.
4. Aplicação dos filtros de escopo.
5. Retorno dos documentos relevantes.

### Componentes

**KnowledgeService**

Responsável pela interface de consulta ao conhecimento.

**Chunking**

Responsável pela divisão de conteúdos em partes menores para processamento e recuperação.

**Reader**

Responsável pela leitura de conteúdos suportados pela implementação.

**Embeddings**

Camada responsável pela geração de representações vetoriais.

**PgVector**

Implementação de armazenamento vetorial utilizando PostgreSQL e pgvector.

### Isolamento de conhecimento

As consultas podem considerar:

- `tenant_id`
- `agent_id`
- `user_id`

O contexto operacional também é utilizado para garantir que a consulta respeite o escopo da execução.

O objetivo é evitar que informações privadas de um usuário ou organização sejam retornadas para outro contexto.

---

## Ferramentas e MCP

O LKThink Agent possui uma camada própria de registro e execução de ferramentas.

### Tool Registry

Permite:

- Registrar ferramentas.
- Consultar ferramentas disponíveis.
- Executar operações síncronas e assíncronas.
- Adaptar ferramentas para integração com o Agno.
- Controlar permissões de utilização.

### Model Context Protocol (MCP)

O módulo MCP permite integrar servidores externos que disponibilizam ferramentas por meio do protocolo MCP.

A arquitetura contempla:

- Conexões STDIO.
- Conexões HTTP.
- Descoberta de ferramentas.
- Registro de ferramentas.
- Permissões por agente.
- Execução controlada.

O objetivo é permitir que agentes utilizem recursos externos sem acoplar diretamente sua implementação aos serviços integrados.

---

## Observabilidade

A observabilidade permite acompanhar o comportamento operacional dos agentes e das equipes.

O contexto de observabilidade trabalha com identificadores como:

- `trace_id`
- `run_id`
- `span_id`
- `parent_span_id`
- `tenant_id`
- `agent`
- `component`
- `operation`

Os eventos permitem identificar o início e o encerramento de operações, acompanhar execuções e relacionar diferentes etapas de uma mesma operação.

### PostgreSQL Exporter

O exporter PostgreSQL permite persistir eventos de observabilidade no banco de dados.

A implementação contempla:

- Conexão por URL ou engine SQLAlchemy.
- Verificação de conexão.
- Inicialização controlada.
- Persistência de eventos.
- Metadados estruturados em JSONB.

A observabilidade é parte da arquitetura do framework, não apenas um mecanismo de logging.

---

## Isolamento de contexto

O Runtime utiliza `ContextVar` para propagar informações de execução sem depender de variáveis globais compartilhadas.

Cada execução pode possuir seu próprio contexto:

```text
Execução A
├── tenant_id
├── agent_id
├── user_id
├── session_id
└── run_id

Execução B
├── tenant_id
├── agent_id
├── user_id
├── session_id
└── run_id
```

Essa abordagem permite executar agentes simultaneamente sem misturar os dados operacionais de diferentes solicitações.

O contexto é restaurado ao final da execução, inclusive quando ocorre uma exceção.

---

## Testes

O projeto utiliza Pytest para validar seus componentes.

Execute a suíte:

```bash
python -m pytest -q
```

Execute a verificação estática:

```bash
python -m ruff check src tests
```

Execute o build:

```bash
python -m build
```

Verifique as dependências:

```bash
python -m pip check
```

Os testes contemplam componentes como:

- Gerenciamento de agentes.
- Runtime.
- Isolamento de contexto.
- Concorrência.
- Observabilidade.
- Memória.
- Knowledge e RAG.
- Ferramentas.
- MCP.
- Orquestração.
- Integração real com DeepSeek, quando configurada.

---

## Build e distribuição

O projeto utiliza o padrão de empacotamento Python.

Para gerar os artefatos:

```bash
python -m build
```

Os arquivos são gerados no diretório:

```text
dist/
├── lkthink_agent-0.1.0.tar.gz
└── lkthink_agent-0.1.0-py3-none-any.whl
```

Valide os artefatos:

```bash
python -m twine check dist/*
```

Para publicar uma nova versão:

```bash
python -m twine upload dist/*
```

A publicação é feita no PyPI e exige credenciais de publicação válidas.

---

## Atualizações e versionamento

O LKThink Agent utiliza versionamento semântico (Semantic Versioning).

O formato segue:

```text
MAJOR.MINOR.PATCH
```

Exemplo:

```text
0.1.0
```

| Tipo | Quando utilizar | Exemplo |
|---|---|---|
| PATCH | Correções compatíveis | 0.1.0 → 0.1.1 |
| MINOR | Novas funcionalidades compatíveis | 0.1.0 → 0.2.0 |
| MAJOR | Mudanças incompatíveis | 0.1.0 → 1.0.0 |

### Como atualizar a biblioteca

Para atualizar para a versão mais recente:

```bash
pip install --upgrade lkthink-agent
```

Para instalar uma versão específica:

```bash
pip install lkthink-agent==0.1.0
```

Para atualizar incluindo as integrações:

```bash
pip install --upgrade "lkthink-agent[postgres,knowledge,mcp,api]"
```

### Como publicar uma nova versão

O processo recomendado é:

1. Atualizar o código.
2. Atualizar ou criar testes.
3. Executar a suíte de testes.
4. Executar o Ruff.
5. Atualizar a versão no `pyproject.toml`.
6. Gerar os artefatos.
7. Validar os artefatos com Twine.
8. Publicar no PyPI.
9. Criar uma tag correspondente no Git.

Exemplo de alteração no `pyproject.toml`:

```toml
[project]
name = "lkthink-agent"
version = "0.1.1"
```

Execute as verificações:

```bash
python -m pytest -q
python -m ruff check src tests
python -m pip check
```

Remova os artefatos antigos e gere os novos:

```powershell
Remove-Item dist -Recurse -Force -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*
```

Publique:

```bash
python -m twine upload dist/*
```

Crie a tag da versão:

```bash
git add .
git commit -m "release: v0.1.1"
git tag v0.1.1
git push origin main
git push origin v0.1.1
```

**Importante:** uma versão já publicada no PyPI não pode ser sobrescrita. Para qualquer correção ou melhoria, publique um novo número de versão.

---

## Roadmap

O LKThink Agent está em desenvolvimento contínuo.

### Documentação e experiência de desenvolvimento

- [ ] Documentação completa da API pública.
- [ ] Exemplos executáveis de criação de agentes.
- [ ] Exemplos de integração com DeepSeek.
- [ ] Exemplos de memória persistente.
- [ ] Exemplos de Knowledge e RAG.
- [ ] Exemplos de integração MCP.
- [ ] Exemplos completos de equipes multiagentes.

### Ecossistema

- [ ] Projeto demonstrativo independente utilizando o pacote via PyPI.
- [ ] Novos provedores de LLM.
- [ ] Novos provedores de embeddings.
- [ ] Expansão dos mecanismos de armazenamento.
- [ ] Estratégias avançadas de recuperação de conhecimento.

### Engenharia e operação

- [ ] CI com GitHub Actions.
- [ ] Pipeline automatizado de testes.
- [ ] Publicação automatizada de releases.
- [ ] Painel de observabilidade.
- [ ] Métricas de custo e consumo de tokens.
- [ ] Estratégias avançadas de execução e recuperação de falhas.

---

## Contribuição

Contribuições são bem-vindas.

Antes de enviar alterações:

1. Execute os testes.
2. Verifique a qualidade do código com Ruff.
3. Documente novas funcionalidades.
4. Adicione testes para comportamentos novos ou modificados.
5. Evite introduzir dependências obrigatórias desnecessárias.

---

## Licença

Este projeto utiliza a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para conhecer os termos de utilização.

---

**LKThink Agent — Modular Agent Engineering.**

Uma base extensível para construir, executar e orquestrar sistemas inteligentes.