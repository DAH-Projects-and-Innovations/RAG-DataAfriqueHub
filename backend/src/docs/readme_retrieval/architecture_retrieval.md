# Diagrammes d'architecture du système de Retrieval

## 1. Vue d'ensemble du système

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Query                               │
│                  "What is machine learning?"                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RetrievalStrategy                             │
│                 (Orchestrateur principal)                       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              RetrievalConfig                              │ │
│  │  • mode: dense/bm25/hybrid                               │ │
│  │  • enable_reranking: true/false                          │ │
│  │  • metadata_filters: {...}                               │ │
│  └───────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ DenseRetriever  │ │  BM25Retriever  │ │ HybridRetriever │
│                 │ │                 │ │                 │
│ • Embeddings    │ │ • Term freq.    │ │ • Fusion RRF   │
│ • Cosine sim.   │ │ • IDF           │ │ • Weighted     │
│ • Vector store  │ │ • Local index   │ │ • Max          │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Top-K Results  │
                  │   (20 docs)     │
                  └────────┬────────┘
                           │
                   [Reranking enabled?]
                           │
                           ▼
              ┌────────────────────────────┐
              │        Reranker            │
              │  ┌──────────────────────┐  │
              │  │  Cross-Encoder       │  │
              │  │  (local, gratuit)    │  │
              │  └──────────────────────┘  │
              │  ┌──────────────────────┐  │
              │  │  Cohere API          │  │
              │  │  (cloud, payant)     │  │
              │  └──────────────────────┘  │
              └────────────┬───────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Final Results  │
                  │    (10 docs)    │
                  └─────────────────┘
```

## 2. Dense Retrieval - Flux détaillé

```
User Query: "What is machine learning?"
    │
    ▼
┌────────────────────────────────────────┐
│         Query Embedding                │
│  embedder.embed_query(query.text)     │
│  → [0.23, -0.15, 0.87, ...]           │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│      Vector Store Search               │
│  vector_store.search(                  │
│    query_embedding,                    │
│    top_k=10,                           │
│    filters={...}                       │
│  )                                     │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│    Similarity Scoring                  │
│  cosine_sim(query_emb, doc_emb)       │
│  → scores: [0.92, 0.87, 0.81, ...]   │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   Filter by threshold (optional)       │
│  if score >= similarity_threshold      │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   Score Normalization (optional)       │
│  normalize to [0, 1] range            │
└──────────────┬─────────────────────────┘
               │
               ▼
      Ranked Documents
```

## 3. BM25 Retrieval - Flux détaillé

```
User Query: "machine learning algorithms"
    │
    ▼
┌────────────────────────────────────────┐
│         Tokenization                   │
│  ["machine", "learning", "algorithms"] │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│    Remove Stopwords (optional)         │
│  ["machine", "learning", "algorithms"] │
│  (no stopwords in this example)        │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│      For each document:                │
│                                        │
│  1. Count term frequencies (TF)       │
│     tf("machine") = 3                 │
│     tf("learning") = 5                │
│                                        │
│  2. Compute IDF                       │
│     idf = log((N - df + 0.5) /        │
│               (df + 0.5) + 1)         │
│                                        │
│  3. BM25 Score                        │
│     score = Σ idf(term) *             │
│              (tf * (k1 + 1)) /        │
│              (tf + k1 * (1 - b +      │
│               b * |doc| / avgdl))     │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│    Apply metadata filters              │
│  filter by: language, date, etc.      │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│    Sort by BM25 score                  │
│  docs sorted: [12.5, 10.3, 8.7, ...]  │
└──────────────┬─────────────────────────┘
               │
               ▼
      Ranked Documents
```

## 4. Hybrid Retrieval - Stratégies de fusion

### A. Reciprocal Rank Fusion (RRF)

```
Dense Results:        BM25 Results:
1. Doc A (0.95)      1. Doc B (15.2)
2. Doc C (0.89)      2. Doc A (12.8)
3. Doc B (0.85)      3. Doc D (10.5)
4. Doc D (0.80)      4. Doc C (9.1)
     │                    │
     └────────┬───────────┘
              │
              ▼
    RRF Score Calculation
    
    Doc A: 1/(60+1) + 1/(60+2) = 0.0323
    Doc B: 1/(60+3) + 1/(60+1) = 0.0322
    Doc C: 1/(60+2) + 1/(60+4) = 0.0318
    Doc D: 1/(60+4) + 1/(60+3) = 0.0314
              │
              ▼
    Final Ranking:
    1. Doc A (0.0323)
    2. Doc B (0.0322)
    3. Doc C (0.0318)
    4. Doc D (0.0314)
```

### B. Weighted Sum Fusion

```
Dense Results:           BM25 Results:
Doc A: 0.95             Doc A: 15.2
Doc B: 0.85             Doc B: 12.8
     │                      │
     │  Normalize           │  Normalize
     ▼                      ▼
