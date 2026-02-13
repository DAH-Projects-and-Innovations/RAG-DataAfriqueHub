import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from src.core.interfaces import IVectorStore
from src.core.models import Chunk

class ChromaVectorStore(IVectorStore):
    def __init__(
        self, 
        persist_directory: str = "./data/chroma_db",
        collection_name: str = "documents",
        distance_metric: str = "cosine", # Chroma utilise 'cosine', 'l2' ou 'ip'
        **kwargs
    ):
        # Initialisation du client persistant
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Mappage de la métrique de distance (Chroma utilise "hnsw:space")
        # Les valeurs possibles sont "l2", "ip" ou "cosine"
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": distance_metric}
        )

    def add_chunks(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return

        # Chroma attend des listes séparées pour les IDs, embeddings, documents et métadonnées
        self.collection.add(
            ids=[str(c.id) if hasattr(c, 'id') else f"id_{i}_{hash(c.content)}" for i, c in enumerate(chunks)],
            embeddings=[c.embedding for c in chunks],
            metadatas=[c.metadata if hasattr(c, 'metadata') else {} for c in chunks],
            documents=[c.content for c in chunks]
        )

    def search(self, query_embedding: List[float], top_k: int = 5, **kwargs) -> List[Chunk]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Reconstruction des objets Chunk à partir des résultats
        chunks = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                chunks.append(Chunk(
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    embedding=results['embeddings'][0][i] if results['embeddings'] else None
                ))
        return chunks

    def delete_collection(self, collection_name: str) -> None:
        try:
            self.client.delete_collection(name=collection_name)
        except Exception as e:
            print(f"Erreur lors de la suppression : {e}")

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        return {"total_vectors": self.collection.count()}