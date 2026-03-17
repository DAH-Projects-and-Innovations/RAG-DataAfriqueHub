# backend/src/api/routes/ingest.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pathlib import Path
import shutil
import uuid
from typing import List

from src.Chunkers.basic_chunker import ConfigurableChunker
from src.Loaders.text_loader import UnifiedDocumentLoader
from src.api.dependencies import get_pipeline

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

SUPPORTED_EXTENSIONS = {f".{fmt}" for fmt in UnifiedDocumentLoader().get_supported_formats()}

# 50 MB par fichier
MAX_FILE_BYTES = 50 * 1024 * 1024

BASE_UPLOAD_DIR = Path("data/uploads")
INSTANCE_UPLOAD_DIR = BASE_UPLOAD_DIR / str(uuid.uuid4())
INSTANCE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("")
async def ingest_uploaded_files(
    files: List[UploadFile] = File(..., description="Upload un ou plusieurs fichiers (PDF, TXT, MD)"),
    pipeline=Depends(get_pipeline),
):
    """
    Upload de fichiers, sauvegarde, puis ingestion dans le vector store.
    Formats supportés : PDF, TXT, MD.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier envoyé.")

    upload_dir = INSTANCE_UPLOAD_DIR
    saved_files: List[str] = []

    for f in files:
        suffix = Path(f.filename).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            continue

        # Vérification de la taille (UploadFile.size disponible depuis Starlette 0.20)
        file_size = getattr(f, "size", None)
        if file_size is not None and file_size > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"{f.filename} dépasse la taille maximale autorisée ({MAX_FILE_BYTES // (1024*1024)} MB).",
            )

        safe_name = f"{uuid.uuid4()}{suffix}"
        file_path = upload_dir / safe_name

        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            # Vérification post-écriture si la taille n'était pas disponible avant
            written_size = file_path.stat().st_size
            if written_size > MAX_FILE_BYTES:
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"{f.filename} dépasse la taille maximale autorisée ({MAX_FILE_BYTES // (1024*1024)} MB).",
                )
            saved_files.append(f.filename)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde de {f.filename}: {str(e)}")
        finally:
            await f.close()

    if not saved_files:
        raise HTTPException(
            status_code=400,
            detail=f"Aucun fichier valide. Formats acceptés : {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Utilise le chunker configuré dans le YAML si disponible, sinon fallback basique
    chunker = getattr(pipeline, "chunker", None) or ConfigurableChunker()

    try:
        chunks_count = pipeline.ingest(
            loader=UnifiedDocumentLoader(),
            chunker=chunker,
            source=str(upload_dir)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ingestion : {str(e)}")

    return {
        "status": "success",
        "documents_processed": len(saved_files),
        "chunks_ingested_total": int(chunks_count),
        "files": saved_files,
    }


@router.delete("/{file_name}")
async def delete_file(
    file_name: str, 
    pipeline=Depends(get_pipeline)
):
    """
    Supprime un document de la base de connaissances (Vector Store).
    """
    try:
        success = pipeline.delete_document(file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression : {str(e)}")

    if not success:
        raise HTTPException(status_code=404, detail="Document non trouvé dans l'index.")

    return {"status": "success", "message": f"Document {file_name} supprimé."}