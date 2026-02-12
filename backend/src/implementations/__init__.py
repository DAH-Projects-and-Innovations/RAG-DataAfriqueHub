from src.core.factory import RAGPipelineFactory
from src.core.interfaces import (
    IEmbedder, IVectorStore, ILLM, IDocumentLoader, 
    IChunker, IRetriever, IQueryRewriter, IReranker
)
from src.llm.mistral_llm import MistralLLM
from src.Loaders.text_loader import UnifiedDocumentLoader
from src.retrieval.retrieval_strategy import RetrievalStrategy
from src.Chunkers.basic_chunker import ConfigurableChunker
from src.Embedders.dummy_embedder import LocalSentenceEmbedder
from src.vectorstores.simple_store import FAISSVectorStore
from src.vectorstores.chroma_store import ChromaVectorStore
from src.retrieval.reranker import CohereReranker

from src.llm import OllamaLLM, LLMAdapter



# ==========================================
# 1. STUBS GÉNÉRIQUES (Acceptent tous les arguments)
# ==========================================

class TextLoader(IDocumentLoader):
    def load(self, source: str):
        print(f"📖 [Stub] Chargement de : {source}")
        return []
    
   
    def get_supported_formats(self) -> list[str]:
        return [".txt", ".md"]

class OverlapChunker(IChunker):
    def chunk(self, documents: list) -> list:
        print(f"✂️ [Stub] Découpage des documents...")
        return []



class MainEmbedder(IEmbedder):
    def __init__(self, **kwargs): pass # Accepte model_name, device, etc.
    def embed_query(self, text: str): return [0.0] * 1536
    def embed_texts(self, texts: list[str]): return [[0.0] * 1536 for _ in texts]
    def get_dimension(self): return 1536

class MainVectorStore(IVectorStore):
    def __init__(self, **kwargs): pass
    def add_chunks(self, chunks, embeddings): return True
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

# ==========================================
# 2. ENREGISTREMENT
# ==========================================

def register_all_components():
    f = RAGPipelineFactory
    f.register_component("loaders", "text_loader", UnifiedDocumentLoader)
    f.register_component("chunkers", "overlap_chunker", ConfigurableChunker)
    f.register_component("embedders", "sentence_transformers", LocalSentenceEmbedder)
    f.register_component("vector_stores", "chroma", ChromaVectorStore)
    f.register_component("retrievers", "vector_retriever", RetrievalStrategy)
    f.register_component("query_rewriters", "llm_rewriter", MainRewriter)
    f.register_component("rerankers", "cohere", CohereReranker)
    f.register_component("llms", "ollama", LLMAdapter)

    print("✅ [INFO] Branchement API validé.")