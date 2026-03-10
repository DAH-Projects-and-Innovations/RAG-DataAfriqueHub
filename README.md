# RAG-DataAfriqueHub

Moteur RAG (Retrieval-Augmented Generation) modulaire et configurable. Le projet fournit un backend FastAPI et une interface React pour interroger des documents en langage naturel. Trois modes de déploiement sont disponibles : gratuit (100 % local), hybride (embedding local + LLM cloud) et premium (tout cloud, haute performance).

---

## Table des matières

1. [Architecture](#architecture)
2. [Prérequis](#prérequis)
3. [Installation locale (développement)](#installation-locale-développement)
4. [Lancement avec Docker](#lancement-avec-docker)
   - [Mode free](#mode-free)
   - [Mode hybrid](#mode-hybrid)
   - [Mode premium](#mode-premium)
5. [Comparaison des modes](#comparaison-des-modes)
6. [Structure du projet](#structure-du-projet)
7. [API REST](#api-rest)
8. [Configuration YAML](#configuration-yaml)
9. [Ajouter un composant personnalisé](#ajouter-un-composant-personnalisé)
10. [Tests](#tests)
11. [Variables d'environnement](#variables-denvironnement)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│   Upload PDF/TXT/MD  ──►  POST /ingest                      │
│   Poser une question ──►  POST /query  ◄── chat_history      │
│   Modèles disponibles ─►  GET  /models                       │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP
┌────────────────────────────▼────────────────────────────────┐
│                       Backend (FastAPI)                      │
│                                                              │
│   POST /ingest                                               │
│     └─ UnifiedDocumentLoader ──► Chunker ──► Embedder        │
│                                          └──► VectorStore    │
│                                                              │
│   POST /query                                                │
│     └─ Embedder(query) ──► VectorStore.search()             │
│               └──► [Reranker] ──► LLM.generate_with_context()│
│                                           └──► RAGResponse   │
└─────────────────────────────────────────────────────────────┘
```

### Composants abstraits (8 interfaces)

| Interface | Rôle |
|-----------|------|
| `IDocumentLoader` | Charge des fichiers (PDF, TXT, MD) |
| `IChunker` | Découpe les documents en chunks |
| `IEmbedder` | Génère des vecteurs d'embedding |
| `IVectorStore` | Stocke et recherche les vecteurs |
| `IRetriever` | Interroge le vector store |
| `IReranker` | Trie les résultats par pertinence |
| `IQueryRewriter` | Reformule la requête utilisateur |
| `ILLM` | Génère la réponse finale |

Chaque interface est interchangeable via configuration YAML, sans modifier le code du pipeline.

---

## Prérequis

| Outil | Version minimale |
|-------|-----------------|
| Python | 3.12 |
| [uv](https://docs.astral.sh/uv/) | 0.4+ |
| Node.js | 20+ |
| Docker + Docker Compose | 24+ / 2.20+ |

---

## Installation locale (développement)

### 1. Cloner le dépôt

```bash
git clone https://github.com/abel2319/RAG-DataAfriqueHub.git
cd RAG-DataAfriqueHub
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos clés API selon le mode choisi
```

### 3. Lancer le backend

```bash
cd backend
uv sync          # installe les dépendances
uv run uvicorn src.api.main:app --reload --port 8000
```

L'API est disponible sur `http://localhost:8000`.
La documentation interactive Swagger est sur `http://localhost:8000/docs`.

### 4. Lancer le frontend

```bash
cd frontend/rag-afrique-hub
npm install
npm run dev      # démarre sur http://localhost:5173
```

> **Note :** Le frontend lit `VITE_API_URL` (par défaut `http://localhost:8000`). Pour changer la cible backend, modifiez `.env` avant `npm run dev`.

---

## Lancement avec Docker

Docker Compose orchestre les deux services. Le frontend est servi par Nginx sur le port `5173` et le backend sur le port `8000`.

```bash
# Copier et remplir le .env
cp .env.example .env
```

### Mode free

**Coût :** 0 € — embedding local (SentenceTransformers), vector DB locale (ChromaDB), LLM HuggingFace Inference API.

**Clés requises :** `HF_TOKEN`

```bash
# .env
RAG_CONFIG=free
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# Lancer
docker compose up --build
```

> Le premier démarrage télécharge le modèle d'embedding (~500 MB). Les démarrages suivants sont rapides grâce au volume `rag_data`.

### Mode hybrid

**Coût :** ~5-30 $/mois — embedding local, vector DB locale (ChromaDB), LLM Gemini (Google AI), reranking Cohere.

**Clés requises :** `GOOGLE_API_KEY`, `COHERE_API_KEY`

```bash
# .env
RAG_CONFIG=hybrid
GOOGLE_API_KEY=AIza...
COHERE_API_KEY=...

# Lancer
docker compose up --build
```

Obtenez une clé Gemini gratuite sur [ai.google.dev](https://ai.google.dev) et une clé Cohere sur [cohere.com](https://cohere.com).

### Mode premium

**Coût :** ~50-500 $/mois — embedding OpenAI (`text-embedding-3-large`), vector DB Pinecone (managée), LLM GPT-4o, reranking Cohere.

**Clés requises :** `OPENAI_API_KEY`, `COHERE_API_KEY`, `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`

```bash
# .env
RAG_CONFIG=premium
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1-aws

# Lancer
docker compose up --build
```

> Pinecone : créez un compte sur [pinecone.io](https://www.pinecone.io). L'index `rag-documents` est créé automatiquement au premier démarrage si `create_index_if_missing: true` est activé dans `premium.yaml`.

### Commandes utiles

```bash
# Voir les logs en temps réel
docker compose logs -f

# Arrêter sans supprimer les volumes (données conservées)
docker compose stop

# Arrêter et supprimer les données
docker compose down -v

# Rebuild uniquement le backend
docker compose up --build backend-rag
```

---

## Comparaison des modes

| Critère | free | hybrid | premium |
|---------|------|--------|---------|
| **Coût mensuel** | 0 € | 5–30 $ | 50–500 $ |
| **Embedding** | SentenceTransformers (local) | SentenceTransformers (local) | OpenAI `text-embedding-3-large` |
| **Vector DB** | ChromaDB (locale) | ChromaDB (locale) | Pinecone (cloud) |
| **LLM** | HuggingFace Zephyr 7B | Gemini 2.0 Flash | GPT-4o |
| **Reranker** | Cross-Encoder (local) | Cohere (cloud) | Cohere (cloud) |
| **Qualité réponse** | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| **Vitesse** | lente (CPU) | rapide | très rapide |
| **Scalabilité** | non | limitée | élevée |
| **GPU requis** | non | non | non |
| **Idéal pour** | dev/tests | production légère | production intensive |

---

## Structure du projet

```
RAG-DataAfriqueHub/
├── .env.example                    # Template des variables d'environnement
├── docker-compose.yml              # Orchestration Docker
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml              # Dépendances Python (uv)
│   ├── configs/
│   │   ├── free.yaml               # Config mode free
│   │   ├── hybrid.yaml             # Config mode hybrid
│   │   └── premium.yaml            # Config mode premium
│   └── src/
│       ├── api/
│       │   ├── main.py             # Application FastAPI, auth globale
│       │   ├── dependencies.py     # get_pipeline() (lru_cache), verify_api_key()
│       │   └── routes/
│       │       ├── query.py        # POST /query
│       │       ├── ingest.py       # POST /ingest, DELETE /ingest/{filename}
│       │       ├── health.py       # GET /health
│       │       └── models.py       # GET /models
│       ├── core/
│       │   ├── interfaces.py       # 8 interfaces abstraites
│       │   ├── models.py           # Document, Chunk, Query, RAGResponse
│       │   ├── orchestrator.py     # RAGPipeline (logique du pipeline)
│       │   ├── factory.py          # RAGPipelineFactory (chargement YAML + injection)
│       │   └── config_schema.py    # Validation Pydantic des YAML au démarrage
│       ├── implementations/
│       │   └── __init__.py         # Enregistrement de tous les composants
│       ├── Embedders/
│       │   ├── dummy_embedder.py   # LocalSentenceEmbedder (SentenceTransformers)
│       │   └── openai_embedder.py  # OpenAIEmbedder (text-embedding-3-large)
│       ├── vectorstores/
│       │   ├── chroma_store.py     # ChromaVectorStore
│       │   ├── simple_store.py     # FAISSVectorStore (in-memory)
│       │   └── pinecone_store.py   # PineconeVectorStore
│       ├── Loaders/
│       │   └── text_loader.py      # UnifiedDocumentLoader (PDF, TXT, MD)
│       ├── Chunkers/
│       │   ├── basic_chunker.py    # ConfigurableChunker (sliding window)
│       │   └── semantic_chunker.py # SemanticChunker (cosine breakpoints)
│       ├── retrieval/
│       │   ├── retrieval_strategy.py  # RetrievalStrategy (dense retriever)
│       │   ├── reranker.py            # CohereReranker, CrossEncoderReranker, NoOpReranker
│       │   └── dense_retriever.py
│       ├── llm/
│       │   ├── base_llm.py         # Implémentations LLM (Mistral, HF, OpenAI, Gemini, Ollama)
│       │   ├── llm_adapter.py      # LLMAdapter (ILLM → génération RAG)
│       │   ├── llm_factory.py      # LLMAdapterFactory
│       │   └── prompt_manager.py   # Gestionnaire de templates de prompts
│       └── tests/
│           ├── test_integration_api.py       # 17 tests API (routes, auth, erreurs)
│           ├── test_integration_pipeline.py  # 13 tests pipeline (ingest, query, delete)
│           └── test_config_validation.py     # 29 tests config + composants
│
└── frontend/
    └── rag-afrique-hub/
        ├── Dockerfile
        ├── package.json
        └── src/
            ├── App.jsx             # Interface principale (chat + upload)
            └── services/
                └── api.js          # Client HTTP (query, ingest, models)
```

---

## API REST

L'API complète est documentée sur `http://localhost:8000/docs` (Swagger UI).

### `POST /query`

Pose une question au pipeline RAG.

**Corps de la requête :**
```json
{
  "question": "Quels sont les indicateurs économiques du Sénégal en 2023 ?",
  "chat_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "top_k": 10,
  "rerank_top_k": 5,
  "llm_params": {
    "model": "gemini-2.0-flash",
    "temperature": 0.7
  }
}
```

**Réponse :**
```json
{
  "answer": "Selon les documents, le PIB du Sénégal...",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "filename": "rapport_2023.pdf",
        "source": "/app/data/rapport_2023.pdf",
        "page": 12
      },
      "score": 0.87
    }
  ],
  "metadata": {
    "model": "gemini-2.0-flash",
    "duration_ms": 1240
  }
}
```

---

### `POST /ingest`

Indexe un ou plusieurs fichiers dans le vector store.

**Form-data :**
- `files` : un ou plusieurs fichiers (PDF, TXT, MD)

**Réponse :**
```json
{
  "status": "success",
  "processed": 2,
  "details": [
    {"filename": "rapport.pdf", "chunks": 47},
    {"filename": "notes.md", "chunks": 12}
  ]
}
```

---

### `DELETE /ingest/{filename}`

Supprime tous les chunks d'un document du vector store.

**Exemple :** `DELETE /ingest/rapport.pdf`

**Réponse :** `204 No Content`

---

### `GET /health`

Vérifie l'état du backend et du pipeline.

**Réponse :**
```json
{
  "status": "up",
  "config": "hybrid",
  "stats": {
    "total_vectors": 523
  }
}
```

---

### `GET /models`

Retourne la liste des modèles LLM disponibles pour le mode actif.

**Réponse :**
```json
[
  {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash (Google)", "provider": "gemini", "default": true},
  {"id": "gemini-1.5-pro",   "label": "Gemini 1.5 Pro (Google)",   "provider": "gemini", "default": false}
]
```

---

### Authentification (optionnelle)

Si `API_KEY` est définie dans `.env`, toutes les routes requièrent le header :

```
X-API-Key: <votre_clé>
```

Sans ce header (ou avec une clé incorrecte), l'API retourne `401 Unauthorized`.

Pour désactiver l'auth, laisser `API_KEY=` vide dans `.env`.

---

## Configuration YAML

Chaque mode est décrit par un fichier YAML dans `backend/configs/`. Le mode actif est sélectionné via la variable d'environnement `RAG_CONFIG` (`free`, `hybrid`, ou `premium`).

La configuration est validée au démarrage via Pydantic — toute erreur de clé ou de type produit un message d'erreur clair avant de lancer le serveur.

### Structure générale

```yaml
embedder:
  name: "sentence_transformers"   # Nom du composant enregistré
  params:
    model_name: "BAAI/bge-large-en-v1.5"

vector_store:
  name: "chroma"
  params:
    collection_name: "documents"
    persist_directory: "./data/chroma_db"

retriever:
  name: "vector_retriever"
  params:
    top_k: 20

reranker:                         # Optionnel
  name: "cohere"
  params:
    api_key: "${COHERE_API_KEY}"  # Substitution automatique de l'env var
    top_n: 5

prompt_managers:
  name: "default"
  params: {}

llm:
  name: "gemini"
  params:
    api_key: "${GOOGLE_API_KEY}"
    model: "gemini-2.0-flash"

models:                           # Liste exposée via GET /models
  - id: "gemini-2.0-flash"
    label: "Gemini 2.0 Flash"
    provider: "gemini"
    default: true

pipeline_config:
  name: "my_pipeline"
  default_top_k: 10
  default_rerank_top_k: 5
  enable_caching: true
  log_level: "INFO"
```

> Les valeurs `"${VAR_NAME}"` sont automatiquement remplacées par la valeur de la variable d'environnement correspondante au chargement du fichier.

---

## Ajouter un composant personnalisé

**Exemple : ajouter un embedder Cohere**

### 1. Implémenter l'interface

```python
# backend/src/Embedders/cohere_embedder.py
import logging
from typing import List
import cohere
from src.core.interfaces import IEmbedder

logger = logging.getLogger(__name__)

class CohereEmbedder(IEmbedder):
    def __init__(self, api_key: str, model: str = "embed-multilingual-v3.0", **kwargs):
        self.client = cohere.Client(api_key)
        self.model = model

    def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        response = self.client.embed(texts=texts, model=self.model, input_type="search_document")
        return response.embeddings

    def embed_query(self, query: str, **kwargs) -> List[float]:
        response = self.client.embed(texts=[query], model=self.model, input_type="search_query")
        return response.embeddings[0]

    def get_dimension(self) -> int:
        return 1024  # embed-multilingual-v3.0
```

### 2. Enregistrer le composant

```python
# backend/src/implementations/__init__.py
from src.Embedders.cohere_embedder import CohereEmbedder

def register_all_components():
    # ...
    f.register_component("embedders", "cohere", CohereEmbedder)
```

### 3. Utiliser dans un YAML

```yaml
embedder:
  name: "cohere"
  params:
    api_key: "${COHERE_API_KEY}"
    model: "embed-multilingual-v3.0"
```

C'est tout — aucune modification du pipeline ou de l'API n'est nécessaire.

---

## Tests

Les tests d'intégration se trouvent dans `backend/src/tests/`.

```bash
cd backend

# Lancer tous les tests
uv run pytest src/tests/ -v

# Lancer avec rapport de couverture
uv run pytest src/tests/ --cov=src --cov-report=term-missing

# Lancer uniquement les tests API
uv run pytest src/tests/test_integration_api.py -v

# Lancer uniquement les tests pipeline
uv run pytest src/tests/test_integration_pipeline.py -v
```

| Fichier | Tests | Couverture |
|---------|-------|-----------|
| `test_integration_api.py` | 17 | Routes `/health`, `/models`, `/query`, `/ingest` (succès, erreurs, auth) |
| `test_integration_pipeline.py` | 13 | Ingest, query, deduplication, reranker, delete |
| `test_config_validation.py` | 29 | Validation Pydantic, substitution env vars, ChromaVectorStore, SemanticChunker |

Les tests utilisent `dependency_overrides` pour mocker le pipeline FastAPI — aucune clé API réelle n'est nécessaire pour les exécuter.

---

## Variables d'environnement

Toutes les variables sont documentées dans [`.env.example`](.env.example).

| Variable | Mode | Requis | Description |
|----------|------|--------|-------------|
| `RAG_CONFIG` | tous | oui | Mode actif : `free`, `hybrid`, `premium` |
| `HF_TOKEN` | free | oui | Token HuggingFace Inference API |
| `GOOGLE_API_KEY` | hybrid | oui | Clé Google AI Studio (Gemini) |
| `COHERE_API_KEY` | hybrid, premium | oui | Clé Cohere (reranking) |
| `OPENAI_API_KEY` | premium | oui | Clé OpenAI (embedding + LLM) |
| `PINECONE_API_KEY` | premium | oui | Clé Pinecone |
| `PINECONE_ENVIRONMENT` | premium | oui | Région Pinecone (ex: `us-east-1-aws`) |
| `API_KEY` | tous | non | Clé d'auth pour l'API (header `X-API-Key`) |
| `VITE_API_URL` | frontend | non | URL du backend vue par le navigateur (défaut: `http://localhost:8000`) |
