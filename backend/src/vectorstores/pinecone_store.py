import logging
import uuid
from typing import List, Dict, Any, Optional

from src.core.interfaces import IVectorStore
from src.core.models import Chunk, Document

logger = logging.getLogger(__name__)

# Taille max par batch pour l'API Pinecone
_UPSERT_BATCH_SIZE = 100


class PineconeVectorStore(IVectorStore):
    """
    Vector store utilisant Pinecone (SDK v3+).

    Prérequis: `uv add pinecone`

    L'index doit exister dans Pinecone avant utilisation, ou sera créé
    automatiquement si `create_index_if_missing=True` (désactivé par défaut
    pour éviter les créations non souhaitées en prod).
    """

    def __init__(
        self,
        api_key: str,
        index_name: str = "rag-documents",
        dimension: int = 3072,
        metric: str = "cosine",
        namespace: str = "",
        environment: str = "us-east-1-aws",
        create_index_if_missing: bool = True,
        **kwargs,
    ):
        try:
            from pinecone import Pinecone, ServerlessSpec
            self._ServerlessSpec = ServerlessSpec
        except ImportError as e:
            raise ImportError(
                "Le package 'pinecone' est requis pour PineconeVectorStore. "
                "Installez-le avec : uv add pinecone"
            ) from e

        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.namespace = namespace

        # Crée l'index s'il n'existe pas encore
        existing = [idx.name for idx in self.pc.list_indexes()]
        if index_name not in existing:
            if create_index_if_missing:
                logger.info("Création de l'index Pinecone '%s' (dim=%d, metric=%s)...", index_name, dimension, metric)
                # On parse l'environnement pour la spec serverless (ex: "us-east-1-aws" → cloud=aws, region=us-east-1)
                cloud, region = self._parse_environment(environment)
                self.pc.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric=metric,
                    spec=ServerlessSpec(cloud=cloud, region=region),
                )
            else:
                raise ValueError(
                    f"L'index Pinecone '{index_name}' n'existe pas. "
                    "Créez-le manuellement ou passez create_index_if_missing=True."
                )

        self.index = self.pc.Index(index_name)
        stats = self.index.describe_index_stats()
        logger.info(
            "PineconeVectorStore connecté — index: '%s', vecteurs: %s",
            index_name,
            stats.get("total_vector_count", "?"),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_environment(env: str):
        """
        Convertit 'us-east-1-aws' → (cloud='aws', region='us-east-1').
        Supporte aussi 'gcp-starter' → (cloud='gcp', region='us-central1').
        """
        if env == "gcp-starter":
            return "gcp", "us-central1"
        parts = env.rsplit("-", 1)
        if len(parts) == 2:
            return parts[1], parts[0]
        return "aws", env

    @staticmethod
    def _chunk_id(chunk: Chunk, index: int) -> str:
        cid = getattr(chunk, "chunk_id", None)
        if cid:
            return str(cid)
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.content[:64]}_{index}"))

    def _metadata_to_pinecone(self, meta: dict) -> dict:
        """Pinecone n'accepte que str/int/float/bool dans les métadonnées."""
        clean = {}
        for k, v in (meta or {}).items():
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            else:
                clean[k] = str(v)
        return clean

    # ------------------------------------------------------------------
    # IVectorStore
    # ------------------------------------------------------------------

    def add_chunks(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return

        vectors = []
        for i, chunk in enumerate(chunks):
            if chunk.embedding is None:
                logger.warning("Chunk %d sans embedding — ignoré", i)
                continue
            vectors.append({
                "id": self._chunk_id(chunk, i),
                "values": chunk.embedding,
                "metadata": {
                    **self._metadata_to_pinecone(getattr(chunk, "metadata", {})),
                    "content": chunk.content,  # stocké dans metadata pour la récupération
                },
            })

        # Upsert par batches
        for start in range(0, len(vectors), _UPSERT_BATCH_SIZE):
            batch = vectors[start : start + _UPSERT_BATCH_SIZE]
            self.index.upsert(vectors=batch, namespace=self.namespace)
            logger.debug("Upsert Pinecone: %d vecteurs (batch %d)", len(batch), start // _UPSERT_BATCH_SIZE + 1)

        logger.info("%d chunks indexés dans Pinecone (namespace='%s')", len(vectors), self.namespace)

    def search(self, query_embedding: List[float], top_k: int = 5, **kwargs) -> List[Document]:
        filter_dict: Optional[Dict[str, Any]] = kwargs.get("filter")
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=self.namespace,
            filter=filter_dict,
        )

        docs: List[Document] = []
        for match in response.get("matches", []):
            meta = dict(match.get("metadata", {}))
            content = meta.pop("content", "")
            meta["score"] = float(match.get("score", 0.0))
            docs.append(Document(content=content, metadata=meta))

        return docs

    def delete(self, where: Dict[str, Any]) -> None:
        """
        Supprime les vecteurs dont les métadonnées correspondent aux filtres.

        Pinecone ne supporte pas la suppression par filtre metadata directement —
        on doit d'abord récupérer les IDs via une requête zéro, puis les supprimer.

        Args:
            where: Filtres metadata (ex: {"filename": "rapport.pdf"})

        Raises:
            ValueError: Si aucun filtre n'est fourni.
        """
        if not where:
            raise ValueError("Un filtre 'where' non vide est requis pour éviter la suppression totale.")

        try:
            # On utilise un vecteur nul pour fetcher tous les IDs qui matchent le filtre
            # top_k max dans Pinecone est 10000
            dummy_vector = [0.0] * self.dimension
            response = self.index.query(
                vector=dummy_vector,
                top_k=10000,
                include_metadata=False,
                namespace=self.namespace,
                filter=where,
            )
            ids = [m["id"] for m in response.get("matches", [])]
            if not ids:
                logger.info("Aucun vecteur trouvé pour le filtre: %s", where)
                return

            # Suppression par batches
            for start in range(0, len(ids), _UPSERT_BATCH_SIZE):
                batch_ids = ids[start : start + _UPSERT_BATCH_SIZE]
                self.index.delete(ids=batch_ids, namespace=self.namespace)

            logger.info("%d vecteurs supprimés avec le filtre: %s", len(ids), where)
        except Exception as e:
            logger.error("Erreur lors de la suppression Pinecone avec filtre %s: %s", where, e)
            raise

    def delete_collection(self, collection_name: str) -> None:
        """Supprime l'index Pinecone entier (irréversible)."""
        try:
            self.pc.delete_index(collection_name)
            logger.info("Index Pinecone '%s' supprimé", collection_name)
        except Exception as e:
            logger.error("Erreur lors de la suppression de l'index '%s': %s", collection_name, e)
            raise

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", self.dimension),
                "namespaces": stats.get("namespaces", {}),
            }
        except Exception as e:
            logger.error("Erreur lors de la récupération des stats: %s", e)
            return {"total_vectors": 0}
