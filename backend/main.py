import time
import os
from pathlib import Path
from src.core import RAGPipelineFactory
from src.Loaders.text_loader import UnifiedDocumentLoader
from src.Chunkers.basic_chunker import ConfigurableChunker
from src.implementations import register_all_components

# 🔒 Configuration du cache HuggingFace pour éviter les re-téléchargements
cache_dir = Path.home() / ".cache" / "huggingface"
os.environ["HF_HOME"] = str(cache_dir)
os.environ["TRANSFORMERS_CACHE"] = str(cache_dir / "transformers")
print(f"📁 Modèles sauvegardés dans : {cache_dir}")

# 1. Enregistrer les composants
register_all_components()

# 2. Charger la configuration
config = RAGPipelineFactory.load_config('configs/hybrid.yaml')  # Avec Ollama LLM

# 3. Créer le pipeline
pipeline = RAGPipelineFactory.create_from_config(config)

pipeline.ingest(
    loader=UnifiedDocumentLoader(),
    chunker=ConfigurableChunker(),
    source="./data/documents/attentionn_is_all_you_need.pdf"
)

# 4. Utiliser
response = pipeline.query("What is multi head attention ?")
print(response)
