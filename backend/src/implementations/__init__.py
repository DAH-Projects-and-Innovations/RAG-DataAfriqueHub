from typing import List
from src.core.factory import RAGPipelineFactory
from src.core.interfaces import (
    IEmbedder, IVectorStore, ILLM, IDocumentLoader, 
    IChunker, IRetriever, IQueryRewriter, IReranker
)

# ==========================================
# 1. STUBS GÉNÉRIQUES (Acceptent tous les arguments)
# ==========================================

from src.core.models import Document

class TextLoader(IDocumentLoader):
    def __init__(self, **kwargs):
        pass

    def load(self, source: str) -> List[Document]:
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
        return [Document(content=content, metadata={"source": source})]

    def get_supported_formats(self) -> list[str]:
        return [".txt", ".md"]

class PDFLoader(IDocumentLoader):
    def __init__(self, **kwargs):
        pass

    def load(self, source: str):
        print(f"📄 [Stub] Chargement PDF : {source}")
        # TODO: ici tu mettras ta vraie logique PDF (pypdf / pdfplumber)
        return []

    def get_supported_formats(self) -> list[str]:
        return [".pdf"]


class MainEmbedder(IEmbedder):
    def __init__(self, **kwargs): pass # Accepte model_name, device, etc.
    def embed_query(self, text: str): return [0.0] * 1536
    def embed_texts(self, texts: list[str]): return [[0.0] * 1536 for _ in texts]
    def get_dimension(self): return 1536

class MainVectorStore(IVectorStore):
    def __init__(self, **kwargs): pass
    def add_chunks(self, chunks, embeddings=None, **kwargs):
        # Stub: accepte les 2 modes (avec ou sans embeddings)
        return True
    def search(self, query_embedding, top_k):
        return {"documents": [["Test"]], "metadatas": [[{"source": "doc.txt"}]], "distances": [[0.1]], "ids": [["1"]]}
    def delete_collection(self): return True
    def get_collection_stats(self): return {"count": 0}


class MainRetriever(IRetriever):
    def __init__(self, **kwargs): pass
    def retrieve(self, query: str, top_k: int = 5): return []

class MainRewriter(IQueryRewriter):
    def __init__(self, **kwargs): pass # C'ÉTAIT ICI LE BLOCAGE !
    def rewrite(self, query: str): return query

class MainReranker(IReranker):
    def __init__(self, **kwargs): pass
    def rerank(self, query: str, documents: list, top_k: int = 5): return documents[:top_k]

class MainLLM(ILLM):
    def __init__(self, **kwargs): pass
    def generate_with_context(self, query, context, **kwargs): return "[STUB] Réponse RAG"
    def generate(self, prompt, **kwargs): return "[STUB] Réponse"
    def get_token_count(self, text): return len(text.split())

class OverlapChunker(IChunker):
    """
    Chunker minimal.
    Découpe basique des documents.
    À enrichir plus tard.
    """

    def __init__(self, **kwargs):
        pass

    def chunk(self, documents: List[str]) -> List[str]:
        # Version minimale : retourne les documents tels quels
        # (permet au pipeline de fonctionner sans erreur)
        return documents
# ==========================================
# 2. ENREGISTREMENT
# ==========================================

def register_all_components():
    f = RAGPipelineFactory
    f.register_component("loaders", "text_loader", TextLoader)
    f.register_component("loaders", "pdf_loader", PDFLoader)
    f.register_component("chunkers", "overlap_chunker", OverlapChunker)
    f.register_component("embedders", "sentence_transformers", MainEmbedder)
    f.register_component("vector_stores", "chroma", MainVectorStore)
    f.register_component("retrievers", "vector_retriever", MainRetriever)
    f.register_component("query_rewriters", "llm_rewriter", MainRewriter)
    f.register_component("rerankers", "cohere", MainReranker)
    f.register_component("llms", "openai", MainLLM)

    print("✅ [INFO] Branchement API validé.")