from typing import List
from src.core.factory import RAGPipelineFactory
from src.core.interfaces import (
    IEmbedder, IVectorStore, ILLM, IDocumentLoader, 
    IChunker, IRetriever, IQueryRewriter, IReranker
)

from src.Loaders.text_loader import UnifiedDocumentLoader
from src.retrieval.retrieval_strategy import RetrievalStrategy
from src.Chunkers.basic_chunker import ConfigurableChunker
from src.Chunkers.semantic_chunker import SemanticChunker
from src.Embedders.dummy_embedder import LocalSentenceEmbedder
from src.vectorstores.simple_store import FAISSVectorStore
from src.vectorstores.chroma_store import ChromaVectorStore
from src.retrieval.reranker import CohereReranker, CrossEncoderReranker, NoOpReranker
from src.implementations.llm_query_rewriter import LLMQueryRewriter

from src.llm.llm_factory import LLMAdapterFactory
from src.llm.prompt_manager import create_default_prompt_manager



def register_all_components():
    f = RAGPipelineFactory
    f.register_component("loaders", "text_loader", UnifiedDocumentLoader)
    f.register_component("chunkers", "overlap_chunker", ConfigurableChunker)
    f.register_component("chunkers", "semantic_chunker", SemanticChunker)
    f.register_component("embedders", "sentence_transformers", LocalSentenceEmbedder)
    f.register_component("vector_stores", "chroma", ChromaVectorStore)
    f.register_component("retrievers", "vector_retriever", RetrievalStrategy)
    f.register_component("rerankers", "cross_encoder", CrossEncoderReranker)
    f.register_component("rerankers", "noop", NoOpReranker)
    f.register_component("rerankers", "cohere", CohereReranker)

    # LLMs - UTILISER LLMAdapterFactory au lieu de LLMAdapter
    f.register_component("llms", "mistral", LLMAdapterFactory)
    f.register_component("llms", "huggingface", LLMAdapterFactory)  # ← AJOUT HuggingFace
    f.register_component("llms", "openai", LLMAdapterFactory)       # ← AJOUT OpenAI
    f.register_component("llms", "gemini", LLMAdapterFactory)
    f.register_component("llms", "ollama", LLMAdapterFactory)
    
    # Query Rewriters
    f.register_component("query_rewriters", "llm_rewriter", LLMQueryRewriter)
    # Prompt Managers
    f.register_component("prompt_managers", "default", lambda: create_default_prompt_manager())

    print("✅ [INFO] Branchement API validé.")