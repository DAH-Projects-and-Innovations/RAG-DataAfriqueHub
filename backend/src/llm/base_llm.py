"""
Abstraction LLM pour le moteur RAG.
Support d'APIs (OpenAI, Anthropic) et modèles open-source (Ollama, HuggingFace).
Pass
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()



class LLMProvider(Enum):
    """Providers LLM supportés."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    MISTRAL = "mistral"
    GEMINI = "gemini"
    


@dataclass
class LLMConfig:
    """Configuration pour un LLM."""
    provider: LLMProvider
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    top_k: int = 0  # 0 means no limit
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    
    # Paramètres spécifiques
    stream: bool = False
    timeout: int = 60

    num_ctx: int = 4096
    repeat_penalty: float = 1.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            'provider': self.provider.value,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'stream': self.stream,
            'timeout': self.timeout
        }


@dataclass
class LLMMessage:
    """Message pour le LLM."""
    role: str  # 'system', 'user', 'assistant'
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit en dictionnaire."""
        return {'role': self.role, 'content': self.content}


@dataclass
class LLMResponse:
    """Réponse du LLM."""
    content: str
    model: str
    usage: Dict[str, int]  # tokens utilisés
    finish_reason: str
    metadata: Dict[str, Any]
    
    def __str__(self) -> str:
        return self.content


class BaseLLM(ABC):
    """
    Classe abstraite pour tous les LLMs.
    
    Fournit une interface unifiée pour différents providers.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialise le LLM.
        
        Args:
            config: Configuration du LLM
        """
        self.config = config
        self._client = None
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialise le client du provider (lazy loading)."""
        pass
    
    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Génère une réponse.
        
        Args:
            messages: Liste de messages (conversation)
            **kwargs: Paramètres additionnels (override config)
            
        Returns:
            Réponse du LLM
        """
        pass
    
    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[LLMMessage]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Interface simplifiée pour chat.
        
        Args:
            user_message: Message de l'utilisateur
            system_prompt: Prompt système optionnel
            conversation_history: Historique de conversation
            **kwargs: Paramètres additionnels
            
        Returns:
            Réponse du LLM
        """
        messages = []
        
        # Ajouter le system prompt
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        
        # Ajouter l'historique
        if conversation_history:
            messages.extend(conversation_history)
        
        # Ajouter le message utilisateur
        messages.append(LLMMessage(role="user", content=user_message))
        
        return self.generate(messages, **kwargs)
    
    def get_config(self) -> Dict[str, Any]:
        """Retourne la configuration actuelle."""
        return self.config.to_dict()
    
    def update_config(self, **kwargs) -> None:
        """
        Met à jour la configuration.
        
        Args:
            **kwargs: Paramètres à mettre à jour
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


class OpenAILLM(BaseLLM):
    """LLM pour OpenAI (GPT-3.5, GPT-4, etc.)."""
    
    def _initialize_client(self) -> None:
        """Initialise le client OpenAI."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.api_base,
                    timeout=self.config.timeout
                )
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai"
                )
    
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Génère une réponse via OpenAI."""
        self._initialize_client()
        
        # Merger les kwargs avec la config
        params = {
            'model': kwargs.get('model', self.config.model),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'top_p': kwargs.get('top_p', self.config.top_p),
            'frequency_penalty': kwargs.get('frequency_penalty', self.config.frequency_penalty),
            'presence_penalty': kwargs.get('presence_penalty', self.config.presence_penalty),
        }
        
        # Convertir les messages
        messages_dict = [msg.to_dict() for msg in messages]
        
        # Appeler l'API
        response = self._client.chat.completions.create(
            messages=messages_dict,
            **params
        )
        
        # Extraire la réponse
        choice = response.choices[0]
        
        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            metadata={'response_id': response.id}
        )


class AnthropicLLM(BaseLLM):
    """LLM pour Anthropic (Claude)."""
    
    def _initialize_client(self) -> None:
        """Initialise le client Anthropic."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(
                    api_key=self.config.api_key,
                    timeout=self.config.timeout
                )
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
                )
    
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Génère une réponse via Anthropic."""
        self._initialize_client()
        
        # Séparer system prompt et messages
        system_prompt = None
        conversation_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                conversation_messages.append(msg.to_dict())
        
        # Paramètres
        params = {
            'model': kwargs.get('model', self.config.model),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'top_p': kwargs.get('top_p', self.config.top_p),
        }
        
        if system_prompt:
            params['system'] = system_prompt
        
        # Appeler l'API
        response = self._client.messages.create(
            messages=conversation_messages,
            **params
        )
        
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason,
            metadata={'response_id': response.id}
        )


class OllamaLLM(BaseLLM):
    """LLM pour Ollama (modèles open-source locaux)."""
    
    def _initialize_client(self) -> None:
        """Initialise le client Ollama."""
        if self._client is None:
            try:
                from ollama import Client
                base_url = self.config.api_base or "http://localhost:11434"
                self._client = Client(host=base_url)
            except ImportError:
                raise ImportError(
                    "ollama package required. Install with: pip install ollama"
                )
    
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Génère une réponse via Ollama."""
        self._initialize_client()
        
        # Convertir les messages
        messages_dict = [msg.to_dict() for msg in messages]
        
        # Paramètres
        params = {
            'model': kwargs.get('model', self.config.model),
            'messages': messages_dict,
            'options': {
                'temperature': kwargs.get('temperature', self.config.temperature),
                'num_predict': kwargs.get('max_tokens', self.config.max_tokens),
                'top_p': kwargs.get('top_p', self.config.top_p),
            }
        }
        
        # Appeler l'API
        response = self._client.chat(**params)
        
        return LLMResponse(
            content=response['message']['content'],
            model=response.get('model', self.config.model),
            usage={
                'prompt_tokens': response.get('prompt_eval_count', 0),
                'completion_tokens': response.get('eval_count', 0),
                'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
            },
            finish_reason='stop',
            metadata={}
        )