Doc A: 1.00             Doc A: 1.00
Doc B: 0.89             Doc B: 0.84
     │                      │
     │  × 0.6 (weight)      │  × 0.4 (weight)
     ▼                      ▼
Doc A: 0.60             Doc A: 0.40
Doc B: 0.53             Doc B: 0.34
     │                      │
     └──────────┬───────────┘
                │  Sum
                ▼
        Final Scores:
        Doc A: 1.00
        Doc B: 0.87
```

## 5. Reranking - Processus détaillé

```
Initial Results (20 docs from retrieval)
    │
    ▼
┌────────────────────────────────────────┐
│   Cross-Encoder Reranking              │
│                                        │
│   For each document:                   │
│   1. Encode (query, doc) pair together │
│   2. Get relevance score [0, 1]       │
│                                        │
│   Model: cross-encoder/                │
│          ms-marco-MiniLM-L-6-v2       │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   Relevance Scores                     │
│   Doc 5:  0.92 ← Très pertinent       │
│   Doc 12: 0.87                         │
│   Doc 3:  0.81                         │
│   Doc 8:  0.75                         │
│   Doc 1:  0.68                         │
│   ...                                  │
│   Doc 7:  0.45 ← Peu pertinent        │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   Filter by min_score (optional)       │
│   Keep only docs with score >= 0.5     │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   Select Top-K                         │
│   Return top 10 documents              │
└──────────────┬─────────────────────────┘
               │
               ▼
      Final Refined Results
```

## 6. Metadata Filtering - Exemples

```
Documents with metadata:
┌─────────────────────────────────────────────┐
│ Doc 1: {"lang": "python", "year": 2024}    │
│ Doc 2: {"lang": "java", "year": 2023}      │
│ Doc 3: {"lang": "python", "year": 2023}    │
│ Doc 4: {"lang": "python", "year": 2024}    │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  Filter: {"lang": "python", "year": 2024}  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
              Results:
         ┌───────────────┐
         │ Doc 1 ✓       │
         │ Doc 4 ✓       │
         └───────────────┘

Advanced filters with operators:
┌─────────────────────────────────────────────┐
│ Filter: {                                   │
│   "year": {"$gte": 2023},                  │
│   "lang": {"$in": ["python", "java"]}      │
│ }                                           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
              Results:
         ┌───────────────┐
         │ Doc 1 ✓       │
         │ Doc 2 ✓       │
         │ Doc 3 ✓       │
         │ Doc 4 ✓       │
         └───────────────┘
```

## 7. Configuration dynamique - Flux

```
Initial State:
┌────────────────────────────────────┐
│  RetrievalStrategy                 │
│  mode: DENSE                       │
│  enable_reranking: false           │
└────────────────────────────────────┘
            │
            │ query("what is AI?")
            ▼
     [Dense retrieval]
            │
            ▼
       10 results
            │
            │ update_config(new_config)
            ▼
┌────────────────────────────────────┐
│  RetrievalStrategy                 │
│  mode: HYBRID                      │
│  enable_reranking: true            │
│  fusion_strategy: rrf              │
└────────────────────────────────────┘
            │
            │ query("what is AI?")
            ▼
  [Hybrid retrieval + Reranking]
            │
            ▼
       10 refined results
```

## 8. Système complet - Vue de bout en bout

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Pipeline                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │      User Query               │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   Query Rewriter (optional)   │
            │   - Expansion                 │
            │   - Reformulation             │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   RetrievalStrategy           │
            │   ┌─────────────────────┐     │
            │   │ Mode: HYBRID        │     │
            │   │ Fusion: RRF         │     │
            │   │ Reranking: enabled  │     │
            │   └─────────────────────┘     │
            └──────────────┬────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   [Dense]            [BM25]           [Metadata]
   20 docs            20 docs           filters
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │    Fusion (RRF)               │
            │    → 20 candidates            │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │    Reranker                   │
            │    (Cross-Encoder)            │
            │    → 10 best docs             │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   Context Assembly            │
            │   - Format documents          │
            │   - Add metadata              │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   LLM Generation              │
            │   - Prompt + context          │
            │   - Generate answer           │
            └──────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   Final Response              │
            │   - Answer                    │
            │   - Citations                 │
            │   - Confidence                │
            └───────────────────────────────┘
```

## 9. Légende des symboles

```
┌─────┐  Boîte / Composant
│     │
└─────┘

  │     Flux / Direction
  ▼

┌─────────────────────────────────┐
│ ┌─────────────────────────┐     │  Composant imbriqué
│ │                         │     │
│ └─────────────────────────┘     │
└─────────────────────────────────┘

  [Action]   Action / Opération

  → Result   Résultat
```