import logging
from typing import List, Optional
from src.core.interfaces import IEmbedder

logger = logging.getLogger(__name__)

# Dimension par modèle OpenAI (valeurs par défaut)
_MODEL_DIMENSIONS = {
    "text-embedding-3-large": 3072,
    "text-embedding-3-small": 1536,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbedder(IEmbedder):
    """
    Embedder utilisant l'API OpenAI (text-embedding-3-large par défaut).
    Supporte la réduction de dimensions via le paramètre `dimensions`.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-large",
        dimensions: Optional[int] = None,
        **kwargs,
    ):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "Le package 'openai' est requis pour OpenAIEmbedder. "
                "Installez-le avec : uv add openai"
            ) from e

        self.client = OpenAI(api_key=api_key)
        self.model = model
        # dimensions=None → la dimension maximale du modèle est utilisée
        self.dimensions = dimensions
        self._default_dim = _MODEL_DIMENSIONS.get(model, 1536)
        logger.info(
            "OpenAIEmbedder initialisé — modèle: %s, dimensions: %s",
            model,
            dimensions or self._default_dim,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_kwargs(self) -> dict:
        kw: dict = {}
        if self.dimensions is not None:
            kw["dimensions"] = self.dimensions
        return kw

    # ------------------------------------------------------------------
    # IEmbedder
    # ------------------------------------------------------------------

    def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        if not texts:
            return []
        # L'API OpenAI accepte jusqu'à 2048 inputs par requête
        # On découpe en batches de 512 pour rester dans les limites de tokens
        batch_size = kwargs.pop("batch_size", 512)
        results: List[List[float]] = []
        kw = {**self._build_kwargs(), **kwargs}

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # Remplace les lignes vides par un espace pour éviter les erreurs API
            clean_batch = [t if t.strip() else " " for t in batch]
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=clean_batch,
                    **kw,
                )
                results.extend([item.embedding for item in response.data])
                logger.debug("Batch %d/%d embeddé (%d textes)", i // batch_size + 1, -(-len(texts) // batch_size), len(batch))
            except Exception as e:
                logger.error("Erreur lors de l'embedding du batch %d: %s", i // batch_size, e)
                raise

        return results

    def embed_query(self, query: str, **kwargs) -> List[float]:
        kw = {**self._build_kwargs(), **kwargs}
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=query if query.strip() else " ",
                **kw,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Erreur lors de l'embedding de la requête: %s", e)
            raise

    def get_dimension(self) -> int:
        if self.dimensions is not None:
            return self.dimensions
        return self._default_dim
