# backend/src/api/routes/ingest.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid
import json
import os
from typing import List, Dict, Any

from src.api.schemas.request import IngestRequest
from src.api.dependencies import get_pipeline
# ON RE-IMPORTE LA FACTORY POUR CRÉER LES COMPOSANTS
from src.core.factory import RAGPipelineFactory

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("")
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


@router.post("/upload")
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
        loader = RAGPipelineFactory._create_component("loaders", {
            "name": loader_name,
            "params": l_params
        })
        chunker = RAGPipelineFactory._create_component("chunkers", {
            "name": chunker_name,
            "params": c_params
        })

        # 3. Dossier temporaire
        upload_dir = Path("data/uploads") / str(uuid.uuid4())
        upload_dir.mkdir(parents=True, exist_ok=True)

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
            #chunks = pipeline.ingest(
            #    loader=loader, 
            #    chunker=chunker, 
            #    source=str(file_path)
            #)
            
            chunks_count = 0 w #int(chunks)
            #total_chunks += chunks_count
            details.append({"filename": f.filename, "chunks_ingested": chunks_count})

        return {
            "status": "success",
            "documents_processed": len(details),
            "chunks_ingested_total": total_chunks,
            "details": details,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))