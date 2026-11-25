from agno.knowledge.chunking.document import DocumentChunking

from lkthink_agent.knowledge.config import KnowledgeConfig


def criar_estrategia_chunking(config: KnowledgeConfig) -> DocumentChunking:
    return DocumentChunking(
        chunk_size=config.chunk_size,
        overlap=config.chunk_overlap,
    )

