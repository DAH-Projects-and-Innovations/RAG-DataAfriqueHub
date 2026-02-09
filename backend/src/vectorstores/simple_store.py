import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any
from src.core.interfaces import IVectorStore
from src.core.models import Chunk

class FAISSVectorStore(IVectorStore):
    def __init__(self, dimension: int, folder_path: str = "storage"):
        self.folder_path = folder_path
        self.index_path = os.path.join(folder_path, "index.faiss")
        self.map_path = os.path.join(folder_path, "chunks.pkl")
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.index = faiss.IndexFlatL2(dimension)
            self.chunks_map = {}
        else:
            self.index = faiss.read_index(self.index_path)
            with open(self.map_path, 'rb') as f:
                self.chunks_map = pickle.load(f)

    def add_chunks(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return
            
        embeddings = np.array([c.embedding for c in chunks]).astype('float32')
        start_idx = self.index.ntotal
        
        self.index.add(embeddings)
        
        for i, chunk in enumerate(chunks):
            self.chunks_map[start_idx + i] = chunk
            
        # Pour Sauvegarder le sur disque
        faiss.write_index(self.index, self.index_path)
        with open(self.map_path, 'wb') as f:
            pickle.dump(self.chunks_map, f)

    def search(self, query_embedding: List[float], top_k: int = 5, **kwargs) -> List[Chunk]:
        query_vec = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vec, top_k)
        
        results = []
        for idx in indices[0]:
            if idx in self.chunks_map:
                results.append(self.chunks_map[idx])
        return results

    def delete_collection(self, collection_name: str) -> None:
        pass

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        return {"total_vectors": self.index.ntotal}