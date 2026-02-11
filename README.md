#  Architecture RAG Modulaire - Tâche 1
> Architecture RAG modulaire et configurable avec interfaces abstraites, orchestrateur de pipeline et configurations fonctionnelles.

##  Objectif
Concevoir et implémenter l'architecture globale du RAG sous forme de pipeline modulaire, extensible et configurable sans modification du code.

##  Livrables

✅ **Schéma d'architecture** - Diagrammes et flux  
✅ **Interfaces et orchestrateur** - 8 interfaces + RAGPipeline + Factory  
✅ **Configurations fonctionnelles** - 3 configs YAML prêtes à l'emploi

##  Architecture

```
Configuration (YAML/JSON)
         ↓
  RAGPipelineFactory (registre de composants)
         ↓
    RAGPipeline (orchestrateur)
         ↓
    [Ingestion Pipeline]  [Query Pipeline]
```

### Interfaces Abstraites (8)

| Interface | Rôle |
|-----------|------|
| `IDocumentLoader` | Charge les documents |
| `IChunker` | Découpe en chunks |
| `IEmbedder` | Génère les embeddings |
| `IVectorStore` | Stocke et recherche les vecteurs |
| `IRetriever` | Récupère les documents |
| `IReranker` | Réordonne par pertinence |
| `IQueryRewriter` | Améliore les requêtes |
| `ILLM` | Génère les réponses |

##  Structure

```
src/core/
├── models.py          # Document, Chunk, Query, RAGResponse
├── interfaces.py      # 8 interfaces abstraites
├── orchestrator.py    # RAGPipeline
├── factory.py         # RAGPipelineFactory
└── __init__.py

configs/
├── base.yaml          # Configuration de base
├── free.yaml          # Config gratuite (0€/mois)
├── hybrid.yaml        # Config hybride (25-60€/mois)
└── premium.yaml       # Config premium (100-500€/mois)
 ├── implementations/
│   │   ├── __init__.py
│   │   ├── embedders/
│   │   │   ├── __init__.py
│   │   │   ├── sentence_transformers.py
│   │   │   ├── openai_embedder.py
│   │   │   └── cohere_embedder.py
│   │   │
│   │   ├── vector_stores/
│   │   │   ├── __init__.py
│   │   │   ├── chroma_store.py
│   │   │   ├── qdrant_store.py
│   │   │   └── pinecone_store.py
│   │   │
│   │   ├── retrievers/
│   │   │   ├── __init__.py
│   │   │   ├── vector_retriever.py
│   │   │   └── hybrid_retriever.py
│   │   │
│   │   ├── rerankers/
│   │   │   ├── __init__.py
│   │   │   ├── cross_encoder.py
│   │   │   └── cohere_reranker.py
│   │   │
│   │   ├── query_rewriters/
│   │   │   ├── __init__.py
│   │   │   └── llm_rewriter.py
│   │   │
│   │   ├── llms/
│   │   │   ├── __init__.py
│   │   │   ├── openai_llm.py
│   │   │   ├── anthropic_llm.py
│   │   │   └── ollama_llm.py
│   │   │
│   │   ├── loaders/
│   │   │   ├── __init__.py
│   │   │   ├── text_loader.py
│   │   │   ├── pdf_loader.py
│   │   │   └── web_loader.py
│   │   │
│   │   └── chunkers/
│   │       ├── __init__.py
│   │       ├── recursive_chunker.py
│   │       └── semantic_chunker.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── query.py
│   │   │   ├── ingest.py
│   │   │   └── health.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── request.py
│   │   │   └── response.py
│   │   └── dependencies.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── config_loader.py
│       └── metrics.py
│
├── frontend/                       # Interface web
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   └── DocumentUpload.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   └── public/
│
├── tests/
│   ├── __init__.py
│   ├── test_interfaces.py
│   ├── test_pipeline.py
│   └── test_api.py
│
├── data/                           # Données persistantes
│   ├── chroma_db/
│   └── documents/
│
└── scripts/
    ├── setup.sh
    ├── run_dev.sh
    └── run_prod.sh
"""

# ==========================================
# requirements.txt
# ==========================================

REQUIREMENTS = """
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# RAG Core
langchain==0.1.0
langchain-community==0.0.13

# Embeddings
sentence-transformers==2.3.1
openai==1.10.0
cohere==4.40

# Vector Stores
chromadb==0.4.22
qdrant-client==1.7.0
pinecone-client==3.0.0
faiss-cpu==1.7.4  # ou faiss-gpu

# Document Processing
pypdf==3.17.4
python-docx==1.1.0
beautifulsoup4==4.12.3

# Utilities
pyyaml==6.0.1
numpy==1.26.3
pandas==2.1.4
tenacity==8.2.3

# Monitoring & Logging
loguru==0.7.2
prometheus-client==0.19.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0

# Optional: Development
black==24.1.1
flake8==7.0.0
mypy==1.8.0
"""
```

##  Utilisation

```python
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
```

##  Configurations

| Config | Coût | Performance | Composants |
|--------|------|-------------|------------|
| **Free** | 0€/mois | 7-8/10 | SentenceTransformers + ChromaDB + Ollama |
| **Hybrid** | 25-60€/mois | 8.5-9/10 | SentenceTransformers + ChromaDB + Cohere + GPT-4o-mini |
| **Premium** | 100-500€/mois | 9.5/10 | OpenAI Embeddings + Pinecone + Cohere + GPT-4 |

## Extensibilité

**3 étapes pour ajouter un composant :**

```python
# 1. Créer la classe
class MyComponent(IInterface):
    def method(self): pass

# 2. Enregistrer
RAGPipelineFactory.register_component('type', 'name', MyComponent)

# 3. Utiliser en config
component:
  name: "name"
  params: {...}
```

##  Points clés

- ✅ **Backend agnostique** : Support de 10+ providers
- ✅ **Configuration YAML** : Zéro modification de code
- ✅ **Interchangeabilité** : Tous les composants sont remplaçables
- ✅ **Extensibilité** : Registre dynamique de composants
- ✅ **Documentation** : Interfaces et méthodes documentées


##  Prochaines étapes

- **Tâche 2** : Implémentations concrètes des interfaces
- **Tâche 3** : API FastAPI et endpoints
- **Tâche 4** : Tests et validation
- **Tâche 5** : Déploiement et monitoring

