"""
Route GET /models — retourne la liste des modèles LLM disponibles
tels que déclarés dans la section `models` du fichier de configuration YAML actif.
"""

from fastapi import APIRouter, Depends
from typing import List
from src.api.dependencies import get_pipeline

router = APIRouter(prefix="/models", tags=["Modèles"])


@router.get("")
def list_models(pipeline=Depends(get_pipeline)) -> List[dict]:
    """
    Retourne les modèles disponibles définis dans pipeline_config.models.

    Réponse :
        [
          {"id": "mistral-small-latest", "label": "Mistral Small", "provider": "mistral", "default": true},
          ...
        ]
    """
    models = pipeline.config.get("models", [])
    # Garantit le format même si la config ne définit pas tous les champs
    return [
        {
            "id": m.get("id", ""),
            "label": m.get("label", m.get("id", "")),
            "provider": m.get("provider", ""),
            "default": m.get("default", False),
        }
        for m in models
    ]
