# ==========================================
# src/core/models.py
# ==========================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Document:
    """Représentation d'un document"""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    doc_id: str | None = None
    score: float | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.doc_id is None:
            import uuid

            self.doc_id = str(uuid.uuid4())


@dataclass
class Chunk:
    """Représentation d'un chunk de document"""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_id: str = ""
    doc_id: str = ""
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.chunk_id:
            import uuid

            self.chunk_id = str(uuid.uuid4())


@dataclass
class Query:
    """Représentation d'une requête"""

    text: str
    metadata: dict[str, Any] | None = None
    embedding: list[float] | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RAGResponse:
    """Réponse du pipeline RAG"""

    answer: str
    sources: list[Document]
    metadata: dict[str, Any] = field(default_factory=dict)
    query: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convertit la réponse en dictionnaire"""
        return {
            "answer": self.answer,
            "sources": [
                {
                    "content": getattr(s, "content", str(s)),
                    "metadata": getattr(s, "metadata", {}) or {},
                    "doc_id": getattr(s, "doc_id", getattr(s, "chunk_id", None)),
                    "score": getattr(s, "score", (getattr(s, "metadata", {}) or {}).get("score")),
                }
                for s in self.sources
            ],
            "metadata": self.metadata,
            "query": self.query,
            "timestamp": self.timestamp.isoformat(),
        }
