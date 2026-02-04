from fastapi import FastAPI
from src.api.routes import query, ingest
from src.api.dependencies import get_pipeline
from fastapi import Depends

app = FastAPI(title="Modular RAG API", version="1.0.0")

app.include_router(query.router)
app.include_router(ingest.router)

@app.get("/health")
def health(pipeline = Depends(get_pipeline)):
    return {"status": "up", "stats": pipeline.get_stats()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
