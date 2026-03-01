from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.request import QueryRequest
from src.api.dependencies import get_pipeline

router = APIRouter(prefix="/query", tags=["RAG"])
print("📡 Query router ready")  # Log pour vérifier que le routeur est chargé

@router.post("")
async def ask_question(req, pipeline = Depends(get_pipeline)):
    try:
        print(f"Received query request: {req}")
        # Appel du pipeline
        response = "Yes"
        #response = pipeline.query(
        #    query_text=req.question,
        #    top_k=req.top_k,
        #    rerank_top_k=req.rerank_top_k
        #)

        # On ignore l'option streaming
        # On renvoie un dictionnaire structuré
        return {
            "answer": response.answer,
            "metadata": response.metadata if hasattr(response, 'metadata') else {},
            "sources": response.sources if hasattr(response, 'sources') else []
        }

    except Exception as e:
        print(f"Error during query processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur Query: {str(e)}")