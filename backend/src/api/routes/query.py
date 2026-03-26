import logging
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.request import QueryRequest
from src.api.dependencies import get_pipeline

router = APIRouter(prefix="/query", tags=["RAG"])
logger = logging.getLogger(__name__)


@router.post("")
async def ask_question(req: QueryRequest, pipeline=Depends(get_pipeline)):
    try:
        logger.info(f"Requête reçue: question='{req.question}' top_k={req.top_k}")
        llm_params = req.llm_params or {}
        if req.chat_history:
            llm_params = {**llm_params, 'conversation_history': req.chat_history}

        response = pipeline.query(
            query_text=req.question,
            top_k=req.top_k,
            rerank_top_k=req.rerank_top_k,
            llm_params=llm_params
        )

        return response.to_dict()

    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur Query: {str(e)}")
