import os
import functools
from dotenv import load_dotenv
from fastapi import HTTPException, Header
from src.core.factory import RAGPipelineFactory
from src.implementations import register_all_components

# Charger le .env le plus tôt possible, avant toute lecture d'os.getenv()
load_dotenv()


def verify_api_key(x_api_key: str = Header(default=None)) -> None:
    """
    Vérifie la clé API si la variable d'environnement API_KEY est définie.
    Si API_KEY n'est pas définie, l'authentification est désactivée (mode local).

    Header requis quand API_KEY est défini :
        X-API-Key: <votre_clé>
    """
    expected = os.getenv("API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(
            status_code=401,
            detail="Clé API manquante ou invalide. Fournissez le header X-API-Key."
        )


@functools.lru_cache()
def get_pipeline():
    register_all_components()

    # Choisir la configuration via la variable d'environnement RAG_CONFIG.
    # Valeurs acceptées : "free" | "hybrid"
    config_name = os.getenv("RAG_CONFIG", "hybrid").strip().lower()
    config_path = f"configs/{config_name}.yaml"

    config = RAGPipelineFactory.load_config(config_path)
    return RAGPipelineFactory.create_from_config(config)
