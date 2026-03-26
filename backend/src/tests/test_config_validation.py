"""
Tests de validation des configurations YAML via Pydantic.

Vérifie que :
- les configs valides passent sans erreur
- les champs obligatoires manquants lèvent une ValueError au chargement
- les variables d'environnement sont correctement substituées
- le SemanticChunker et les nouvelles fonctionnalités de l'interface IVectorStore sont testés

Lancement :
    cd backend
    pytest src/tests/test_config_validation.py -v
"""

import sys
import os
import tempfile
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.core.config_schema import (
    PipelineConfigSchema,
    ComponentConfig,
    PipelineMetaConfig,
    ModelEntry,
)
from src.core.factory import RAGPipelineFactory


# ─── Config minimale valide ───────────────────────────────────────────────────

VALID_CONFIG = {
    "embedder": {"name": "sentence_transformers", "params": {"model_name": "test"}},
    "vector_store": {"name": "chroma", "params": {}},
    "retriever": {"name": "vector_retriever", "params": {}},
    "llm": {"name": "mistral", "params": {"api_key": "fake"}},
    "prompt_managers": {"name": "default", "params": {}},
}


# ─── Tests ComponentConfig ────────────────────────────────────────────────────

class TestComponentConfig:
    def test_valid_component(self):
        c = ComponentConfig(name="test_component", params={"key": "value"})
        assert c.name == "test_component"
        assert c.params == {"key": "value"}

    def test_empty_name_raises(self):
        with pytest.raises(Exception):
            ComponentConfig(name="", params={})

    def test_whitespace_name_stripped(self):
        c = ComponentConfig(name="  my_component  ")
        assert c.name == "my_component"

    def test_params_defaults_to_empty_dict(self):
        c = ComponentConfig(name="comp")
        assert c.params == {}


# ─── Tests PipelineConfigSchema ───────────────────────────────────────────────

class TestPipelineConfigSchema:
    def test_valid_config_passes(self):
        schema = PipelineConfigSchema(**VALID_CONFIG)
        assert schema.embedder.name == "sentence_transformers"
        assert schema.llm.name == "mistral"

    def test_missing_embedder_raises(self):
        config = {k: v for k, v in VALID_CONFIG.items() if k != "embedder"}
        with pytest.raises(Exception):
            PipelineConfigSchema(**config)

    def test_missing_llm_raises(self):
        config = {k: v for k, v in VALID_CONFIG.items() if k != "llm"}
        with pytest.raises(Exception):
            PipelineConfigSchema(**config)

    def test_missing_vector_store_raises(self):
        config = {k: v for k, v in VALID_CONFIG.items() if k != "vector_store"}
        with pytest.raises(Exception):
            PipelineConfigSchema(**config)

    def test_optional_reranker_absent_is_none(self):
        schema = PipelineConfigSchema(**VALID_CONFIG)
        assert schema.reranker is None

    def test_optional_query_rewriter_absent_is_none(self):
        schema = PipelineConfigSchema(**VALID_CONFIG)
        assert schema.query_rewriter is None

    def test_reranker_present(self):
        config = {
            **VALID_CONFIG,
            "reranker": {"name": "cross_encoder", "params": {"model_name": "test"}},
        }
        schema = PipelineConfigSchema(**config)
        assert schema.reranker.name == "cross_encoder"

    def test_models_list_defaults_to_empty(self):
        schema = PipelineConfigSchema(**VALID_CONFIG)
        assert schema.models == []

    def test_models_list_populated(self):
        config = {
            **VALID_CONFIG,
            "models": [{"id": "gpt-4o-mini", "label": "GPT-4o mini", "provider": "openai", "default": True}],
        }
        schema = PipelineConfigSchema(**config)
        assert len(schema.models) == 1
        assert schema.models[0].id == "gpt-4o-mini"
        assert schema.models[0].default is True

    def test_retriever_with_vector_store_in_params_raises(self):
        """vector_store ne doit pas être défini dans retriever.params du YAML."""
        config = {
            **VALID_CONFIG,
            "retriever": {"name": "vector_retriever", "params": {"vector_store": "chroma"}},
        }
        with pytest.raises(Exception, match="vector_store"):
            PipelineConfigSchema(**config)

    def test_retriever_with_embedder_in_params_raises(self):
        """embedder ne doit pas être défini dans retriever.params du YAML."""
        config = {
            **VALID_CONFIG,
            "retriever": {"name": "vector_retriever", "params": {"embedder": "bert"}},
        }
        with pytest.raises(Exception, match="embedder"):
            PipelineConfigSchema(**config)


# ─── Tests factory._replace_env_vars ─────────────────────────────────────────

