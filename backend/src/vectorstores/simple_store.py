import logging
import os
import pickle
from typing import Any

import faiss
import numpy as np

from src.core.interfaces import IVectorStore
from src.core.models import Chunk

logger = logging.getLogger(__name__)

# Compteur global pour générer des IDs FAISS uniques et monotones,
# indépendants de self.index.ntotal (qui varie après les suppressions).
_next_id: int = 0


def _new_ids(n: int) -> np.ndarray:
    """Retourne n IDs entiers 64-bit uniques pour IndexIDMap."""
    global _next_id
    ids = np.arange(_next_id, _next_id + n, dtype=np.int64)
    _next_id += n
    return ids


class FAISSVectorStore(IVectorStore):
    """Vector store FAISS avec suppression réelle des vecteurs via IndexIDMap.

    Contrairement à IndexFlatIP/L2, IndexIDMap(base) associe chaque vecteur
    ajouté à un ID arbitraire (int64) et expose remove_ids() pour les effacer
    réellement de l'index — pas seulement du dictionnaire chunks_map.
    Cela garantit que :
    - search(top_k=k) retourne toujours k résultats vivants (si disponibles)
    - get_collection_stats() rapporte un compte exact
    - l'index ne grossit pas indéfiniment après des suppressions
    """

    def __init__(
        self,
        dimension: int = 1024,  # BGE-large-en-v1.5 utilise 1024
        persist_directory: str = "./data/faiss_db",
        collection_name: str = "documents",
        distance_metric: str = "cosine",
        **kwargs,
    ):
        self.dimension = dimension
        self.distance_metric = distance_metric
        self.folder_path = persist_directory
        self.index_path = os.path.join(self.folder_path, f"{collection_name}_index.faiss")
        self.map_path = os.path.join(self.folder_path, f"{collection_name}_chunks.pkl")

        os.makedirs(self.folder_path, exist_ok=True)

        if os.path.exists(self.index_path) and os.path.exists(self.map_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.map_path, "rb") as f:
                self.chunks_map: dict[int, Chunk] = pickle.load(f)
            # Resynchroniser le compteur global au-delà du max ID connu
            if self.chunks_map:
                global _next_id
                _next_id = max(self.chunks_map.keys()) + 1
            logger.info(
                "FAISSVectorStore chargé : %d vecteurs, %d chunks",
                self.index.ntotal,
                len(self.chunks_map),
            )
        else:
            self.index = self._build_empty_index()
            self.chunks_map = {}

    # ------------------------------------------------------------------
    # Helpers internes
    # ------------------------------------------------------------------

    def _build_empty_index(self) -> faiss.Index:
        """Crée un IndexIDMap wrappant IndexFlatIP (cosine) ou IndexFlatL2."""
        if self.distance_metric == "cosine":
            base = faiss.IndexFlatIP(self.dimension)
        else:
            base = faiss.IndexFlatL2(self.dimension)
        return faiss.IndexIDMap(base)

    def _persist(self) -> None:
        """Sauvegarde l'index et la map sur disque."""
        faiss.write_index(self.index, self.index_path)
        with open(self.map_path, "wb") as f:
            pickle.dump(self.chunks_map, f)

    # ------------------------------------------------------------------
    # Interface IVectorStore
    # ------------------------------------------------------------------

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        embeddings = np.array([c.embedding for c in chunks], dtype="float32")
        if self.distance_metric == "cosine":
            faiss.normalize_L2(embeddings)

        ids = _new_ids(len(chunks))
        self.index.add_with_ids(embeddings, ids)

        for faiss_id, chunk in zip(ids, chunks):
            self.chunks_map[int(faiss_id)] = chunk

        self._persist()
        logger.debug("Ajout de %d chunks (IDs %d–%d)", len(chunks), ids[0], ids[-1])

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[Chunk]:
        query_vec = np.array([query_embedding]).astype("float32")
        # Normalisation de la requête pour la similarité cosine
        faiss.normalize_L2(query_vec)

        # Sur-échantillonnage : FAISS ne filtre pas nativement,
        # on compense en cherchant plus de candidats avant le post-filtre.
        fetch_k = top_k * 4 if filters else top_k
        distances, indices = self.index.search(query_vec, min(fetch_k, self.index.ntotal or 1))

        results: list[Chunk] = []
        for idx in indices[0]:
            if idx == -1 or idx not in self.chunks_map:
                continue  # -1 = aucun résultat FAISS
            chunk = self.chunks_map[idx]
            # Post-filtrage : on vérifie chaque condition du dict `filters`
            if filters and not all(
                chunk.metadata.get(k) == v for k, v in filters.items()
            ):
                continue
            results.append(chunk)
            if len(results) >= top_k:
                break

        return results

    def delete(self, where: dict[str, Any]) -> None:
        """Supprime les vecteurs correspondant aux filtres *de l'index FAISS*
        et de chunks_map (fix #15 : auparavant seul chunks_map était nettoyé).

        Args:
            where: Filtres metadata (ex: {"filename": "rapport.pdf"})
        """
        if not where:
            raise ValueError("Un filtre 'where' non vide est requis.")

        ids_to_remove = [
            idx
            for idx, chunk in self.chunks_map.items()
            if all(chunk.metadata.get(k) == v for k, v in where.items())
        ]

        if not ids_to_remove:
            logger.info("delete() : aucun chunk correspondant à %s", where)
            return

        # 1. Supprimer les vecteurs de l'index FAISS (suppression réelle)
        remove_array = np.array(ids_to_remove, dtype=np.int64)
        self.index.remove_ids(remove_array)

        # 2. Nettoyer la map
        for idx in ids_to_remove:
            del self.chunks_map[idx]

        self._persist()
        logger.info(
            "delete() : %d chunk(s) supprimés pour %s, index FAISS = %d vecteurs",
            len(ids_to_remove),
            where,
            self.index.ntotal,
        )

    def delete_collection(self, collection_name: str) -> None:
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.map_path):
            os.remove(self.map_path)
        self.index = self._build_empty_index()
        self.chunks_map = {}

    def get_collection_stats(self, collection_name: str) -> dict[str, Any]:
        # ntotal est maintenant exact car les suppressions sont réelles
        return {"total_vectors": self.index.ntotal}
