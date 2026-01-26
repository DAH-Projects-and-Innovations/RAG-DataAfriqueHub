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

