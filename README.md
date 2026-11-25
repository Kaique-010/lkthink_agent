Uma biblioteca Python para construir agentes de IA especializados, conectá-los a ferramentas e servidores MCP, utilizar modelos de linguagem e preparar aplicações com conhecimento vetorial e observabilidade.

O que o LKThink Agent já faria hoje
1. Criar agentes especializados
Uma aplicação poderia instalar a biblioteca e criar agentes com identidades e instruções independentes.

Exemplo:
from lkthink_agent.agents.agent import LKThinkAgentfrom lkthink_agent.agents.config import AgentConfigfrom lkthink_agent.providers.deepseek import (    DeepSeekConfig,    DeepSeekProvider,)provider = DeepSeekProvider(    DeepSeekConfig(        api_key="SUA_API_KEY",        model="deepseek-chat",    ))config = AgentConfig(    id="agent-financeiro",    slug="financeiro",    name="Agente Financeiro",    label="Financeiro",    instructions="""    Você é um especialista financeiro.    Analise informações e responda objetivamente.    """)agente = LKThinkAgent(    config=config,    provider=provider,



Cada agente pode ter suas próprias instruções, identidade, ferramentas e configuração.
2. Conectar agentes a ferramentas
O LKThink Agent já possui um registro próprio de ferramentas e um adaptador para o motor interno.

Isso permite disponibilizar funções Python para os agentes.

Exemplos de aplicações:
- Consultar clientes.
- Consultar pedidos.
- Calcular indicadores.
- Consultar estoque.
- Gerar relatórios.
- Executar operações em sistemas externos.
A aplicação registra as funções, e o agente pode utilizá-las durante a execução.
3. Integrar servidores MCP
Integração real testada
Esse é um dos recursos mais interessantes.

O LKThink Agent consegue:
- Conectar servidores MCP via STDIO.
- Conectar servidores via HTTP, conforme o transporte implementado.
- Descobrir ferramentas disponíveis.
- Restringir quais ferramentas cada agente pode utilizar.
- Registrar ferramentas MCP no seu ToolRegistry.
- Executar chamadas através do cliente MCP.
- Encerrar conexões.
Já testamos uma execução real com DeepSeek e um servidor MCP que consulta clientes.
4. Utilizar diferentes modelos de IA
A arquitetura possui uma camada de providers independente do agente.

Atualmente, temos integração implementada com DeepSeek por meio da interface compatível com OpenAI.

Isso prepara a arquitetura para adicionar outros providers sem precisar reescrever o agente.

Atenção: outros providers ainda precisam ser implementados e testados.
5. Trabalhar com conhecimento próprio (RAG)
O projeto já possui integração funcional com:
- PostgreSQL.
- pgvector.
- Jina Embeddings.
- Fragmentação de documentos (chunking).
- Armazenamento vetorial.
- Busca semântica.
Na prática, isso permite preparar uma base de conhecimento para os agentes consultarem.

Exemplos:
- Documentação interna.
- Manuais de sistemas.
- Contratos.
- Políticas empresariais.
- Documentação técnica.
O pipeline de ingestão e busca já foi testado. A integração completa desse conhecimento ao fluxo de execução dos agentes ainda precisa ser consolidada.
6. Memória operacional
Já existe uma estrutura de memória persistida em PostgreSQL, com isolamento por:
- Agente.
- Usuário.
- Sessão.
Ela foi projetada para armazenar e recuperar informações operacionais.

Porém, ainda não está totalmente integrada ao ciclo de execução do agente.

Isso significa que não devemos anunciar memória conversacional automática como recurso concluído.
7. Observabilidade
O projeto já possui uma camada própria de observabilidade.

Ela contempla:
- Logs coloridos no terminal.
- Logs estruturados em JSON.
- Contexto de execução.
- Identificação de agentes.
- Trace ID.
- Run ID.
- Spans.
- Métricas de tokens e duração.
- Exportadores para console, arquivo e PostgreSQL.
Na execução que acabamos de realizar, tivemos:
Exemplo de execução real
10,83 segundos
Tokens consumidos
1.124

Spans registrados
2


Execução com DeepSeek e agente conectado ao MCP. A instrumentação individual das chamadas de ferramentas ainda está pendente.


O que alguém conseguiria construir com ele?










Central de atendimento inteligente

Agentes especializados consultando clientes, pedidos e informações por ferramentas e MCP.













Agentes financeiros

Consultas financeiras, cálculos, análises e integração com sistemas empresariais.













Agentes de desenvolvimento

Consultar documentação, executar ferramentas e analisar informações técnicas.













Assistentes de conhecimento empresarial

Consultar documentos e bases vetoriais privadas usando RAG.



O que ainda não poderíamos prometer
Recurso	Situação
Multiagentes com orquestração	Não concluído
Memória automática integrada	Pendente
Knowledge integrado ao agente	Pendente
Observabilidade de ferramentas	Pendente
API HTTP independente	Pendente
Container Docker pronto para produção	Pendente de validação
Instalação pública no PyPI	Não publicada
Aprendizado contínuo	Não implementado