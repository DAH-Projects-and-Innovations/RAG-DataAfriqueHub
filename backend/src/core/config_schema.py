"""
Schémas Pydantic pour valider les configurations YAML du pipeline RAG.
La validation se déclenche au chargement, avant la création des composants.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, field_validator, model_validator


class ComponentConfig(BaseModel):
    """Configuration générique d'un composant (embedder, retriever, llm…)"""

    name: str
    params: Dict[str, Any] = {}

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le champ 'name' ne peut pas être vide.")
        return v.strip()


class PipelineMetaConfig(BaseModel):
    """Section pipeline_config — paramètres globaux du pipeline."""

    name: str = "rag_pipeline"
    version: str = "1.0.0"
    default_top_k: int = 5
    default_rerank_top_k: int = 3
    enable_caching: bool = True
    log_level: str = "INFO"
    # Champs optionnels (ex: coût estimé, latence)
    model_config = {"extra": "allow"}


class ModelEntry(BaseModel):
    """Entrée dans la liste des modèles exposée via GET /models."""

    id: str
    label: str
    provider: str = ""
    default: bool = False


class PipelineConfigSchema(BaseModel):
    """Schéma complet d'un fichier de configuration YAML du pipeline RAG.

    Composants obligatoires : embedder, vector_store, retriever, llm, prompt_managers.
    Composants optionnels  : reranker, query_rewriter.
    """

    embedder: ComponentConfig
    vector_store: ComponentConfig
    retriever: ComponentConfig
    llm: ComponentConfig
    prompt_managers: ComponentConfig

    # Optionnels
    reranker: Optional[ComponentConfig] = None
    query_rewriter: Optional[ComponentConfig] = None

    # Métadonnées pipeline
    pipeline_config: PipelineMetaConfig = PipelineMetaConfig()

    # Liste des modèles exposée via /models
    models: List[ModelEntry] = []

    model_config = {"extra": "allow"}

    @model_validator(mode="after")
    def check_retriever_has_no_vector_store_in_yaml(self) -> "PipelineConfigSchema":
        """
        vector_store et embedder sont injectés dynamiquement dans retriever.params
        par la factory — ils ne doivent PAS être présents dans le YAML
        (évite une double instanciation accidentelle).
        """
        params = self.retriever.params
        for forbidden in ("vector_store", "embedder"):
            if forbidden in params:
                raise ValueError(
                    f"retriever.params.{forbidden} ne doit pas être défini dans le YAML : "
                    "il est injecté automatiquement par la factory."
                )
        return self
