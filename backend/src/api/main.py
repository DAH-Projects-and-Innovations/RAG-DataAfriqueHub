import os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.dependencies import get_pipeline, verify_api_key
from src.api.routes import ingest, query
from src.api.routes.models import router as models_router

# Taille maximale autorisée pour les uploads (50 MB)
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

app = FastAPI(
    title="Modular RAG API",
    version="1.0.0",
    # Toutes les routes nécessitent une clé API valide (désactivé si API_KEY absent)
    dependencies=[Depends(verify_api_key)],
)

# Origines CORS autorisées.
# En production, définir CORS_ORIGINS dans le .env :
#   CORS_ORIGINS=https://mon-app.com,https://www.mon-app.com
# En dev local, la valeur par défaut (localhost) est utilisée si la variable est absente.
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:5173")
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_UPLOAD_BYTES:
        return JSONResponse(
            status_code=413,
            content={
                "detail": f"Fichier trop volumineux. Taille maximale : {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
            },
        )
    return await call_next(request)


app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(models_router)


@app.get("/health")
def health(pipeline=Depends(get_pipeline)):
    return {"status": "up", "stats": pipeline.get_stats()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