class HuggingFaceLLM(BaseLLM):
    """
    LLM pour HuggingFace.

    - Si `api_key` est fourni  → utilise l'API Inference HuggingFace (serverless,
      aucun téléchargement, modèle hébergé chez HF). Requiert HF_TOKEN.
    - Si `api_key` est absent  → charge le modèle localement via `transformers`
      (télécharge les poids la première fois, nécessite RAM/VRAM suffisante).
    """

    def _initialize_client(self) -> None:
        if self._client is not None:
            return

        if self.config.api_key:
            # Mode API Inference — aucun téléchargement de modèle
            # provider="hf-inference" force l'utilisation de l'infra HF sans auto-routing
            try:
                from huggingface_hub import InferenceClient
                self._client = InferenceClient(
                    provider="hf-inference",
                    token=self.config.api_key,
                )
                self._use_inference_api = True
            except ImportError:
                raise ImportError(
                    "huggingface-hub package required. Install with: uv add huggingface-hub"
                )
        else:
            # Mode local — télécharge et charge le modèle (peut être volumineux)
            try:
                from transformers import pipeline
                self._client = pipeline(
                    "text-generation",
                    model=self.config.model,
                    device_map="auto",
                )
                self._use_inference_api = False
            except ImportError:
                raise ImportError(
                    "transformers package required. Install with: uv add transformers torch"
                )

    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Génère une réponse via l'API Inference HuggingFace ou en local."""
        self._initialize_client()

        max_new_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        temperature = kwargs.get('temperature', self.config.temperature)

        if getattr(self, '_use_inference_api', False):
            # -- API Inference (chat_completion) --
            hf_messages = [{"role": m.role, "content": m.content} for m in messages]
            response = self._client.chat_completion(
                model=self.config.model,
                messages=hf_messages,
                max_tokens=max_new_tokens,
                temperature=temperature,
            )
            generated_text = response.choices[0].message.content or ""
            return LLMResponse(
                content=generated_text,
                model=self.config.model,
                usage={
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0),
                },
                finish_reason=response.choices[0].finish_reason or 'stop',
                metadata={},
            )
        else:
            # -- Inférence locale --
            prompt = self._format_messages_to_prompt(messages)
            outputs = self._client(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', self.config.top_p),
                do_sample=True,
                return_full_text=False,
            )
            generated_text = outputs[0]['generated_text']
            return LLMResponse(
                content=generated_text,
                model=self.config.model,
                usage={
                    'prompt_tokens': len(prompt.split()),
                    'completion_tokens': len(generated_text.split()),
                    'total_tokens': len(prompt.split()) + len(generated_text.split()),
                },
                finish_reason='stop',
                metadata={},
            )

    def _format_messages_to_prompt(self, messages: List[LLMMessage]) -> str:
        """Formate les messages en prompt texte (mode local uniquement)."""
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


