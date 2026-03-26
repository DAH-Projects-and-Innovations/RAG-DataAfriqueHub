"""
Tests d'intégration du pipeline RAG (orchestrateur).

Teste le flux complet embed → retrieve → rerank → generate avec des
mocks légers pour chaque composant — aucun modèle réel n'est chargé.

Lancement :
    cd backend
    pytest src/tests/test_integration_pipeline.py -v
"""

import sys
import os
from unittest.mock import MagicMock, patch
from typing import List

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.core.models import Document, Chunk, Query, RAGResponse
from src.core.orchestrator import RAGPipeline


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_chunk(content: str, filename: str = "test.pdf") -> Chunk:
    return Chunk(content=content, doc_id="doc-1", metadata={"filename": filename, "source": filename})


def _make_pipeline(
    llm_answer: str = "Réponse générée.",
    retrieved_docs: List[Document] | None = None,
) -> RAGPipeline:
    """Crée un pipeline avec tous les composants mockés."""
    if retrieved_docs is None:
        retrieved_docs = [
            Document(content="Le RAG combine recherche et génération.", metadata={"filename": "test.pdf"}),
            Document(content="Les embeddings représentent le sens des phrases.", metadata={"filename": "test.pdf"}),
        ]

    embedder = MagicMock()
    embedder.embed_texts.return_value = [[0.1] * 10] * 5
    embedder.embed_query.return_value = [0.1] * 10
    embedder.get_dimension.return_value = 10

    vector_store = MagicMock()
    vector_store.search.return_value = retrieved_docs

    retriever = MagicMock()
    retriever.retrieve.return_value = retrieved_docs

    llm = MagicMock()
    llm.generate_with_context.return_value = llm_answer

    pipeline = RAGPipeline(
        embedder=embedder,
        vector_store=vector_store,
        retriever=retriever,
        llm=llm,
        config={"models": [], "enable_caching": True},
    )
    return pipeline


# ─── Tests ingest ─────────────────────────────────────────────────────────────

class TestPipelineIngest:
    def test_ingest_calls_loader_chunker_embedder_store(self):
        pipeline = _make_pipeline()

        loader = MagicMock()
        loader.load.return_value = [
            Document(content="Texte du document de test.", metadata={"filename": "doc.txt"}),
        ]

        chunker = MagicMock()
        chunker.chunk.return_value = [
            _make_chunk("Texte du document de test."),
        ]

        count = pipeline.ingest(loader=loader, chunker=chunker, source="/fake/path")

        loader.load.assert_called_once_with("/fake/path")
        chunker.chunk.assert_called_once()
        pipeline.embedder.embed_texts.assert_called_once()
        pipeline.vector_store.add_chunks.assert_called_once()
        assert count == 1

    def test_ingest_empty_documents_returns_zero(self):
        pipeline = _make_pipeline()
        loader = MagicMock()
        loader.load.return_value = []
        chunker = MagicMock()

        count = pipeline.ingest(loader=loader, chunker=chunker, source="/empty")
        assert count == 0

    def test_ingest_empty_chunks_returns_zero(self):
        pipeline = _make_pipeline()
        loader = MagicMock()
        loader.load.return_value = [Document(content="Texte.", metadata={})]
        chunker = MagicMock()
        chunker.chunk.return_value = []

        count = pipeline.ingest(loader=loader, chunker=chunker, source="/path")
        assert count == 0


# ─── Tests query ──────────────────────────────────────────────────────────────

class TestPipelineQuery:
    def test_query_returns_rag_response(self):
        pipeline = _make_pipeline(llm_answer="Voici la réponse.")
        response = pipeline.query("Qu'est-ce que le RAG ?")
        assert isinstance(response, RAGResponse)
        assert response.answer == "Voici la réponse."

    def test_query_returns_sources(self):
        docs = [Document(content="Doc 1.", metadata={"filename": "a.pdf"})]
        pipeline = _make_pipeline(retrieved_docs=docs)
        response = pipeline.query("Question ?")
        assert len(response.sources) == 1

    def test_query_deduplication(self):
        """Les documents avec le même doc_id ne doivent apparaître qu'une fois."""
        duplicate_doc = Document(content="Identique.", metadata={})
        duplicate_doc.doc_id = "same-id"
        docs = [duplicate_doc, duplicate_doc]

        pipeline = _make_pipeline(retrieved_docs=docs)
        response = pipeline.query("Test déduplication")
        # Après déduplication, une seule source
        assert len(response.sources) == 1

    def test_query_with_reranker(self):
        pipeline = _make_pipeline()
        reranker = MagicMock()
        reranker.rerank.return_value = [
            Document(content="Top résultat.", metadata={"filename": "best.pdf"}),
        ]
        pipeline.reranker = reranker

        response = pipeline.query("Question ré-rankée ?", rerank_top_k=1)
        reranker.rerank.assert_called_once()
        assert len(response.sources) == 1

    def test_query_reranker_error_does_not_crash(self):
        """Si le reranker lève une erreur, le pipeline doit continuer sans reranking."""
        pipeline = _make_pipeline(llm_answer="Réponse sans rerank.")
        reranker = MagicMock()
        reranker.rerank.side_effect = RuntimeError("Reranker cassé")
        pipeline.reranker = reranker

        response = pipeline.query("Question ?")
        assert isinstance(response, RAGResponse)
        assert "Réponse sans rerank." == response.answer

    def test_query_metadata_contains_steps(self):
        pipeline = _make_pipeline()
        response = pipeline.query("Test metadata")
        assert "steps" in response.metadata

    def test_query_with_query_rewriter(self):
        pipeline = _make_pipeline()
        query_rewriter = MagicMock()
        query_rewriter.rewrite.return_value = ["Version 1", "Version 2"]
        pipeline.query_rewriter = query_rewriter

        response = pipeline.query("Question originale")
        query_rewriter.rewrite.assert_called_once()
        assert isinstance(response, RAGResponse)


# ─── Tests delete_document ────────────────────────────────────────────────────

class TestPipelineDeleteDocument:
    def test_delete_calls_vector_store_delete(self):
        pipeline = _make_pipeline()
        pipeline.vector_store.delete = MagicMock()

        result = pipeline.delete_document("rapport.pdf")
        pipeline.vector_store.delete.assert_called_once_with(where={"source": "rapport.pdf"})
        assert result is True

    def test_delete_returns_false_on_error(self):
        pipeline = _make_pipeline()
        pipeline.vector_store.delete = MagicMock(side_effect=RuntimeError("Erreur store"))

        result = pipeline.delete_document("fichier.pdf")
        assert result is False


# ─── Tests get_stats ──────────────────────────────────────────────────────────

class TestPipelineGetStats:
    def test_get_stats_returns_dict(self):
        pipeline = _make_pipeline()
        stats = pipeline.get_stats()
        assert isinstance(stats, dict)
        assert "embedder" in stats
        assert "vector_store" in stats
        assert "retriever" in stats
        assert "llm" in stats

    def test_get_stats_shows_optional_components(self):
        pipeline = _make_pipeline()
        stats = pipeline.get_stats()
        assert "optional_components" in stats
        assert stats["optional_components"]["reranker"] is None
        assert stats["optional_components"]["query_rewriter"] is None


# ─── Lancement direct ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess
    subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        cwd=BACKEND_DIR,
    )
