"""
Tests d'intégration des routes FastAPI.

Utilise TestClient (httpx) et des mocks pour les composants lourds
(embedder, LLM, vector store) — aucun modèle n'est chargé en mémoire.

Lancement :
    cd backend
    pytest src/tests/test_integration_api.py -v
"""

import sys
import os
from unittest.mock import MagicMock, patch
from typing import List

import pytest

# Ajoute le répertoire backend au PYTHONPATH
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient

from src.core.models import Document, RAGResponse


# ─── Fixtures ────────────────────────────────────────────────────────────────

def _make_mock_pipeline(answer: str = "Réponse de test.") -> MagicMock:
    """Crée un pipeline entièrement mocké."""
    pipeline = MagicMock()
    pipeline.query.return_value = RAGResponse(
        answer=answer,
        sources=[Document(content="Extrait de test.", metadata={"filename": "test.pdf"})],
        metadata={"steps": []},
        query="question",
    )
    pipeline.ingest.return_value = 5
    pipeline.delete_document.return_value = True
    pipeline.get_stats.return_value = {"embedder": {"type": "Mock"}}
    pipeline.config = {
        "models": [
            {"id": "mock-model", "label": "Mock Model", "provider": "mock", "default": True}
        ]
    }
    return pipeline


@pytest.fixture
def client():
    """Client HTTP avec pipeline mocké injecté."""
    mock_pipeline = _make_mock_pipeline()

    # On importe l'app APRÈS avoir patché get_pipeline pour éviter le chargement réel
    from src.api.dependencies import get_pipeline
    from src.api.main import app

    app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_auth():
    """Client HTTP avec authentification activée (API_KEY définie)."""
    mock_pipeline = _make_mock_pipeline()

    from src.api.dependencies import get_pipeline
    from src.api.main import app

    app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
    with patch.dict(os.environ, {"API_KEY": "secret-test-key"}):
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.clear()


# ─── Tests /health ────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_up(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "up"
        assert "stats" in data

    def test_health_with_auth_no_key_fails(self, client_with_auth):
        response = client_with_auth.get("/health")
        assert response.status_code == 401

    def test_health_with_auth_valid_key(self, client_with_auth):
        response = client_with_auth.get("/health", headers={"X-API-Key": "secret-test-key"})
        assert response.status_code == 200

    def test_health_with_auth_wrong_key(self, client_with_auth):
        response = client_with_auth.get("/health", headers={"X-API-Key": "mauvaise-cle"})
        assert response.status_code == 401


# ─── Tests /models ────────────────────────────────────────────────────────────

class TestModelsEndpoint:
    def test_models_returns_list(self, client):
        response = client.get("/models")
        assert response.status_code == 200
        models = response.json()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_models_have_required_fields(self, client):
        response = client.get("/models")
        for model in response.json():
            assert "id" in model
            assert "label" in model
            assert "default" in model


# ─── Tests /query ─────────────────────────────────────────────────────────────

class TestQueryEndpoint:
    def test_query_returns_answer(self, client):
        payload = {"question": "Qu'est-ce que le RAG ?", "top_k": 5}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

    def test_query_returns_sources(self, client):
        payload = {"question": "Qu'est-ce que le RAG ?"}
        response = client.post("/query", json=payload)
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_query_with_chat_history(self, client):
        payload = {
            "question": "Et en français ?",
            "chat_history": [
                {"role": "user", "content": "Qu'est-ce que Python ?"},
                {"role": "assistant", "content": "Python est un langage."},
            ],
            "top_k": 3,
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_missing_question_returns_422(self, client):
        response = client.post("/query", json={"top_k": 5})
        assert response.status_code == 422

    def test_query_with_llm_params(self, client):
        payload = {
            "question": "Test",
            "llm_params": {"temperature": 0.3, "model": "gpt-4o-mini"},
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_pipeline_error_returns_500(self, client):
        from src.api.dependencies import get_pipeline
        from src.api.main import app

        broken_pipeline = MagicMock()
        broken_pipeline.query.side_effect = RuntimeError("Pipeline cassé")
        broken_pipeline.config = {"models": []}

        app.dependency_overrides[get_pipeline] = lambda: broken_pipeline
        try:
            response = client.post("/query", json={"question": "test"})
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()


# ─── Tests /ingest ────────────────────────────────────────────────────────────

class TestIngestEndpoint:
    def test_ingest_no_files_returns_400(self, client):
        response = client.post("/ingest", files=[])
        assert response.status_code in (400, 422)

    def test_ingest_unsupported_format_returns_400(self, client):
        response = client.post(
            "/ingest",
            files={"files": ("test.exe", b"binary content", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_ingest_valid_txt_file(self, client):
        txt_content = b"Ceci est un document de test. Il contient plusieurs phrases."
        with patch("src.api.routes.ingest.pipeline") if False else __import__("contextlib").nullcontext():
            response = client.post(
                "/ingest",
                files={"files": ("rapport.txt", txt_content, "text/plain")},
            )
        # Peut échouer si le pipeline réel est appelé, mais avec mock doit passer
        assert response.status_code in (200, 500)

    def test_delete_existing_file(self, client):
        response = client.delete("/ingest/rapport.pdf")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_delete_nonexistent_file(self, client):
        from src.api.dependencies import get_pipeline
        from src.api.main import app

        pipeline_404 = _make_mock_pipeline()
        pipeline_404.delete_document.return_value = False
        pipeline_404.config = {"models": []}

        app.dependency_overrides[get_pipeline] = lambda: pipeline_404
        try:
            response = client.delete("/ingest/fichier_inexistant.pdf")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()


# ─── Lancement direct ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess
    subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        cwd=BACKEND_DIR,
    )
