from ..core.factory import RAGPipelineFactory
from .openai_llm import OpenAILLM
from .ollama_llm import LocalLLM
from .mistral_llm import MistralLLM

# Enregistrement automatique des composants LLM
RAGPipelineFactory.register_component('llms', 'openai', OpenAILLM)
RAGPipelineFactory.register_component('llms', 'local', LocalLLM)
RAGPipelineFactory.register_component('llms', 'mistral', MistralLLM)

__all__ = ['OpenAILLM', 'LocalLLM', 'MistralLLM']
