import os
from typing import List, Dict, Any, Optional
import logging
from mistralai import Mistral

from ..core.interfaces import ILLM
from ..core.models import Document

logger = logging.getLogger(__name__)

class MistralLLM(ILLM):
    """Implémentation Mistral AI du LLM utilisant l'API Mistral (via client compatible OpenAI)"""
    
    def __init__(self, model_name: str = "mistral-small-latest", api_key: Optional[str] = None,
                 system_prompt: Optional[str] = None, user_prompt_template: Optional[str] = None):
        """
        Initialise le client Mistral AI (compatible OpenAI)
        
        Args:
            model_name: Nom du modèle (ex: mistral-small-latest, mistral-large-latest)
            api_key: Clé API Mistral (optionnel, lit la variable d'env MISTRAL_API_KEY par défaut)
            system_prompt: Template du prompt système (optionnel)
            user_prompt_template: Template du prompt utilisateur (optionnel)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        
        # Mistral AI endpoint
        self.base_url = "https://api.mistral.ai/v1"
        
        self.client = Mistral(api_key=self.api_key)
    
        model = "mistral-medium-latest"

        
        
        # Message de refus standard
        self.refusal_message = "Je ne dispose pas d’informations fiables dans les documents fournis pour répondre à cette question."
        
        # Default System Prompt avec instruction de refus stricte
        self.default_system_prompt = system_prompt or (
            "Tu es un assistant précis et fiable. Utilise EXCLUSIVEMENT les documents fournis pour répondre à la question.\n"
            "Si l'information n'est pas dans les documents, tu DOIS répondre exactement :\n"
            f"'{self.refusal_message}'\n"
            "Ne fais aucune supposition. Cite tes sources entre crochets si possible."
        )
        
        # Default User Prompt Template
        self.default_user_prompt_template = user_prompt_template or "Contexte:\n{context_str}\n\nQuestion: {query}"
        
        logger.info(f"MistralLLM initialisé avec le modèle: {model_name}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse simple
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur lors de la génération Mistral: {e}")
            raise

    def generate_with_context(self, query: str, context: List[Document], **kwargs) -> str:
        """
        Génère une réponse RAG basée sur le contexte
        """
        # Construction du contexte
        context_str = "\n\n".join([f"Document {i+1}:\n{doc.content}" for i, doc in enumerate(context)])
        
        # Utilisation des prompts configurés ou des overrides via kwargs
        system_prompt = kwargs.get('system_prompt', self.default_system_prompt)
        user_template = kwargs.get('user_prompt_template', self.default_user_prompt_template)
        
        user_prompt = user_template.format(context_str=context_str, query=query)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur lors de la génération RAG Mistral: {e}")
            raise
