from typing import List, Optional, Any
from sentence_transformers import SentenceTransformer
from src.core.interfaces import IEmbedder

class LocalSentenceEmbedder(IEmbedder):
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2", 
        device: Optional[str] = None,
        **kwargs  # Capture normalize_embeddings, batch_size, etc.
    ):
        # Initialisation du modèle avec le device
        self.model = SentenceTransformer(model_name, device=device)
        
        # Stockage des paramètres par défaut pour l'encodage
        self.default_kwargs = kwargs

    def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        # On fusionne les paramètres de la config avec d'éventuels paramètres à l'appel
        params = {**self.default_kwargs, **kwargs}
        embeddings = self.model.encode(texts, **params)
        return embeddings.tolist()

    def embed_query(self, query: str, **kwargs) -> List[float]:
        params = {**self.default_kwargs, **kwargs}
        return self.model.encode(query, **params).tolist()

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()