# backend/src/api/schemas/request.py

from typing import Any

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    source: str = Field(..., description="Chemin du fichier ou URL")
    loader_name: str = Field(..., description="Nom du loader (ex: pdf_loader)")
    chunker_name: str = Field(..., description="Nom du chunker (ex: overlap_chunker)")
    loader_params: dict[str, Any] = Field(default_factory=dict)
    chunker_params: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str = Field(..., description="La question de l'utilisateur")
    chat_history: list | None = Field(
        default_factory=list, description="Historique de la conversation"
    )
    top_k: int = Field(default=5)
    rerank_top_k: int | None = Field(default=None)
    llm_params: dict[str, Any] | None = Field(
        default_factory=dict, description="Paramètres optionnels pour le LLM"
    )
