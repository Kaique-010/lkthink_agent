from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MCPTool:
    server_name: str
    name: str
    description: str
    input_schema: dict[str, Any]