class TestEnvVarSubstitution:
    def test_replaces_existing_env_var(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MY_TEST_KEY", "my_value_123")
            result = RAGPipelineFactory._replace_env_vars("${MY_TEST_KEY}")
            assert result == "my_value_123"

    def test_returns_raw_if_env_var_not_set(self):
        # Variable non définie → retourne la valeur brute ${...}
        with pytest.MonkeyPatch.context() as mp:
            mp.delenv("NONEXISTENT_VAR_XYZ", raising=False)
            result = RAGPipelineFactory._replace_env_vars("${NONEXISTENT_VAR_XYZ}")
            assert result == "${NONEXISTENT_VAR_XYZ}"

    def test_nested_dict_substitution(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("MY_MODEL", "gpt-4o")
            config = {"llm": {"params": {"model": "${MY_MODEL}", "key": "plain"}}}
            result = RAGPipelineFactory._replace_env_vars(config)
            assert result["llm"]["params"]["model"] == "gpt-4o"
            assert result["llm"]["params"]["key"] == "plain"

    def test_list_substitution(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("VAL", "substituted")
            result = RAGPipelineFactory._replace_env_vars(["${VAL}", "literal"])
            assert result == ["substituted", "literal"]

    def test_non_env_string_untouched(self):
        result = RAGPipelineFactory._replace_env_vars("just a plain string")
        assert result == "just a plain string"


# ─── Tests factory.load_config ────────────────────────────────────────────────

class TestLoadConfig:
    def _write_yaml(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
        f.write(content)
        f.close()
        return f.name

    def test_load_valid_yaml(self):
        yaml_content = """
embedder:
  name: sentence_transformers
  params: {}
vector_store:
  name: chroma
  params: {}
retriever:
  name: vector_retriever
  params: {}
llm:
  name: mistral
  params:
    api_key: fake
prompt_managers:
  name: default
  params: {}
"""
        path = self._write_yaml(yaml_content)
        try:
            config = RAGPipelineFactory.load_config(path)
            assert config["embedder"]["name"] == "sentence_transformers"
            assert config["llm"]["name"] == "mistral"
        finally:
            os.unlink(path)

    def test_load_missing_required_field_raises(self):
        yaml_content = """
vector_store:
  name: chroma
  params: {}
retriever:
  name: vector_retriever
  params: {}
llm:
  name: mistral
  params: {}
prompt_managers:
  name: default
  params: {}
"""
        path = self._write_yaml(yaml_content)
        try:
            with pytest.raises(ValueError, match="invalide"):
                RAGPipelineFactory.load_config(path)
        finally:
            os.unlink(path)

    def test_load_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            RAGPipelineFactory.load_config("/chemin/inexistant/config.yaml")


# ─── Tests IVectorStore.delete ────────────────────────────────────────────────

class TestChromaVectorStoreDelete:
    """Teste la méthode delete() de ChromaVectorStore avec un mock de collection."""

    def test_delete_calls_collection_delete(self):
        from src.vectorstores.chroma_store import ChromaVectorStore
        from unittest.mock import MagicMock, patch

        with patch("src.vectorstores.chroma_store.chromadb") as mock_chroma:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_chroma.PersistentClient.return_value = mock_client
            mock_client.get_or_create_collection.return_value = mock_collection

            store = ChromaVectorStore()
            store.delete(where={"filename": "test.pdf"})

            mock_collection.delete.assert_called_once_with(where={"filename": "test.pdf"})

    def test_delete_empty_filter_raises(self):
        from src.vectorstores.chroma_store import ChromaVectorStore
        from unittest.mock import MagicMock, patch

        with patch("src.vectorstores.chroma_store.chromadb") as mock_chroma:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_chroma.PersistentClient.return_value = mock_client
            mock_client.get_or_create_collection.return_value = mock_collection

            store = ChromaVectorStore()
            with pytest.raises(ValueError, match="filtre"):
                store.delete(where={})


# ─── Tests SemanticChunker ────────────────────────────────────────────────────

class TestSemanticChunker:
    """Teste le SemanticChunker avec un embedder mocké."""

    def _get_chunker_with_mock_model(self):
        from src.Chunkers.semantic_chunker import SemanticChunker
        from unittest.mock import MagicMock
        import numpy as np

        chunker = SemanticChunker(breakpoint_threshold=0.5, max_chunk_size=200, min_chunk_size=10)

        # Mock du modèle : retourne des embeddings aléatoires
        mock_model = MagicMock()
        mock_model.encode.side_effect = lambda sentences, **kw: np.random.rand(len(sentences), 10)
        chunker._model = mock_model
        return chunker

    def test_chunks_non_empty_text(self):
        from src.core.models import Document
        chunker = self._get_chunker_with_mock_model()
        doc = Document(
            content=(
                "Le RAG est une technique d'IA. "
                "Elle combine la recherche de documents avec la génération de texte. "
                "Les embeddings jouent un rôle clé dans ce processus. "
                "Le modèle trouve les passages pertinents avant de répondre."
            ),
            metadata={"filename": "test.pdf"},
        )
        chunks = chunker.chunk([doc])
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.doc_id == doc.doc_id
            assert len(chunk.content) > 0
            assert chunk.metadata.get("chunker") == "semantic"

    def test_empty_document_skipped(self):
        from src.core.models import Document
        chunker = self._get_chunker_with_mock_model()
        doc = Document(content="", metadata={})
        chunks = chunker.chunk([doc])
        assert chunks == []

    def test_very_short_text_returns_one_chunk(self):
        from src.core.models import Document
        chunker = self._get_chunker_with_mock_model()
        doc = Document(content="Phrase courte.", metadata={})
        chunks = chunker.chunk([doc])
        # Le texte est trop court pour être découpé en phrases → 1 seul chunk
        assert len(chunks) <= 1

    def test_fallback_on_embed_error(self):
        from src.Chunkers.semantic_chunker import SemanticChunker
        from src.core.models import Document

        chunker = SemanticChunker(max_chunk_size=100, min_chunk_size=5)
        # Forcer une erreur d'embedding
        from unittest.mock import MagicMock
        mock_model = MagicMock()
        mock_model.encode.side_effect = RuntimeError("GPU indisponible")
        chunker._model = mock_model

        doc = Document(
            content="Phrase 1. Phrase 2. Phrase 3. Phrase 4. Phrase 5.",
            metadata={"filename": "doc.pdf"},
        )
        # Ne doit pas lever d'exception grâce au fallback sliding-window
        chunks = chunker.chunk([doc])
        assert len(chunks) >= 1


# ─── Lancement direct ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess
    subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        cwd=BACKEND_DIR,
    )
