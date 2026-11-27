
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from lkthink_agent.knowledge.service import KnowledgeService
from lkthink_agent.observability.context import (
    AgentIdentity,
    criar_contexto_execucao,
    definir_contexto,
    limpar_contexto,
)


class FakeEmbeddingProvider:
    def __init__(self, config):
        self.config = config
        self.client = object()


class FakeVectorStore:
    def __init__(self, config, embedder):
        self.config = config
        self.embedder = embedder
        self.client = object()
        self.criado = False
        self.count_args = None

    def create(self):
        self.criado = True

    def count(self, *, filters, user_id=None):
        self.count_args = {
            "filters": filters,
            "user_id": user_id,
        }
        return 7


class FakeKnowledge:
    def __init__(self, **kwargs):
        self.config = kwargs
        self.insert_args = None
        self.search_args = None

    def insert(self, **kwargs):
        self.insert_args = kwargs

    def search(self, **kwargs):
        self.search_args = kwargs

        return [
            SimpleNamespace(
                id="documento-001",
                content="Conteúdo de teste.",
                meta_data={
                    "tenant_id": "empresa-001",
                    "agent_id": "agente-001",
                },
            )
        ]


class FakePostgresDb:
    def __init__(self, **kwargs):
        self.config = kwargs


@contextmanager
def contexto_runtime(
    *,
    tenant_id="empresa-001",
    agent_id="agente-001",
    user_id="usuario-001",
):
    identidade = AgentIdentity(
        id=agent_id,
        slug=agent_id,
        name="Agente de teste",
        label="Teste",
        color="blue",
    )

    contexto = criar_contexto_execucao(
        tenant_id=tenant_id,
        agent=identidade,
        metadata={"user_id": user_id},
    )

    token = definir_contexto(contexto)

    try:
        yield contexto
    finally:
        limpar_contexto(token)


@pytest.fixture
def knowledge_service(monkeypatch):
    import lkthink_agent.knowledge.service as service_module

    monkeypatch.setattr(
        service_module,
        "JinaEmbeddingProvider",
        FakeEmbeddingProvider,
    )

    monkeypatch.setattr(
        service_module,
        "PgVectorStore",
        FakeVectorStore,
    )

    monkeypatch.setattr(
        service_module,
        "PostgresDb",
        FakePostgresDb,
    )

    monkeypatch.setattr(
        service_module,
        "Knowledge",
        FakeKnowledge,
    )

    monkeypatch.setattr(
        service_module,
        "criar_text_reader",
        lambda config: "fake-reader",
    )

    config = SimpleNamespace(
        database_url="postgresql+psycopg://test:test@localhost/test",
        jina_api_key="fake-key",
        embedding_model="jina-embeddings-v3",
        embedding_dimensions=1024,
        chunk_size=900,
        chunk_overlap=100,
        top_k=5,
        schema="public",
        vector_table="test_vectors",
        knowledge_table="test_knowledge",
        distance="cosine",
    )

    return KnowledgeService(config)


def test_adiciona_texto_com_escopo_do_runtime(knowledge_service):
    with contexto_runtime():
        knowledge_service.add_text(
            "Documentação interna.",
        )

    argumentos = knowledge_service.knowledge.insert_args

    assert argumentos["text_content"] == "Documentação interna."
    assert argumentos["metadata"]["tenant_id"] == "empresa-001"
    assert argumentos["metadata"]["agent_id"] == "agente-001"
    assert argumentos["user_id"] == "usuario-001"


def test_preserva_metadados_personalizados(knowledge_service):
    with contexto_runtime():
        knowledge_service.add_text(
            "Documento de teste.",
            metadata={
                "origem": "manual",
                "categoria": "financeiro",
            },
        )

    metadata = knowledge_service.knowledge.insert_args["metadata"]

    assert metadata["origem"] == "manual"
    assert metadata["categoria"] == "financeiro"
    assert metadata["tenant_id"] == "empresa-001"
    assert metadata["agent_id"] == "agente-001"


