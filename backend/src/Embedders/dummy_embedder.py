from typing import List
from sentence_transformers import SentenceTransformer
from src.core.interfaces import IEmbedder

class LocalSentenceEmbedder(IEmbedder):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, query: str, **kwargs) -> List[float]:
        return self.model.encode(query).tolist()

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()