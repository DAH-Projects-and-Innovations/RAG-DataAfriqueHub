from typing import List
from src.core.interfaces import IChunker
from src.core.models import Document, Chunk

class ConfigurableChunker(IChunker):
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, **kwargs):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: List[Document], **kwargs) -> List[Chunk]:
        size = kwargs.get('chunk_size', self.chunk_size)
        overlap = kwargs.get('chunk_overlap', self.chunk_overlap)
        all_chunks = []

        for doc in documents:
            text = doc.content
            start = 0
            while start < len(text):
                end = start + size
                chunk_text = text[start:end]
                
                # Pour crée le chunk en liant le doc_id du parent
                new_chunk = Chunk(
                    content=chunk_text,
                    doc_id=doc.doc_id,
                    metadata={**doc.metadata, "chunk_size": len(chunk_text)}
                )
                all_chunks.append(new_chunk)
                
                # pour le Calcul du prochain départ avec overlap
                start += (size - overlap)
                
        return all_chunks