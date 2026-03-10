# Module de Retrieval Avancé - Documentation

## 📋 Vue d'ensemble

Système de retrieval robuste et générique supportant :
- ✅ **Dense retrieval** basé embeddings (recherche sémantique)
- ✅ **BM25 retrieval** lexical (recherche par mots-clés)
- ✅ **Hybrid retrieval** combinant les deux approches
- ✅ **Reranking** via cross-encoder ou Cohere
- ✅ **Filtrage par métadonnées** avec opérateurs avancés
- ✅ **Configuration dynamique** sans modification de code

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  RetrievalStrategy                      │
│  (Orchestrateur configurable dynamiquement)             │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Dense     │  │     BM25     │  │   Hybrid     │
│  Retriever   │  │  Retriever   │  │  Retriever   │
└──────────────┘  └──────────────┘  └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Reranker   │
                  │ (optionnel)  │
                  └──────────────┘
```

---

## 📦 Structure des fichiers

```
src/retrieval/
├── __init__.py                 # Exports publics
├── dense_retriever.py          # Dense retrieval (embeddings)
├── bm25_retriever.py           # BM25 retrieval (lexical)
├── hybrid_retriever.py         # Fusion dense + BM25
├── reranker.py                 # Cross-encoder, Cohere, NoOp
└── retrieval_strategy.py       # Orchestrateur configurable

configs/retrieval/
├── dense_simple.yaml           # Config dense basique
├── bm25_pure.yaml             # Config BM25 pure
├── hybrid_rerank.yaml         # Config hybride + reranking
└── premium_cohere.yaml        # Config premium avec Cohere

tests/
└── test_retrieval_comparison.py  # Tests comparatifs

examples/
└── retrieval_examples.py       # Exemples d'utilisation
```

---

## 🚀 Quick Start

### 1. Dense Retrieval (Simple)

```python
from src.retrieval import create_retriever, RetrievalConfig, RetrievalMode
from src.core.models import Query

# Créer une stratégie dense
strategy = create_retriever(
    mode="dense",
    vector_store=my_vector_store,
    embedder=my_embedder,
    documents=documents
)

# Exécuter une requête
query = Query(text="What is machine learning?")
results = strategy.retrieve(query, top_k=5)

# Afficher les résultats
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.content[:100]}... (score: {doc.metadata['score']:.3f})")
```

### 2. Hybrid Retrieval + Reranking

```python
from src.retrieval import RetrievalStrategy, RetrievalConfig, RetrievalMode

# Configuration hybride avancée
config = RetrievalConfig(
    mode=RetrievalMode.HYBRID,
    hybrid_dense_weight=0.6,
    hybrid_bm25_weight=0.4,
    hybrid_fusion_strategy="rrf",  # Reciprocal Rank Fusion
    enable_reranking=True,
    reranker_type="cross-encoder",
    reranker_top_k=10
)

# Créer la stratégie
strategy = RetrievalStrategy(
    vector_store=my_vector_store,
    embedder=my_embedder,
    documents=documents,
    config=config
)

# Récupérer avec reranking
results = strategy.retrieve(query)
```

### 3. Charger depuis YAML

```python
import yaml
from src.retrieval import RetrievalConfig, create_retriever

# Charger la config
with open('configs/retrieval/hybrid_rerank.yaml') as f:
    config_dict = yaml.safe_load(f)

config = RetrievalConfig.from_dict(config_dict)

# Créer la stratégie
strategy = create_retriever(
    mode=config.mode.value,
    vector_store=my_vector_store,
    embedder=my_embedder,
    documents=documents,
    config=config_dict
)
```

---

## 🎯 Configurations prêtes à l'emploi

### Dense Simple (`dense_simple.yaml`)
- **Usage**: Recherche sémantique basique
- **Performance**: ⚡⚡⚡ Très rapide
- **Qualité**: ⭐⭐⭐ Bonne
- **Coût**: 💰 Faible (embeddings uniquement)

```yaml
mode: "dense"
dense:
  top_k: 10
  similarity_threshold: 0.7
  normalize_scores: true
reranking:
  enabled: false
