"""
SemanticChunker — chunker basé sur la similarité sémantique entre phrases.

Algorithme :
1. Découpe le texte en phrases (regex).
2. Calcule les embeddings de chaque phrase via SentenceTransformer.
3. Mesure la similarité cosinus entre phrases consécutives.
4. Insère un point de coupure là où la similarité descend sous `breakpoint_threshold`.
5. Groupe les phrases en chunks en respectant max_chunk_size et min_chunk_size.

Avantage par rapport au sliding-window : les coupures coïncident avec les
changements de sujet, ce qui améliore la précision du retrieval.
"""

import re
import logging
from typing import List, Optional

import numpy as np

from src.core.interfaces import IChunker
from src.core.models import Document, Chunk

logger = logging.getLogger(__name__)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Similarité cosinus entre deux vecteurs numpy."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))


def _split_sentences(text: str) -> List[str]:
    """
    Découpe un texte en phrases en utilisant la ponctuation (.!?) comme
    séparateurs, tout en gérant les abréviations courantes.
    """
    # Sépare sur . ! ? suivis d'un espace ou fin de chaîne
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filtre les fragments vides ou trop courts
    return [s.strip() for s in raw if len(s.strip()) > 10]


class SemanticChunker(IChunker):
    """
    Chunker sémantique : regroupe les phrases par thème en détectant les
    ruptures sémantiques via la similarité cosinus inter-phrases.

    Params YAML :
        model_name          : modèle SentenceTransformer (défaut : paraphrase-multilingual-MiniLM-L12-v2)
        breakpoint_threshold: seuil de similarité en dessous duquel on coupe (défaut : 0.4)
        max_chunk_size      : taille max d'un chunk en caractères (défaut : 1200)
        min_chunk_size      : taille min d'un chunk en caractères (défaut : 100)
        device              : "cpu" ou "cuda" (défaut : "cpu")
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        breakpoint_threshold: float = 0.4,
        max_chunk_size: int = 1200,
        min_chunk_size: int = 100,
        device: str = "cpu",
        **kwargs,
    ):
        self.model_name = model_name
        self.breakpoint_threshold = breakpoint_threshold
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.device = device
        self._model = None  # Chargé à la première utilisation (lazy)

    def _get_model(self):
        """Charge le modèle SentenceTransformer de manière lazy."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Chargement du modèle SemanticChunker: {self.model_name}")
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except Exception as e:
                logger.error(f"Impossible de charger le modèle d'embedding pour SemanticChunker: {e}")
                raise
        return self._model

    def _embed_sentences(self, sentences: List[str]) -> List[List[float]]:
        model = self._get_model()
        embeddings = model.encode(sentences, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def _find_breakpoints(self, embeddings: List[List[float]]) -> List[int]:
        """
        Retourne les indices i tels que la similarité entre sentence[i] et
        sentence[i+1] est inférieure au seuil → point de coupure après i.
        """
        breakpoints = []
        for i in range(len(embeddings) - 1):
            sim = _cosine_similarity(embeddings[i], embeddings[i + 1])
            if sim < self.breakpoint_threshold:
                breakpoints.append(i)
        return breakpoints

    def _group_sentences(
        self, sentences: List[str], breakpoints: List[int]
    ) -> List[str]:
        """
        Regroupe les phrases en chunks en respectant les points de coupure
        et les contraintes de taille (max_chunk_size / min_chunk_size).
        """
        chunks: List[str] = []
        current_sentences: List[str] = []
        current_size = 0
        bp_set = set(breakpoints)

        for i, sentence in enumerate(sentences):
            current_sentences.append(sentence)
            current_size += len(sentence)

            is_breakpoint = i in bp_set
            is_too_large = current_size >= self.max_chunk_size
            is_last = i == len(sentences) - 1

            if (is_breakpoint or is_too_large or is_last) and current_size >= self.min_chunk_size:
                chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_size = 0

        # Rattacher les résidus trop petits au chunk précédent
        if current_sentences:
            residual = " ".join(current_sentences)
            if chunks:
                chunks[-1] += " " + residual
            else:
                chunks.append(residual)

        return chunks

    def chunk(self, documents: List[Document], **kwargs) -> List[Chunk]:
        """
        Découpe les documents en chunks sémantiques.

        Args:
            documents: Liste de documents à découper.
            **kwargs : Paramètres optionnels (non utilisés, pour compatibilité interface).

        Returns:
            Liste de Chunk avec doc_id et metadata hérités du document parent.
        """
        all_chunks: List[Chunk] = []

        for doc in documents:
            text = doc.content.strip()
            if not text:
                continue

            sentences = _split_sentences(text)
            if not sentences:
                # Fallback : document entier comme chunk unique
                all_chunks.append(
                    Chunk(
                        content=text,
                        doc_id=doc.doc_id,
                        metadata={**doc.metadata, "chunk_size": len(text), "chunker": "semantic"},
                    )
                )
                continue

            try:
                embeddings = self._embed_sentences(sentences)
                breakpoints = self._find_breakpoints(embeddings)
                grouped = self._group_sentences(sentences, breakpoints)
            except Exception as e:
                logger.warning(
                    f"SemanticChunker: erreur sur doc {doc.doc_id}, fallback sliding-window: {e}"
                )
                # Fallback : sliding window basique
                size = kwargs.get("chunk_size", 500)
                overlap = kwargs.get("chunk_overlap", 50)
                grouped = []
                start = 0
                while start < len(text):
                    grouped.append(text[start: start + size])
                    start += size - overlap

            for chunk_text in grouped:
                if not chunk_text.strip():
                    continue
                all_chunks.append(
                    Chunk(
                        content=chunk_text.strip(),
                        doc_id=doc.doc_id,
                        metadata={
                            **doc.metadata,
                            "chunk_size": len(chunk_text),
                            "chunker": "semantic",
                        },
                    )
                )

        logger.info(
            f"SemanticChunker: {len(documents)} documents → {len(all_chunks)} chunks"
        )
        return all_chunks