def test_nao_permite_sobrescrever_tenant_e_agente(knowledge_service):
    with contexto_runtime():
        knowledge_service.add_text(
            "Documento de teste.",
            metadata={
                "tenant_id": "outra-empresa",
                "agent_id": "outro-agente",
            },
        )

    metadata = knowledge_service.knowledge.insert_args["metadata"]

    assert metadata["tenant_id"] == "empresa-001"
    assert metadata["agent_id"] == "agente-001"


def test_busca_com_filtros_de_isolamento(knowledge_service):
    with contexto_runtime():
        documentos = knowledge_service.search(
            "Como funciona o sistema?",
        )

    argumentos = knowledge_service.knowledge.search_args

    assert argumentos["filters"] == {
        "tenant_id": "empresa-001",
        "agent_id": "agente-001",
    }

    assert argumentos["user_id"] == "usuario-001"
    assert argumentos["max_results"] == 5

    assert len(documentos) == 1
    assert documentos[0]["id"] == "documento-001"


def test_contagem_respeita_escopo(knowledge_service):
    with contexto_runtime():
        total = knowledge_service.count()

    assert total == 7

    assert knowledge_service.vector_store.count_args == {
        "filters": {
            "tenant_id": "empresa-001",
            "agent_id": "agente-001",
        },
        "user_id": "usuario-001",
    }


def test_herda_contexto_sem_user_id(knowledge_service):
    with contexto_runtime(user_id=None):
        knowledge_service.add_text("Documento compartilhado.")

    argumentos = knowledge_service.knowledge.insert_args

    assert argumentos["user_id"] is None
    assert argumentos["metadata"]["tenant_id"] == "empresa-001"
    assert argumentos["metadata"]["agent_id"] == "agente-001"


def test_permite_escopo_explicito_fora_do_runtime(knowledge_service):
    knowledge_service.add_text(
        "Documento externo.",
        tenant_id="empresa-002",
        agent_id="agente-002",
        user_id="usuario-002",
    )

    argumentos = knowledge_service.knowledge.insert_args

    assert argumentos["metadata"]["tenant_id"] == "empresa-002"
    assert argumentos["metadata"]["agent_id"] == "agente-002"
    assert argumentos["user_id"] == "usuario-002"


def test_rejeita_operacao_sem_escopo(knowledge_service):
    with pytest.raises(ValueError, match="tenant_id"):
        knowledge_service.add_text("Documento sem escopo.")


def test_rejeita_tenant_diferente_do_runtime(knowledge_service):
    with contexto_runtime(), pytest.raises(ValueError, match="diverge"):
        knowledge_service.search(
            "Consulta.",
            tenant_id="outra-empresa",
        )


def test_rejeita_agente_diferente_do_runtime(knowledge_service):
    with contexto_runtime(), pytest.raises(ValueError, match="diverge"):
        knowledge_service.search(
            "Consulta.",
            agent_id="outro-agente",
        )


def test_rejeita_usuario_diferente_do_runtime(knowledge_service):
    with contexto_runtime(), pytest.raises(ValueError, match="diverge"):
        knowledge_service.search(
            "Consulta.",
            user_id="outro-usuario",
        )


def test_rejeita_texto_vazio(knowledge_service):
    with contexto_runtime(), pytest.raises(
        ValueError,
        match="conteúdo não pode ser vazio",
    ):
        knowledge_service.add_text("   ")


def test_rejeita_consulta_vazia(knowledge_service):
    with contexto_runtime(), pytest.raises(
        ValueError,
        match="consulta não pode ser vazia",
    ):
        knowledge_service.search("   ")


def test_rejeita_limite_invalido(knowledge_service):
    with contexto_runtime(), pytest.raises(ValueError, match="maior que zero"):
        knowledge_service.search("Consulta.", limit=0)


def test_inicializa_armazenamento_apenas_uma_vez(knowledge_service):
    knowledge_service.initialize()
    knowledge_service.initialize()

    assert knowledge_service.vector_store.criado is True
    assert knowledge_service._initialized is True
