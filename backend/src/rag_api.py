# ==========================================
# src/rag_api.py
# ==========================================

"""
RAG API - Exposition du pipeline RAG via FastAPI

Fonctionnalités :
- Ingestion des documents (/ingest)
- Interrogation du RAG (/query)
- Statistiques (/stats)
- Support du streaming (optionnel)
- Documentation interactive Swagger / OpenAPI (/docs)
"""

import sys
import os
import asyncio
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Ajouter le répertoire courant pour retrouver le package src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.implementations import register_all_components, DummyPipeline
from src.core.factory import RAGPipelineFactory
from src.core.models import RAGResponse, Document

# ------------------------------------------
# Initialisation du pipeline (VRAI)
# ------------------------------------------

try:
    # 1. Enregistrer tous les composants RAG
    register_all_components()

    # 2. Charger la configuration YAML
    config = RAGPipelineFactory.load_config("configs/hybrid.yaml")

    # 3. Construire le pipeline réel
    pipeline: RAGPipeline = RAGPipelineFactory.create_from_config(config)

    logging.info("✅ Pipeline RAG initialisé avec succès")

except Exception as e:
    logging.error(f"❌ Erreur lors de l'initialisation du pipeline: {e}")
    raise e


# ------------------------------------------
# Modèles Pydantic pour Swagger / OpenAPI
# ------------------------------------------

class IngestRequest(BaseModel):
    source: str = Field(..., description="Chemin ou URL du document à ingérer")
    loader_name: str = Field(..., description="Nom du loader à utiliser")
    chunker_name: str = Field(..., description="Nom du chunker à utiliser")
    loader_params: Optional[Dict[str, Any]] = Field({}, description="Paramètres du loader")
    chunker_params: Optional[Dict[str, Any]] = Field({}, description="Paramètres du chunker")

class QueryRequest(BaseModel):
    question: str = Field(..., description="Question à poser au pipeline RAG")
    top_k: int = Field(5, description="Nombre de résultats à retourner")
    rerank_top_k: Optional[int] = Field(None, description="Nombre de résultats à reranker")
    streaming: Optional[bool] = Field(False, description="Si True, active le streaming des réponses")

# ------------------------------------------
# FastAPI App
# ------------------------------------------

app = FastAPI(title="RAG API", version="1.0")

# ------------------------------------------
# Endpoint : ingestion
# ------------------------------------------

@app.post("/ingest", summary="Ingestion de documents")
def ingest_docs(req: IngestRequest):
    try:
        # DummyPipeline n'a pas de factory, donc on appelle directement ingest
        chunks_ingested = pipeline.ingest(
            loader=DummyPipeline(),  # Pour tests, on peut remplacer par le vrai loader
            chunker=DummyPipeline(), # Pour tests, on peut remplacer par le vrai chunker
            source=req.source
        )
        return {"status": "success", "chunks_ingested_count": chunks_ingested}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------
# Endpoint : query
# ------------------------------------------

@app.post("/query", summary="Interrogation du pipeline")
async def ask_question(req: QueryRequest):
    if req.streaming:
        async def event_generator():
            try:
                response: RAGResponse = pipeline.query(req.question, top_k=req.top_k, rerank_top_k=req.rerank_top_k)
                answer = response.answer
                for i in range(0, len(answer), 50):
                    yield f"data: {answer[i:i+50]}\n\n"
                    await asyncio.sleep(0.05)
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: Erreur: {str(e)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        try:
            response: RAGResponse = pipeline.query(req.question, top_k=req.top_k, rerank_top_k=req.rerank_top_k)
            return response.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------
# Endpoint : stats
# ------------------------------------------

@app.get("/stats", summary="Récupération des statistiques")
def get_pipeline_stats():
    try:
        return pipeline.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------
# Startup Event
# ------------------------------------------

@app.on_event("startup")
def startup_event():
    logging.info("✅ RAG API démarrée et pipeline initialisé")

# ------------------------------------------
# Exemples JSON pour Swagger
# ------------------------------------------

"""
Exemple JSON pour /ingest :
{
  "source": "data/documents/doc1.txt",
  "loader_name": "text_loader",
  "chunker_name": "simple_chunker",
  "loader_params": {},
  "chunker_params": {}
}

Exemple JSON pour /query :
{
  "question": "Qui est le président du Bénin ?",
  "top_k": 5,
  "rerank_top_k": 3,
  "streaming": false
}
"""
