
from __future__ import annotations

import json
from typing import Any

from lkthink_agent.orchestration.context import TeamExecutionContext


class TeamAggregator:
    """Consolida resultados de agentes para uso nas próximas etapas."""

    def agregar(
        self,
        context: TeamExecutionContext,
        *,
        stage_names: tuple[str, ...] | None = None,
    ) -> str:
        """
        Constrói um contexto textual com os resultados anteriores.

        Quando stage_names não é informado, utiliza todas as etapas
        registradas no contexto, respeitando a ordem de execução.
        """

        etapas = (
            stage_names
            if stage_names is not None
            else tuple(context.stage_results.keys())
        )

        partes = [
            "SOLICITAÇÃO ORIGINAL:",
            context.prompt,
            "",
            "RESULTADOS DAS ETAPAS ANTERIORES:",
        ]

        total = 0

        for stage_name in etapas:
            resultados = context.obter_resultados_etapa(stage_name)

            if not resultados:
                continue

            partes.extend([
                "",
                f"ETAPA: {stage_name}",
            ])

            for resultado in resultados:
                agent_id = getattr(resultado, "agent_id", "desconhecido")
                agent_name = getattr(resultado, "agent_name", agent_id)
                content = self._formatar_conteudo(
                    getattr(resultado, "content", resultado)
                )

                partes.extend([
                    "",
                    f"AGENTE: {agent_name} ({agent_id})",
                    "RESULTADO:",
                    content,
                ])

                total += 1

        if total == 0:
            partes.extend([
                "",
                "Nenhum resultado anterior foi registrado.",
            ])

        return "\n".join(partes)

    @staticmethod
    def _formatar_conteudo(content: Any) -> str:
        """Normaliza conteúdos estruturados ou textuais."""

        if isinstance(content, str):
            return content

        if content is None:
            return ""

        if isinstance(content, (dict, list, tuple)):
            return json.dumps(
                content,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        return str(content)
