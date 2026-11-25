
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable

from agno.tools.function import Function

from lkthink_agent.observability.tool_execution import (
    obter_observador,
    observar_ferramenta,
)
from lkthink_agent.tools.registry import ToolRegistry


class AgnoToolAdapter:

    @staticmethod
    def _instrumentar(
        func: Callable[..., Any],
        nome: str,
    ) -> Callable[..., Any]:

        if iscoroutinefunction(func):

            @wraps(func)
            async def executar_async(*args: Any, **kwargs: Any) -> Any:
                observador = obter_observador()

                if observador is None:
                    return await func(*args, **kwargs)

                with observar_ferramenta(observador, nome):
                    return await func(*args, **kwargs)

            return executar_async

        @wraps(func)
        def executar_sync(*args: Any, **kwargs: Any) -> Any:
            observador = obter_observador()

            if observador is None:
                return func(*args, **kwargs)

            with observar_ferramenta(observador, nome):
                return func(*args, **kwargs)

        return executar_sync

    def adaptar(self, registry: ToolRegistry) -> list[Function]:
        ferramentas = []

        for definition in registry.list_tools():

            funcao_instrumentada = self._instrumentar(
                definition.func,
                definition.name,
            )

            if definition.parameters is not None:
                ferramenta = Function(
                    name=definition.name,
                    description=definition.description,
                    parameters=definition.parameters,
                    entrypoint=funcao_instrumentada,
                    strict=definition.strict,
                    skip_entrypoint_processing=True,
                )

            else:
                ferramenta = Function.from_callable(
                    c=funcao_instrumentada,
                    name=definition.name,
                    strict=definition.strict,
                )

                if definition.description:
                    ferramenta.description = definition.description

            ferramentas.append(ferramenta)

        return ferramentas
