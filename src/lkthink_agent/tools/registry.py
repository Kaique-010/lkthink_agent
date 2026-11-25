from collections.abc import Callable
from typing import Any

from lkthink_agent.tools.base import BaseTool
from lkthink_agent.tools.definition import ToolDefinition


class ToolRegistry:

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        func: Callable[..., Any] | BaseTool,
        *,
        name: str | None = None,
        description: str | None = None,
        strict: bool = False,
        parameters: dict[str, Any] | None = None,
    ) -> ToolDefinition:

        if isinstance(func, BaseTool):
            tool_func = func.execute
            tool_name = name or func.name
            tool_description = description or func.description

        else:
            if not callable(func):
                raise TypeError("A ferramenta precisa ser callable.")

            tool_func = func
            tool_name = name or getattr(func, "__name__", None)
            tool_description = description

        if not tool_name:
            raise ValueError("Não foi possível determinar o nome da ferramenta.")

        if tool_name in self._tools:
            raise ValueError(
                f"Já existe uma ferramenta registrada com o nome '{tool_name}'."
            )

        definition = ToolDefinition(
            name=tool_name,
            func=tool_func,
            description=tool_description,
            strict=strict,
            parameters=parameters,
        )

        self._tools[tool_name] = definition

        return definition

    def unregister(self, name: str) -> bool:
        return self._tools.pop(name, None) is not None

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(f"Ferramenta '{name}' não encontrada.") from None

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def exists(self, name: str) -> bool:
        return name in self._tools

    def clear(self) -> None:
        self._tools.clear()

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return self.exists(name)