class GeminiLLM(BaseLLM):
    """LLM pour Google Gemini API (utilisant google-genai)."""
    
    def _initialize_client(self) -> None:
        """Initialise le client Gemini."""
        if self._client is None:
            try:
                # Utiliser le nouveau package google-genai
                from google import genai
                
                # Charger la clé API depuis l'environnement
                api_key = self.config.api_key
                if api_key and api_key.startswith('$'):
                    # Si c'est une référence d'env var ($VAR_NAME), la résoudre
                    api_key = os.getenv(api_key[1:]) or api_key
                elif not api_key or api_key == 'GOOGLE_API_KEY':
                    # Sinon, chercher dans l'environnement
                    api_key = os.getenv('GOOGLE_API_KEY') or self.config.api_key
                
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in environment or config")
                
                # Créer le client avec la clé API (pas de configure())
                self._client = genai.Client(api_key=api_key)
            except ImportError:
                raise ImportError(
                    "google-genai package required. Install with: pip install google-genai"
                )
    
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Génère une réponse via Gemini."""
        self._initialize_client()
        
        # Préparer les messages au format Gemini
        request_messages = []
        system_prompt = None
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            elif msg.role == "user":
                request_messages.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == "assistant":
                request_messages.append({
                    "role": "model",
                    "parts": [{"text": msg.content}]
                })
        
        # Configuration pour API Gemini
        model_name = kwargs.get('model', self.config.model)
        
        # Formater le nom du modèle correctement pour google-genai
        # Si le modèle ne commence pas par "models/", l'ajouter
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        
        # Appeler l'API avec le nouveau client
        try:
            from google.genai.types import GenerateContentConfig
            
            
            # Créer la configuration avec les paramètres corrects
            config_dict = {
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_output_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "top_p": kwargs.get('top_p', self.config.top_p),
                "top_k": kwargs.get('top_k', self.config.top_k),
            }
            
            # Ajouter system_instruction si fourni
            if system_prompt:
                config_dict["system_instruction"] = system_prompt
            
            config = GenerateContentConfig(**config_dict)
            
            # Appeler l'API generate_content
            response = self._client.models.generate_content(
                model=model_name,
                contents=request_messages,
                config=config
            )
            
            return LLMResponse(
                content=response.text if hasattr(response, 'text') else str(response),
                model=kwargs.get('model', self.config.model),
                usage={
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0
                },
                finish_reason="STOP",
                metadata={}
            )
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'appel Gemini API: {str(e)}")


class MistralLLM(BaseLLM):
    """LLM pour Mistral AI."""
    
    def _initialize_client(self) -> None:
        """Initialise le client Mistral."""
        if self._client is None:
            try:
                from mistralai import Mistral
                self._client = Mistral(api_key=self.config.api_key)
            except ImportError:
                raise ImportError(
                    "mistralai package required. Install with: pip install mistralai"
                )
    
    def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Génère une réponse via Mistral AI."""
        self._initialize_client()
        
        # Préparation des paramètres
        params = {
            'model': kwargs.get('model', self.config.model),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'top_p': kwargs.get('top_p', self.config.top_p),
        }
        
        # Conversion des messages au format attendu par Mistral
        messages_dict = [msg.to_dict() for msg in messages]
        
        # Appel API
        response = self._client.chat.complete(
            messages=messages_dict,
            **params
        )
        
        choice = response.choices[0]
        
        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            metadata={'response_id': response.id}
        )

def create_llm(
    provider: Union[str, LLMProvider],
    model: str,
    **kwargs
) -> BaseLLM:
    """
    Factory pour créer un LLM.
    
    Args:
        provider: Provider du LLM
        model: Nom du modèle
        **kwargs: Configuration additionnelle
        
    Returns:
        Instance de LLM
    """
    if isinstance(provider, str):
        provider = LLMProvider(provider)
    
    config = LLMConfig(provider=provider, model=model, **kwargs)
    
    if provider == LLMProvider.OPENAI:
        return OpenAILLM(config)
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicLLM(config)
    elif provider == LLMProvider.OLLAMA:
        return OllamaLLM(config)
    elif provider == LLMProvider.HUGGINGFACE:
        return HuggingFaceLLM(config)
    elif provider == LLMProvider.MISTRAL:
        return MistralLLM(config)
    elif provider == LLMProvider.GEMINI:
        return GeminiLLM(config)
    else:
        raise ValueError(f"Unknown provider: {provider}")