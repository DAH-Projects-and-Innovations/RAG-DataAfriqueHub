"""
Module RAG - Moteur de génération avec citations et contrôle.
"""

from .engine import CitationRAG, RAGEngine, SimpleRAG
from .models import Citation, ConfidenceLevel, RAGConfig, RAGQuery, RAGResponse, Source

__all__ = [
    # Models
    "RAGResponse",
    "RAGQuery",
    "RAGConfig",
    "Source",
    "Citation",
    "ConfidenceLevel",
    # Engines
    "RAGEngine",
    "SimpleRAG",
    "CitationRAG",
]
