from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.request import IngestRequest
from src.api.dependencies import get_pipeline
from src.core.factory import RAGPipelineFactory

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("")
async def ingest_document(req: IngestRequest, pipeline = Depends(get_pipeline)):
    try:
        loader = RAGPipelineFactory._create_component('loaders', {
            "name": req.loader_name, "params": req.loader_params
        })
        chunker = RAGPipelineFactory._create_component('chunkers', {
            "name": req.chunker_name, "params": req.chunker_params
        })
        count = pipeline.ingest(loader=loader, chunker=chunker, source=req.source)
        return {"status": "success", "chunks_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
