from agno.knowledge.reader.text_reader import TextReader

from lkthink_agent.knowledge.chunking import (
    criar_estrategia_chunking,
)
from lkthink_agent.knowledge.config import KnowledgeConfig


def criar_text_reader(config: KnowledgeConfig) -> TextReader:
    return TextReader(
        chunking_strategy=criar_estrategia_chunking(config),
        chunk=True,
    )
    