# ==========================================
# src/implementations.py
# ==========================================

"""
Implémentations concrètes pour le pipeline RAG

- Loaders : chargement des documents
- Chunkers : découpage des documents
- Embedders : calcul des embeddings
- Retrievers : récupération des chunks pertinents
- Fonction d'enregistrement pour RAGPipelineFactory
"""

from typing import List
from src.core.models import Document, Chunk, Query, RAGResponse
from src.core.factory import RAGPipelineFactory

# -------------------------------
# Loaders
# -------------------------------
class TextLoader:
    """Charge un fichier texte et retourne un Document"""
    def __init__(self, **kwargs):
        pass

    def load(self, source: str) -> List[Document]:
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
        return [Document(content=content, metadata={"source": source})]

class PDFLoader:
    """Charge un PDF et retourne un Document"""
    def __init__(self, **kwargs):
        pass

    def load(self, source: str) -> List[Document]:
        # Ici on mettra la vraie logique PDF plus tard
        return [Document(content=f"[PDF content from {source}]", metadata={"source": source})]

# -------------------------------
# Chunkers
# -------------------------------
class SimpleChunker:
    """Découpe un document en chunks simples"""
    def __init__(self, chunk_size: int = 200, **kwargs):
        self.chunk_size = chunk_size

    def chunk(self, docs: List[Document]) -> List[Chunk]:
        chunks = []
        for doc in docs:
            text = doc.content
            for i in range(0, len(text), self.chunk_size):
                chunks.append(Chunk(content=text[i:i+self.chunk_size], doc_id=doc.doc_id))
        return chunks

class OverlapChunker:
    """Découpe avec chevauchement"""
    def __init__(self, chunk_size: int = 200, overlap: int = 50, **kwargs):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, docs: List[Document]) -> List[Chunk]:
        chunks = []
        for doc in docs:
            text = doc.content
            i = 0
            while i < len(text):
                end = min(i+self.chunk_size, len(text))
                chunks.append(Chunk(content=text[i:end], doc_id=doc.doc_id))
                i += self.chunk_size - self.overlap
        return chunks

# -------------------------------
# Embedders
# -------------------------------
class SentenceTransformerEmbedder:
    """Dummy embedder : transforme chaque chunk en vecteur (placeholder)"""
    def embed(self, chunks: List[Chunk]) -> List[Chunk]:
        for chunk in chunks:
            # Ici on mettra le vrai embedding
            chunk.embedding = [0.0] * 768
        return chunks

# -------------------------------
# Retrievers
# -------------------------------
class HybridRetriever:
    """Dummy retriever : retourne les chunks selon un critère simple"""
    def retrieve(self, query: Query, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        # Ici on mettra le vrai retrieval et reranking
        return chunks[:top_k]

# -------------------------------
# Pipeline Dummy (pour tests rapides)
# -------------------------------
class DummyPipeline:
    """Pipeline minimal pour tests"""
    def __init__(self):
        self.registry = {}

    def ingest(self, loader, chunker, source):
        docs = loader.load(source)
        chunks = chunker.chunk(docs)
        return len(chunks)

    def query(self, question, top_k=5, rerank_top_k=None):
        doc = Document(content=f"Réponse simulée pour : {question}", metadata={"source": "dummy"})
        return RAGResponse(answer=f"Réponse à '{question}'", sources=[doc], query=question)

    def get_stats(self):
        return {"documents": 1, "chunks": 1}

# -------------------------------
# Fonction d'enregistrement
# -------------------------------
def register_all_components():
    """Enregistre tous les composants auprès de RAGPipelineFactory"""
    RAGPipelineFactory.register_component("loaders", "text_loader", TextLoader)
    RAGPipelineFactory.register_component("loaders", "pdf_loader", PDFLoader)
    RAGPipelineFactory.register_component("chunkers", "simple_chunker", SimpleChunker)
    RAGPipelineFactory.register_component("chunkers", "overlap_chunker", OverlapChunker)
    RAGPipelineFactory.register_component("embedders", "sentence_transformers", SentenceTransformerEmbedder)
    RAGPipelineFactory.register_component("retrievers", "hybrid", HybridRetriever)
