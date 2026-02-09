import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.core.orchestrator import RAGPipeline
from src.core.models import Document, Chunk
from src.loaders.document_loaders import UnifiedDocumentLoader
from src.chunkers.text_chunkers import ConfigurableChunker
from src.embedders.local_embedders import LocalSentenceEmbedder
from src.vectorstores.faiss_store import FAISSVectorStore

app = FastAPI(title="API d'Ingestion pour Document")

#  INITIALISATION

embedder = LocalSentenceEmbedder()
vector_store = FAISSVectorStore(dimension=embedder.get_dimension())

pipeline = RAGPipeline(
    embedder=embedder,
    vector_store=vector_store,
    retriever=None,
    llm=None
)


@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """Point d'entrée pour envoyer un document PDF, MD ou TXT"""
    
    # Pour la vérification du format d'un ficher 
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    if ext not in ["pdf", "md", "txt"]:
        raise HTTPException(status_code=400, detail="Format non supporté (utilisez PDF, MD ou TXT)")
    temp_path = f"temp_{filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Exécution du pipeline d'ingestion complet
        num_chunks = pipeline.ingest(
            loader=UnifiedDocumentLoader(),
            chunker=ConfigurableChunker(),
            source=temp_path,
            chunker_params={
                "chunk_size": 500,
                "chunk_overlap": 50
            }
        )

        return {
            "status": "success",
            "document": filename,
            "chunks_crees": num_chunks,
            "message": "Le document a été transformé en base de connaissance."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)