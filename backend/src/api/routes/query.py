import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.api.schemas.request import QueryRequest
from src.api.dependencies import get_pipeline

router = APIRouter(prefix="/query", tags=["RAG"])

@router.post("")
async def ask_question(req: QueryRequest, pipeline = Depends(get_pipeline)):
    try:
        response = pipeline.query(
            query_text=req.question,
            top_k=req.top_k,
            rerank_top_k=req.rerank_top_k
        )
        if req.streaming:
            async def event_generator():
                for word in response.answer.split(" "):
                    yield f"data: {word} \n\n"
                    await asyncio.sleep(0.05)
                yield "data: [DONE]\n\n"
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