```

### BM25 Pure (`bm25_pure.yaml`)
- **Usage**: Recherche par mots-clés exacts
- **Performance**: ⚡⚡⚡ Très rapide
- **Qualité**: ⭐⭐⭐ Excellente pour termes techniques
- **Coût**: 💰 Gratuit (pas d'embeddings)

```yaml
mode: "bm25"
bm25:
  k1: 1.2
  b: 0.75
  top_k: 10
  min_score: 1.0
```

### Hybrid + Rerank (`hybrid_rerank.yaml`)
- **Usage**: Recherche de précision, QA
- **Performance**: ⚡⚡ Moyen
- **Qualité**: ⭐⭐⭐⭐⭐ Excellente
- **Coût**: 💰💰 Moyen

```yaml
mode: "hybrid"
hybrid:
  dense_weight: 0.5
  bm25_weight: 0.5
  fusion_strategy: "rrf"
  top_k_per_retriever: 20
reranking:
  enabled: true
  type: "cross-encoder"
  model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
  top_k: 10
```

### Premium Cohere (`premium_cohere.yaml`)
- **Usage**: Production, applications critiques
- **Performance**: ⚡⚡ Moyen
- **Qualité**: ⭐⭐⭐⭐⭐ Meilleure disponible
- **Coût**: 💰💰💰 Élevé (~$1-2/1000 requêtes)

```yaml
mode: "hybrid"
hybrid:
  dense_weight: 0.6
  bm25_weight: 0.4
  top_k_per_retriever: 50
reranking:
  enabled: true
  type: "cohere"
  model: "rerank-multilingual-v3.0"
  top_k: 10
```

---

## ⚙️ Configuration dynamique

### Changer de stratégie à la volée

```python
# Commencer avec dense
strategy = create_retriever(mode="dense", ...)
results = strategy.retrieve(query)

# Passer à hybrid
new_config = RetrievalConfig(
    mode=RetrievalMode.HYBRID,
    hybrid_fusion_strategy="rrf"
)
strategy.update_config(new_config)
results = strategy.retrieve(query)

# Activer le reranking
new_config.enable_reranking = True
new_config.reranker_type = "cross-encoder"
strategy.update_config(new_config)
results = strategy.retrieve(query)
```

---

## 🔍 Filtrage par métadonnées

### Filtres simples

```python
# Configuration avec filtres
config = RetrievalConfig(
    mode=RetrievalMode.DENSE,
    metadata_filters={
        "language": "python",
        "level": "beginner"
    }
)

# Ou à la requête
results = strategy.retrieve(
    query,
    filters={"language": "python"}
)
```

### Filtres avancés (opérateurs)

```python
# Opérateurs supportés: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin
filters = {
    "year": {"$gte": 2023},              # Année >= 2023
    "language": {"$in": ["python", "js"]}, # Python OU JavaScript
    "deprecated": {"$ne": True}          # Pas deprecated
}

results = strategy.retrieve(query, filters=filters)
```

---

## 📊 Évaluation et comparaison

### Utiliser le comparateur

```python
from tests.test_retrieval_comparison import RetrievalComparator

# Préparer les données
queries = [Query(id="q1", text="..."), ...]
ground_truth = {"q1": ["doc1", "doc3"], ...}
strategies = {
    "Dense": dense_strategy,
    "Hybrid": hybrid_strategy,
    "Hybrid+Rerank": rerank_strategy
}

# Exécuter la comparaison
comparator = RetrievalComparator(queries, ground_truth, strategies)
results = comparator.run_comparison()

# Afficher le tableau comparatif
comparator.print_comparison_table(results)
```

### Métriques calculées

- **Latency**: Temps de réponse moyen (ms)
- **Precision@k**: Proportion de docs pertinents dans top-k
- **Recall@k**: Proportion de docs pertinents retrouvés
- **MRR**: Mean Reciprocal Rank
- **NDCG@k**: Normalized Discounted Cumulative Gain

---

## 🎨 Stratégies de fusion (Hybrid)

### Weighted Sum
```yaml
fusion_strategy: "weighted_sum"
dense_weight: 0.5
bm25_weight: 0.5
```
- Somme pondérée des scores normalisés
- Simple et rapide
- Sensible aux échelles de scores

### Reciprocal Rank Fusion (RRF)
```yaml
fusion_strategy: "rrf"
rrf_k: 60
```
- Robuste aux différences d'échelles
- Basé sur les rangs, pas les scores
- **Recommandé pour hybrid**

### Max Fusion
```yaml
fusion_strategy: "max"
```
- Prend le maximum des scores normalisés
- Favorise les documents excellents sur une dimension

---

## 🔄 Types de Reranking

### Cross-Encoder (Local, Gratuit)
```yaml
reranking:
  type: "cross-encoder"
  model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
