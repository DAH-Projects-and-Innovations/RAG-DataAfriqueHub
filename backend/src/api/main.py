from fastapi import FastAPI, Depends, Request
from src.api.routes import query, ingest
from src.api.dependencies import get_pipeline
from contextlib import asynccontextmanager

# --- IL FAUT DÉCOMMENTER CES LIGNES ---
from src.core.factory import RAGPipelineFactory 
from src.implementations import register_all_components 
# Note : j'ai ajusté les noms selon tes messages précédents (core et implementations)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie : s'exécute une seule fois au lancement"""
    # 1. Enregistrement des composants
    register_all_components()
    
    # 2. Chargement de la config et création du pipeline
    config = RAGPipelineFactory.load_config('configs/hybrid.yaml')
    pipeline_instance = RAGPipelineFactory.create_from_config(config)
    
    # 3. Stockage dans l'état global de l'app
    app.state.pipeline = pipeline_instance
    
    print("🚀 Pipeline RAG instancié et prêt !")
    yield
    print("🛑 Arrêt de l'API")

app = FastAPI(
    title="Modular RAG API", 
    version="1.0.0",
    lifespan=lifespan 
)

app.include_router(query.router)
app.include_router(ingest.router)

@app.get("/health")
def health(request: Request):
    pipeline = request.app.state.pipeline
    return {"status": "up", "stats": pipeline.get_stats()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)