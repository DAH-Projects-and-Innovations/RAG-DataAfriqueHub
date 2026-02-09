# backend/src/api/routes/ingest.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid
import json
from typing import List, Dict, Any

from src.api.schemas.request import IngestRequest
from src.api.dependencies import get_pipeline
from src.core.factory import RAGPipelineFactory

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("")
async def ingest_document(req: IngestRequest, pipeline=Depends(get_pipeline)):
    """
    Ingestion d'un document via un chemin local ou une URL (1 document).
    """
    try:
        loader = RAGPipelineFactory._create_component("loaders", {
            "name": req.loader_name,
            "params": req.loader_params
        })
        chunker = RAGPipelineFactory._create_component("chunkers", {
            "name": req.chunker_name,
            "params": req.chunker_params
        })

        count = pipeline.ingest(loader=loader, chunker=chunker, source=req.source)
        return {"status": "success", "chunks_ingested": int(count)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def ingest_uploaded_pdfs(
    files: List[UploadFile] = File(..., description="Upload one or more PDF files"),
    loader_name: str = Form("pdf_loader"),
    chunker_name: str = Form("overlap_chunker"),
    loader_params: str = Form("{}"),     # JSON string
    chunker_params: str = Form("{}"),    # JSON string
    pipeline=Depends(get_pipeline),
):
    """
    Upload de plusieurs PDF (multipart/form-data), sauvegarde sur disque, puis ingestion.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")

        # Parse params JSON -> dict
        try:
            loader_params_dict: Dict[str, Any] = json.loads(loader_params) if loader_params else {}
            chunker_params_dict: Dict[str, Any] = json.loads(chunker_params) if chunker_params else {}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="loader_params and chunker_params must be valid JSON strings."
            )

        loader = RAGPipelineFactory._create_component("loaders", {
            "name": loader_name,
            "params": loader_params_dict
        })
        chunker = RAGPipelineFactory._create_component("chunkers", {
            "name": chunker_name,
            "params": chunker_params_dict
        })

        upload_dir = Path("data/uploads") / str(uuid.uuid4())
        upload_dir.mkdir(parents=True, exist_ok=True)

        total_chunks = 0
        details = []

        for f in files:
            # Validation simple du PDF
            if not (f.filename or "").lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"'{f.filename}' is not a PDF.")

            safe_name = f"{uuid.uuid4()}_{Path(f.filename).name}"
            out_path = upload_dir / safe_name

            with out_path.open("wb") as buffer:
                shutil.copyfileobj(f.file, buffer)

            chunks = pipeline.ingest(loader=loader, chunker=chunker, source=str(out_path))
            chunks = int(chunks)

            total_chunks += chunks
            details.append({"filename": f.filename, "chunks_ingested": chunks})

        return {
            "status": "success",
            "documents": len(details),
            "chunks_ingested_total": total_chunks,
            "details": details,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