```
- Exécuté localement
- Gratuit
- Qualité: ⭐⭐⭐⭐
- Vitesse: Moyen

### Cohere (API, Payant)
```yaml
reranking:
  type: "cohere"
  model: "rerank-multilingual-v3.0"
```
- Via API Cohere
- ~$1-2 / 1000 requêtes
- Qualité: ⭐⭐⭐⭐⭐ (meilleure)
- Support multilingue natif

### NoOp (Désactivé)
```yaml
reranking:
  type: "noop"
```
- Pas de reranking
- Pass-through

---

## 💡 Bonnes pratiques

### Quand utiliser quoi ?

| Cas d'usage | Recommandation |
|-------------|----------------|
| **Recherche générale** | Dense Simple |
| **Mots-clés techniques** | BM25 Pure |
| **Haute précision** | Hybrid + Rerank |
| **Production critique** | Premium Cohere |
| **Multilingue** | Cohere Reranker |
| **Budget limité** | Dense + Cross-Encoder |

### Optimisation des performances

1. **Commencer simple**: Dense ou BM25
2. **Mesurer**: Utiliser le comparateur
3. **Itérer**: Tester différentes configs
4. **Hybrid pour qualité**: Si précision critique
5. **Reranking pour top-k**: Affiner les 10-20 premiers résultats
6. **Filtres métadonnées**: Réduire l'espace de recherche

### Paramètres à ajuster

```python
# Dense
similarity_threshold: 0.5-0.8  # Plus élevé = plus strict
top_k: 5-20                     # Selon besoin

# BM25
k1: 1.2-2.0    # Saturation (1.5 standard)
b: 0.0-1.0     # Normalisation longueur (0.75 standard)

# Hybrid
dense_weight: 0.5-0.7  # Favoriser sémantique
bm25_weight: 0.3-0.5   # Pour termes exacts
fusion_strategy: "rrf"  # Recommandé

# Reranking
top_k_per_retriever: 20-50  # Large rappel avant rerank
reranker_top_k: 5-10        # Final top-k
```

---

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python -m pytest tests/test_retrieval_comparison.py

# Exemples
python examples/retrieval_examples.py

# Comparaison personnalisée
python tests/test_retrieval_comparison.py --config my_config.yaml
```

---

## 📚 Références

### Papers
- BM25: Robertson & Zaragoza, 2009
- RRF: Cormack et al., 2009
- Cross-Encoders: Reimers & Gurevych, 2019

### Modèles recommandés

**Embeddings**:
- `all-MiniLM-L6-v2` (rapide, 80M params)
- `all-mpnet-base-v2` (qualité, 110M params)
- `text-embedding-3-small` (OpenAI, excellent)

**Cross-Encoders**:
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (rapide)
- `cross-encoder/ms-marco-MiniLM-L-12-v2` (meilleur)
- `cross-encoder/ms-marco-electra-base` (très bon)

---

## 🤝 Contribution

Pour ajouter une nouvelle stratégie de retrieval :

1. Implémenter `IRetriever` dans `src/retrieval/`
2. Enregistrer dans `RetrievalStrategy._get_*_retriever()`
3. Ajouter les paramètres dans `RetrievalConfig`
4. Créer une config YAML exemple
5. Ajouter des tests

---

## 📞 Support

Pour questions ou bugs :
- Documentation: Ce fichier
- Exemples: `examples/retrieval_examples.py`
- Tests: `tests/test_retrieval_comparison.py`

---

**Version**: 1.0.0  
**Date**: 2024  
**Status**: ✅ Production-ready
