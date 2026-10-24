from src.core.interfaces import IChunker
from src.core.models import Chunk, Document


def _validate_chunk_params(chunk_size: int, chunk_overlap: int) -> None:
    """Vérifie que les paramètres de chunking sont cohérents.

    Raises:
        ValueError: Si chunk_overlap >= chunk_size, ce qui provoquerait
                    une boucle infinie dans le sliding-window chunker (fix #10).
    """
    if chunk_size <= 0:
        raise ValueError(
            f"chunk_size doit être strictement positif, reçu : {chunk_size}"
        )
    if chunk_overlap < 0:
        raise ValueError(
            f"chunk_overlap doit être >= 0, reçu : {chunk_overlap}"
        )
    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) doit être strictement inférieur à "
            f"chunk_size ({chunk_size}). Sinon le curseur de départ n'avance plus "
            "et la boucle devient infinie."
        )


class ConfigurableChunker(IChunker):
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, **kwargs):
        # fix #10 : validation dès la construction pour détecter une mauvaise config YAML
        _validate_chunk_params(chunk_size, chunk_overlap)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: list[Document], **kwargs) -> list[Chunk]:
        size = kwargs.get("chunk_size", self.chunk_size)
        overlap = kwargs.get("chunk_overlap", self.chunk_overlap)

        # fix #10 : on revalide ici car chunk() peut recevoir des kwargs qui
        # contournent la validation faite dans __init__.
        _validate_chunk_params(size, overlap)

        all_chunks = []

        for doc in documents:
            text = doc.content
            start = 0
            while start < len(text):
                end = start + size
                chunk_text = text[start:end]

                # Pour créer le chunk en liant le doc_id du parent
                new_chunk = Chunk(
                    content=chunk_text,
                    doc_id=doc.doc_id,
                    metadata={**doc.metadata, "chunk_size": len(chunk_text)},
                )
                all_chunks.append(new_chunk)

                # Calcul du prochain départ avec overlap
                start += size - overlap

        return all_chunks
