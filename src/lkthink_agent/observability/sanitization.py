
from __future__ import annotations

import re
from typing import Any

VALOR_REDACTADO = "[REDACTED]"
LIMITE_TEXTO = 12_000

CAMPOS_SENSIVEIS = {
    "password",
    "passwd",
    "senha",
    "secret",
    "client_secret",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "authorization",
    "proxy_authorization",
    "access_token",
    "refresh_token",
    "id_token",
    "auth_token",
    "credentials",
    "credential",
    "connection_string",
    "database_url",
    "dsn",
    "cookie",
    "set_cookie",
}

PADRAO_BEARER = re.compile(
    r"(?i)\b(Bearer\s+)[A-Za-z0-9._~+/=-]+"
)

PADRAO_URL = re.compile(
    r"(?i)(://)[^/@\s:]+(?::[^/@\s]*)?@"
)

PADRAO_CREDENCIAL = re.compile(
    r"(?i)\b("
    r"api[_-]?key|"
    r"access[_-]?token|"
    r"refresh[_-]?token|"
    r"client[_-]?secret|"
    r"password|"
    r"passwd|"
    r"authorization|"
    r"secret"
    r")(\s*[=:]\s*)([^\s,;]+)"
)


def _normalizar_chave(chave: str) -> str:
    return chave.strip().lower().replace("-", "_")


def _campo_sensivel(chave: str) -> bool:
    normalizada = _normalizar_chave(chave)

    return (
        normalizada in CAMPOS_SENSIVEIS
        or normalizada.endswith(
            ("_api_key", "_token", "_password", "_secret")
        )
    )


def sanitizar_texto(
    texto: str,
    limite: int = LIMITE_TEXTO,
) -> str:
    """Remove credenciais de textos livres."""

    if not isinstance(texto, str):
        texto = str(texto)

    resultado = PADRAO_BEARER.sub(
        lambda match: match.group(1) + VALOR_REDACTADO,
        texto,
    )

    resultado = PADRAO_URL.sub(
        lambda match: (
            match.group(1) + VALOR_REDACTADO + "@"
        ),
        resultado,
    )

    resultado = PADRAO_CREDENCIAL.sub(
        lambda match: (
            match.group(1)
            + match.group(2)
            + VALOR_REDACTADO
        ),
        resultado,
    )

    if len(resultado) > limite:
        resultado = resultado[:limite] + "... [TRUNCADO]"

    return resultado


def sanitizar_valor(
    valor: Any,
    chave: str | None = None,
    limite: int = LIMITE_TEXTO,
) -> Any:
    """Sanitiza recursivamente os dados de um evento."""

    if chave and _campo_sensivel(chave):
        return VALOR_REDACTADO

    if isinstance(valor, BaseException):
        return sanitizar_excecao(valor)

    if isinstance(valor, dict):
        return {
            str(k): sanitizar_valor(
                v,
                chave=str(k),
                limite=limite,
            )
            for k, v in valor.items()
        }

    if isinstance(valor, (list, tuple, set)):
        return [
            sanitizar_valor(item, limite=limite)
            for item in valor
        ]

    if isinstance(valor, str):
        return sanitizar_texto(valor, limite=limite)

    if isinstance(valor, bytes):
        return "[DADOS BINÁRIOS OMITIDOS]"

    return valor


def sanitizar_metadata(
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Sanitiza os metadados de um evento."""

    if not metadata:
        return {}

    return sanitizar_valor(metadata)


def sanitizar_excecao(
    erro: BaseException,
) -> dict[str, str]:
    """Retorna informações seguras de uma exceção."""

    return {
        "type": type(erro).__name__,
        "message": sanitizar_texto(str(erro)),
    }
