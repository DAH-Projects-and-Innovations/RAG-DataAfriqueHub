from src.core import RAGPipelineFactory
from src.implementations import register_all_components

# 1. Enregistrer les composants
register_all_components()

# 2. Charger la configuration
config = RAGPipelineFactory.load_config('configs/free.yaml')

# 3. Créer le pipeline
pipeline = RAGPipelineFactory.create_from_config(config)

# 4. Utiliser
response = pipeline.query("Votre question?")
print(response)
