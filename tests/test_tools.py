import pytest

from lkthink_agent.tools import BaseTool, ToolRegistry
from lkthink_agent.tools.adapters.agno import AgnoToolAdapter


def consultar_cliente(codigo: int) -> dict:
    """Consulta um cliente."""
    return {"codigo": codigo}


class ConsultarEstoque(BaseTool):
    name = "consultar_estoque"
    description = "Consulta estoque."

    def execute(self, codigo: int) -> dict:
        return {"estoque": codigo}


def test_registrar_funcao():
    registry = ToolRegistry()

    definition = registry.register(consultar_cliente)

    assert definition.name == "consultar_cliente"
    assert registry.exists("consultar_cliente")


def test_registrar_com_nome_personalizado():
    registry = ToolRegistry()

    registry.register(consultar_cliente, name="cliente")

    assert registry.exists("cliente")


def test_registrar_classe_base_tool():
    registry = ToolRegistry()

    registry.register(ConsultarEstoque())

    assert registry.exists("consultar_estoque")


def test_rejeitar_ferramenta_duplicada():
    registry = ToolRegistry()

    registry.register(consultar_cliente)

    with pytest.raises(ValueError):
        registry.register(consultar_cliente)


def test_remover_ferramenta():
    registry = ToolRegistry()
    registry.register(consultar_cliente)

    assert registry.unregister("consultar_cliente")
    assert not registry.exists("consultar_cliente")


def test_buscar_ferramenta_inexistente():
    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.get("inexistente")


def test_converter_para_agno():
    registry = ToolRegistry()

    registry.register(
        consultar_cliente,
        description="Consulta um cliente pelo código.",
    )

    adapter = AgnoToolAdapter()
    ferramentas = adapter.adaptar(registry)

    assert len(ferramentas) == 1
    assert ferramentas[0].name == "consultar_cliente"
    assert ferramentas[0].description == "Consulta um cliente pelo código."


def test_registrar_funcao_async():
    registry = ToolRegistry()

    async def consultar() -> dict:
        """Consulta assíncrona."""
        return {"resultado": True}

    registry.register(consultar)

    ferramentas = AgnoToolAdapter().adaptar(registry)

    assert len(ferramentas) == 1