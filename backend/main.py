import time
from src.core import RAGPipelineFactory
from src.Loaders.text_loader import UnifiedDocumentLoader
from src.Chunkers.basic_chunker import ConfigurableChunker
from src.implementations import register_all_components

# 1. Enregistrer les composants
register_all_components()

# 2. Charger la configuration
config = RAGPipelineFactory.load_config('configs/free.yaml')

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
