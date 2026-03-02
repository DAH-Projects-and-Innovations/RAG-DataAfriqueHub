# backend/src/api/routes/ingest.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid
import json
import os
from typing import List, Dict, Any

from src.Chunkers.basic_chunker import ConfigurableChunker
from src.Loaders.text_loader import UnifiedDocumentLoader
from src.api.schemas.request import IngestRequest
from src.api.dependencies import get_pipeline
# ON RE-IMPORTE LA FACTORY POUR CRÉER LES COMPOSANTS
from src.core.factory import RAGPipelineFactory

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

# Crée un dossier unique par instance de l'API pour stocker les fichiers uploadés.
# Ainsi, on n'utilisera qu'un seul UUID pour toute la durée de vie du processus.
BASE_UPLOAD_DIR = Path("data/uploads")
INSTANCE_UPLOAD_DIR = BASE_UPLOAD_DIR / str(uuid.uuid4())
INSTANCE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/old")
async def ingest_document(req: IngestRequest, pipeline=Depends(get_pipeline)):
    """
    Ingestion via chemin local ou URL.
    """
    try:
        # CRÉATION DES COMPOSANTS EXIGÉS PAR LE PIPELINE
        loader = RAGPipelineFactory._create_component("loaders", {
            "name": req.loader_name,
            "params": req.loader_params
        })
        chunker = RAGPipelineFactory._create_component("chunkers", {
            "name": req.chunker_name,
            "params": req.chunker_params
        })

        # APPEL AVEC LES OBJETS CRÉÉS
        count = pipeline.ingest(loader=loader, chunker=chunker, source=req.source)
        return {"status": "success", "chunks_ingested": int(count)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@router.post("")
async def ingest_uploaded_pdfs(
    files: List[UploadFile] = File(..., description="Upload un ou plusieurs fichiers PDF"),
    loader_name: str = Form("pdf_loader"),
    chunker_name: str = Form("overlap_chunker"),
    loader_params: str = Form("{}"), 
    chunker_params: str = Form("{}"),
    pipeline=Depends(get_pipeline),
):
    """
    Upload de plusieurs PDF, sauvegarde, puis ingestion.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="Aucun fichier envoyé.")

        # 1. Conversion des paramètres
        try:
            l_params = json.loads(loader_params) if loader_params else {}
            c_params = json.loads(chunker_params) if chunker_params else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="JSON invalide.")

        # 2. Création des COMPOSANTS (Loader & Chunker) requis par pipeline.ingest
        
        # 3. Dossier temporaire (utilise l'UUID créé une fois pour l'instance)
        upload_dir = INSTANCE_UPLOAD_DIR

        total_chunks = 0
        details = []

        for f in files:
            if not f.filename.lower().endswith(".pdf"):
                continue

            safe_name = f"{uuid.uuid4()}_{f.filename}"
            file_path = upload_dir / safe_name

            # Sauvegarde
            try:
                with file_path.open("wb") as buffer:
                    shutil.copyfileobj(f.file, buffer)
            finally:
                await f.close()

        # 4. Ingestion avec les arguments positionnels loader et chunker
        chunks = pipeline.ingest(
            loader=UnifiedDocumentLoader(),
            chunker=ConfigurableChunker(),
            source=str(upload_dir)
        )
        
        chunks_count = int(chunks) if isinstance(chunks, str) else chunks
        total_chunks += chunks_count
        details.append({"filename": f.filename, "chunks_ingested": chunks_count})

        return {
            "status": "success",
            "documents_processed": len(details),
            "chunks_ingested_total": total_chunks,
            "details": details,
        }

    except Exception as e:
        print(f"Erreur lors de l'ingestion : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))