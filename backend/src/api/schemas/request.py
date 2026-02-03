from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class IngestRequest(BaseModel):
    source: str = Field(..., description="Chemin du fichier ou URL")
    loader_name: str = Field(..., description="Nom du loader (ex: pdf_loader)")
    chunker_name: str = Field(..., description="Nom du chunker (ex: overlap_chunker)")
    loader_params: Dict[str, Any] = Field(default_factory=dict)
    chunker_params: Dict[str, Any] = Field(default_factory=dict)

class QueryRequest(BaseModel):
    question: str = Field(..., description="La question de l'utilisateur")
    top_k: int = Field(default=5)
    rerank_top_k: Optional[int] = Field(default=None)
    streaming: bool = Field(default=False)
