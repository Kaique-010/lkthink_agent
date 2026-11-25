from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    func: Callable[..., Any]
    description: str | None = None
    strict: bool = False
    parameters: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("O nome da ferramenta não pode ser vazio.")

        if not callable(self.func):
            raise TypeError("A ferramenta precisa ser callable.")

        if self.description is not None and not self.description.strip():
            raise ValueError("A descrição não pode ser vazia.")

        if self.parameters is not None:
            if not isinstance(self.parameters, dict):
                raise TypeError("parameters precisa ser um dicionário JSON Schema.")

            if self.parameters.get("type") != "object":
                raise ValueError("O JSON Schema da ferramenta deve ter type='object'.")