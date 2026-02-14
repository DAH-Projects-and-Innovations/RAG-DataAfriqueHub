from typing import List, Dict, Any, Optional
import logging
import os
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from ..core.interfaces import ILLM
from ..core.models import Document

logger = logging.getLogger(__name__)

class LocalLLM(ILLM):
    """Implémentation LLM Local (Embedded) utilisant LlamaCpp"""
    
    def __init__(self, model_path: str, n_ctx: int = 2048, temperature: float = 0.7, 
                 system_prompt: Optional[str] = None, user_prompt_template: Optional[str] = None,
                 n_gpu_layers: int = -1):
        """
        Initialise le modèle local LlamaCpp
        
        Args:
            model_path: Chemin vers le fichier .gguf
            n_ctx: Taille du contexte (fenêtre)
            temperature: Température de génération
            system_prompt: Template du prompt système (optionnel)
            user_prompt_template: Template du prompt utilisateur (optionnel)
            n_gpu_layers: Nombre de couches à décharger sur le GPU (-1 = toutes, 0 = CPU only)
        """
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.temperature = temperature
        
        # Validation du fichier
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle introuvable : {model_path}. Utilisez scripts/download_model.py pour le télécharger.")

        logger.info(f"Chargement du modèle LlamaCpp depuis : {model_path}")
        
        # Callback pour le streaming (optionnel mais utile en dev)
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        # Initialisation de LlamaCpp
        try:
            self.llm = LlamaCpp(
                model_path=model_path,
                n_ctx=n_ctx,
                temperature=temperature,
                n_gpu_layers=n_gpu_layers,
                callback_manager=callback_manager,
                verbose=True,  # Utile pour le debug initial
                f16_kv=True,   # Optimisation mémoire
            )
        except Exception as e:
            logger.error(f"Erreur à l'initialisation de LlamaCpp : {e}")
            raise

        # Message de refus standard
        self.refusal_message = "Je ne dispose pas d’informations fiables dans les documents fournis pour répondre à cette question."
        
        # Default System Prompt avec instruction de refus stricte
        self.default_system_prompt = system_prompt or (
            "Tu es un assistant IA qui répond uniquement en se basant sur le contexte fourni.\n"
            "Si l'information n'est pas dans le documents, tu DOIS répondre exactement :\n"
            f"'{self.refusal_message}'\n"
        )
        
        # Default User Prompt Template
        self.default_user_prompt_template = user_prompt_template or "Contexte:\n{context_str}\n\nQuestion: {query}"

        logger.info("LocalLLM initialisé avec succès")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse via LlamaCpp
        """
        try:
            # LlamaCpp supporte l'invocation directe
            return self.llm.invoke(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Erreur lors de la génération LocalLLM: {e}")
            raise

    def generate_with_context(self, query: str, context: List[Document], **kwargs) -> str:
        """
        Génère une réponse RAG via LlamaCpp avec contexte
        """
        context_str = "\n\n".join([f"--- Document {i+1} ---\n{doc.content}" for i, doc in enumerate(context)])
        
        system_prompt_text = kwargs.get('system_prompt', self.default_system_prompt)
        user_template_text = kwargs.get('user_prompt_template', self.default_user_prompt_template)
        
        # Construction du prompt final
        # Pour LlamaCpp/GGUF, la gestion du template de chat (System/User/Assistant) dépend du modèle.
        # Ici on fait une construction générique simple, mais idéalement il faudrait utiliser les tokens spécifiques du modèle (ex: [INST] pour Mistral)
        # LangChain LlamaCpp ne gère pas automatiquement les chat templates complexes out-of-the-box sans configuration.
        # On concatène simplement pour l'instant.
        
        full_prompt = f"{system_prompt_text}\n\n{user_template_text.format(context_str=context_str, query=query)}"
        
        try:
            return self.llm.invoke(full_prompt)
        except Exception as e:
            logger.error(f"Erreur lors de la génération RAG LocalLLM: {e}")
            raise

