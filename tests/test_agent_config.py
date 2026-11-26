import pytest

from lkthink_agent.agents.config import AgentConfig


def criar_config(**overrides):
    dados = {
        "id": "agent-001",
        "slug": "agente-teste",
        "name": "Agente de teste",
        "label": "Teste",
        "instructions": "Você é um agente de teste.",
    }
    dados.update(overrides)
    return AgentConfig(**dados)


def test_normaliza_id_e_slug():
    config = criar_config(
        id="  agent-001  ",
        slug="  agente-teste  ",
    )

    assert config.id == "agent-001"
    assert config.slug == "agente-teste"


@pytest.mark.parametrize(
    "campo",
    ["id", "slug", "name", "label", "instructions"],
)
def test_rejeita_campos_vazios(campo):
    with pytest.raises(ValueError):
        criar_config(**{campo: "   "})


@pytest.mark.parametrize(
    "campo",
    ["id", "slug", "name", "label", "instructions"],
)
def test_rejeita_campos_que_nao_sao_strings(campo):
    with pytest.raises(TypeError):
        criar_config(**{campo: 123})


def test_config_permanece_imutavel():
    config = criar_config()

    with pytest.raises(AttributeError):
        config.id = "outro-id"

    with pytest.raises(AttributeError):
        config.slug = "outro-slug"