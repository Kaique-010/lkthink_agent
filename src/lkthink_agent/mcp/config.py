from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True, slots=True)
class MCPServerConfig:
    name: str
    transport: Literal["stdio", "http"]

    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] | None = None
    cwd: str | None = None

    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)

    timeout: float = 30.0
    sse_read_timeout: float = 300.0

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("O nome do servidor MCP não pode ser vazio.")

        if self.transport not in ("stdio", "http"):
            raise ValueError("Transporte MCP deve ser 'stdio' ou 'http'.")

        if self.transport == "stdio" and not self.command:
            raise ValueError("O transporte stdio exige um command.")

        if self.transport == "http" and not self.url:
            raise ValueError("O transporte http exige uma url.")

        if self.timeout <= 0 or self.sse_read_timeout <= 0:
            raise ValueError("Os timeouts devem ser maiores que zero.")