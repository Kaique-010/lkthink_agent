
from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    """Snapshot imutável de uma métrica."""

    name: str
    labels: tuple[tuple[str, str], ...]
    count: int
    total: float
    minimum: float | None
    maximum: float | None
    mean: float | None


class MetricsRegistry:
    """
    Registro de métricas do LKThink Agent.

    Suporta:
    - Contadores incrementais.
    - Observações de duração, tokens e valores numéricos.
    - Agregação por labels.
    - Acesso concorrente com proteção por lock.

    Não depende de provedores ou engines de agentes.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._counters: dict[
            tuple[str, tuple[tuple[str, str], ...]], float
        ] = {}
        self._observations: dict[
            tuple[str, tuple[tuple[str, str], ...]], list[float]
        ] = {}

    @staticmethod
    def _normalizar_labels(
        labels: Mapping[str, str] | None,
    ) -> tuple[tuple[str, str], ...]:
        if not labels:
            return ()

        return tuple(
            sorted(
                (str(chave), str(valor))
                for chave, valor in labels.items()
            )
        )

    @staticmethod
    def _validar_nome(name: str) -> None:
        if not name or not name.strip():
            raise ValueError("O nome da métrica não pode ser vazio.")

    def increment(
        self,
        name: str,
        value: float = 1,
        *,
        labels: Mapping[str, str] | None = None,
    ) -> float:
        """Incrementa um contador e retorna seu valor atualizado."""

        self._validar_nome(name)

        if value < 0:
            raise ValueError("Contadores não aceitam incrementos negativos.")

        chave = (name, self._normalizar_labels(labels))

        with self._lock:
            atual = self._counters.get(chave, 0.0) + value
            self._counters[chave] = atual
            return atual

    def observe(
        self,
        name: str,
        value: float,
        *,
        labels: Mapping[str, str] | None = None,
    ) -> None:
        """Registra uma observação numérica."""

        self._validar_nome(name)

        chave = (name, self._normalizar_labels(labels))

        with self._lock:
            self._observations.setdefault(chave, []).append(
                float(value)
            )

    def get_counter(
        self,
        name: str,
        *,
        labels: Mapping[str, str] | None = None,
    ) -> float:
        """Retorna o valor atual de um contador."""

        chave = (name, self._normalizar_labels(labels))

        with self._lock:
            return self._counters.get(chave, 0.0)

    def get_observations(
        self,
        name: str,
        *,
        labels: Mapping[str, str] | None = None,
    ) -> tuple[float, ...]:
        """Retorna as observações registradas."""

        chave = (name, self._normalizar_labels(labels))

        with self._lock:
            return tuple(self._observations.get(chave, ()))

    def snapshot(self) -> tuple[MetricSnapshot, ...]:
        """Gera snapshots de todas as métricas observadas."""

        with self._lock:
            snapshots = []

            for (name, labels), valores in self._observations.items():
                total = sum(valores)
                count = len(valores)

                snapshots.append(
                    MetricSnapshot(
                        name=name,
                        labels=labels,
                        count=count,
                        total=total,
                        minimum=min(valores) if valores else None,
                        maximum=max(valores) if valores else None,
                        mean=total / count if count else None,
                    )
                )

            return tuple(snapshots)

    def reset(self) -> None:
        """Limpa todas as métricas registradas."""

        with self._lock:
            self._counters.clear()
            self._observations.clear()
