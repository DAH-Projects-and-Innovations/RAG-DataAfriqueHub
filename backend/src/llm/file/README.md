# 🤖 Moteur RAG avec Génération Contrôlée et Citations - Tâche 4

> Moteur RAG production-ready avec support multi-providers, citations traçables et protection contre les hallucinations

[![Status](https://img.shields.io/badge/status-production--ready-green)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![LLM Support](https://img.shields.io/badge/LLM-OpenAI%20|%20Anthropic%20|%20Ollama%20|%20HF-orange)]()

---

## ✨ Fonctionnalités

### 🎯 Moteur RAG Opérationnel
- ✅ **3 modes de fonctionnement**: Simple, Citations, Sécurisé
- ✅ **Génération contrôlée** avec anti-hallucination
- ✅ **Évaluation de confiance** automatique
- ✅ **Réponses structurées** avec sources et métadonnées

### 🔌 Abstraction LLM Multi-Provider
- ✅ **OpenAI** (GPT-3.5, GPT-4, GPT-4o)
- ✅ **Anthropic** (Claude 3.5, Claude Opus)
- ✅ **Ollama** (Llama, Mistral, etc. - local/gratuit)
- ✅ **HuggingFace** (tous modèles compatibles)

### 📝 Gestion de Prompts Avancée
- ✅ **Templates versionnés** avec variables
- ✅ **13 prompts prédéfinis** (Q&A, technique, médical, légal, etc.)
- ✅ **Import/Export JSON** pour partage
- ✅ **Composition de prompts** modulaire

### 🔒 Sécurité et Fiabilité
- ✅ **Anti-hallucination** renforcée
- ✅ **Citations obligatoires** [1], [2], [3]
- ✅ **Niveaux de confiance** (High/Medium/Low/Uncertain)
- ✅ **Vérification contexte** automatique

---

## 🚀 Installation

```bash
# Dépendances de base
pip install pyyaml dataclasses

# Pour OpenAI
pip install openai

# Pour Anthropic
pip install anthropic

# Pour Ollama (gratuit, local)
pip install ollama

# Pour HuggingFace
pip install transformers torch
```

---

## ⚡ Quick Start

### 1️⃣ RAG Simple (30 secondes)

```python
from src.rag import RAGEngine, RAGQuery, RAGConfig
from src.llm import create_llm, create_default_prompt_manager

# 1. Créer le LLM
llm = create_llm(
    provider="openai",
    model="gpt-4o-mini",
    api_key="your-api-key"
)

# 2. Créer le moteur RAG
engine = RAGEngine(
    retriever=your_retriever,  # De la tâche 3
    llm=llm,
    prompt_manager=create_default_prompt_manager(),
    config=RAGConfig()
)

# 3. Poser une question
query = RAGQuery(question="What is machine learning?")
response = engine.query(query)

# 4. Afficher la réponse
print(response.answer)
print(f"Sources: {len(response.sources)}")
print(f"Confidence: {response.confidence.value}")
```

### 2️⃣ RAG avec Citations

```python
from src.rag import CitationRAG, RAGQuery

# Moteur avec citations forcées
engine = CitationRAG(
    retriever=your_retriever,
    llm=llm,
    prompt_manager=create_default_prompt_manager()
)

# Question
query = RAGQuery(
    question="How does photosynthesis work?",
    include_citations=True
)

response = engine.query(query)

# Afficher avec citations
print(response.get_formatted_answer(include_sources=True))
# Output:
# Photosynthesis is the process... [1] The chlorophyll... [2]
#
# Sources:
# [1] Biology Textbook, Chapter 5
# [2] Plant Science Journal, 2023
```

### 3️⃣ Charger depuis Configuration

```python
import yaml
from src.rag import RAGConfig

# Charger config
with open('configs/rag/citations.yaml') as f:
    config_dict = yaml.safe_load(f)

config = RAGConfig.from_dict(config_dict)
engine = RAGEngine(..., config=config)
```

---

## 📦 Configurations Prêtes à l'Emploi

| Config | Citations | Température | Use Case |
|--------|-----------|-------------|----------|
| **`simple.yaml`** | Non | 0.7 | FAQ, support basique |
| **`citations.yaml`** | Oui | 0.5 | Documentation, recherche |
| **`secure.yaml`** | Oui | 0.3 | Médical, légal, finance |

---

## 🎨 Modes de Fonctionnement

### Simple RAG
```python
from src.rag import SimpleRAG

engine = SimpleRAG(...)  # Pas de citations
response = engine.query(RAGQuery(question="..."))
```

**Caractéristiques:**
- Réponses rapides
- Pas de citations
- Idéal pour FAQ

### Citation RAG
```python
from src.rag import CitationRAG

engine = CitationRAG(...)  # Citations forcées
response = engine.query(RAGQuery(question="..."))
```

**Caractéristiques:**
- Citations obligatoires [1], [2], [3]
- Traçabilité complète
- Idéal pour documentation

### Secure RAG
```python
config = RAGConfig(
    prevent_hallucinations=True,
    confidence_threshold=0.7,
    min_relevance_score=0.7
)
engine = RAGEngine(..., config=config)
```

**Caractéristiques:**
- Anti-hallucination renforcée
- Seuils élevés
- Idéal pour domaines critiques

---

## 📝 Prompts Configurables

### Prompts Prédéfinis (13)

1. **generic_qa_system** - Q&A générique
2. **technical_doc_system** - Documentation technique
3. **medical_info_system** - Informations médicales
4. **legal_research_system** - Recherche juridique
5. **customer_support_system** - Support client
6. **eli5_system** - Explications simples
7. **detailed_analysis_system** - Analyses détaillées
8. **comparative_system** - Analyses comparatives
9. **multilingual_system** - Support multilingue
10. **conversational_system** - Conversations naturelles
11. **structured_json_system** - Réponses JSON
12. **bullet_points_system** - Bullet points
13. **fact_check_system** - Vérification de faits

### Créer un Prompt Personnalisé

```python
from src.llm import PromptTemplate, PromptManager

# 1. Définir le template
custom_prompt = PromptTemplate(
    name="custom_support",
    version="1.0",
    template="""You are a support agent for {company_name}.

Help the user using this context:
{context}

Always be {tone} and professional.""",
    variables=["company_name", "context", "tone"]
)

# 2. Enregistrer
manager = PromptManager()
manager.register_template(custom_prompt)

# 3. Utiliser
rendered = manager.render_template(
    "custom_support",
    company_name="Acme Corp",
    context="...",
    tone="friendly"
)
```

---

## 🏗️ Architecture

```
User Query
    ↓
RAGEngine
    ├─→ Retriever (Tâche 3) → Documents
    ├─→ PromptManager → System + User Prompts
    ├─→ LLM (OpenAI/Anthropic/Ollama/HF) → Answer
    └─→ Post-Processing → Citations + Confidence
    ↓
RAGResponse
    ├─ answer: str
    ├─ sources: List[Source]
    ├─ citations: List[Citation]
    ├─ confidence: ConfidenceLevel
    └─ metadata: Dict
```

---

## 📊 Structure des Réponses

```python
@dataclass
class RAGResponse:
    # Réponse
    answer: str
    
    # Sources et citations
    sources: List[Source]
    citations: List[Citation]
    
    # Confiance
    confidence: ConfidenceLevel  # HIGH, MEDIUM, LOW, UNCERTAIN
    based_on_context: bool
    
    # Métadonnées
    model_used: str
    tokens_used: int
    generation_time_ms: float
```

### Exemple de Réponse

```python
{
    "answer": "Python is a programming language [1] created by Guido van Rossum in 1991 [2].",
    "sources": [
        {
            "id": "doc1",
            "content": "Python is a programming language...",
            "citation_id": 1,
            "relevance_score": 0.95
        },
        {
            "id": "doc2",
            "content": "Created by Guido van Rossum in 1991...",
            "citation_id": 2,
            "relevance_score": 0.92
        }
    ],
    "citations": [
        {"source_id": "doc1", "citation_number": 1, ...},
        {"source_id": "doc2", "citation_number": 2, ...}
    ],
    "confidence": "HIGH",
    "based_on_context": true,
    "tokens_used": 245
}
```

---

## 🔒 Protection Anti-Hallucination

### Mécanismes Intégrés

1. **System Prompts Stricts**
   ```
   "Answer ONLY using information from the context"
   "Do not use your general knowledge"
   ```

2. **Vérification Contexte**
   - Détection de phrases hors-contexte
   - Filtrage par pertinence minimum
   - Refus si pas de sources

3. **Évaluation de Confiance**
   - Score basé sur pertinence sources
   - Ratio citations/sources
   - Détection phrases d'incertitude

4. **Configuration Sécurisée**
   ```python
   config = RAGConfig(
       require_sources=True,  # Refuse sans sources
       prevent_hallucinations=True,
       confidence_threshold=0.7,
       min_relevance_score=0.7
   )
   ```

---

## 🌍 Support Multi-Provider

### Comparaison des Providers

| Provider | Coût | Qualité | Vitesse | Local |
|----------|------|---------|---------|-------|
| **OpenAI** | 💰💰 | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | ❌ |
| **Anthropic** | 💰💰💰 | ⭐⭐⭐⭐⭐ | ⚡⚡ | ❌ |
| **Ollama** | Gratuit | ⭐⭐⭐ | ⚡⚡ | ✅ |
| **HuggingFace** | Gratuit | ⭐⭐⭐ | ⚡ | ✅ |

### Exemples d'Utilisation

```python
# OpenAI
llm = create_llm("openai", "gpt-4", api_key="...")

# Anthropic
llm = create_llm("anthropic", "claude-3-5-sonnet-20241022", api_key="...")

# Ollama (gratuit, local)
llm = create_llm("ollama", "llama2", api_base="http://localhost:11434")

# HuggingFace
llm = create_llm("huggingface", "meta-llama/Llama-2-7b-chat-hf")
```

---

## 📚 Exemples Complets

Voir `examples/rag_examples.py` pour 10 exemples détaillés:

1. RAG Simple
2. RAG avec Citations
3. RAG Sécurisé
4. RAG Conversationnel
5. Réponses Structurées (JSON)
6. RAG Domaine Spécifique
7. RAG Multilingue
8. Niveaux de Confiance
9. Chargement depuis Config
10. Bonnes Pratiques

```bash
python examples/rag_examples.py
```

---

## 🎯 Cas d'Usage par Domaine

### Documentation Technique
```python
config = RAGConfig(
    system_prompt_template="technical_doc_system",
    enable_citations=True,
    default_temperature=0.5
)
```

### Support Médical
```python
config = RAGConfig(
    system_prompt_template="medical_info_system",
    prevent_hallucinations=True,
    require_sources=True,
    confidence_threshold=0.8
)
```

### Support Client
```python
config = RAGConfig(
    system_prompt_template="customer_support_system",
    enable_citations=False,  # Plus fluide
    default_temperature=0.7
)
```

---

## 📋 Livrables de la Tâche 4

✅ **1. Moteur RAG opérationnel**
- `src/rag/engine.py` - 3 moteurs (Simple, Citation, Base)
- Support multi-provider LLM
- Génération contrôlée avec anti-hallucination

✅ **2. Réponses avec sources citées**
- `src/rag/models.py` - Modèles complets (Source, Citation, RAGResponse)
- Citations automatiques [1], [2], [3]
- Métadonnées riches (confiance, tokens, temps)

✅ **3. Exemple de prompts configurables**
- `src/llm/prompt_manager.py` - Gestionnaire de prompts
- `src/prompts/example_prompts.py` - 13 prompts prêts
- Templates versionnés avec variables

✅ **Bonus:**
- 3 configurations YAML prêtes
- 10 exemples d'utilisation
- Documentation complète

---

## 🧪 Tests

```bash
# Exécuter les exemples
python examples/rag_examples.py

# Test avec différents providers
python -c "from src.llm import create_llm; llm = create_llm('ollama', 'llama2'); print('✓ Ollama OK')"
```

---

## 📖 Documentation

- **README.md** - Ce fichier (vue d'ensemble)
- **docs/RAG_ENGINE.md** - Guide technique détaillé
- **docs/PROMPTS_GUIDE.md** - Guide des prompts
- **examples/rag_examples.py** - 10 exemples commentés

---

## 🤝 Intégration avec Tâches Précédentes

```python
# Tâche 3: Retrieval
from src.retrieval import create_retriever

retriever = create_retriever(mode="hybrid", ...)

# Tâche 4: RAG
from src.rag import RAGEngine
from src.llm import create_llm, create_default_prompt_manager

engine = RAGEngine(
    retriever=retriever,  # De tâche 3
    llm=create_llm("openai", "gpt-4o-mini"),
    prompt_manager=create_default_prompt_manager()
)

# Pipeline complet
response = engine.query(RAGQuery(question="..."))
```

---

## 💡 Bonnes Pratiques

✅ **DO:**
- Toujours citer les sources
- Utiliser `prevent_hallucinations=True` en prod
- Tester avec questions hors contexte
- Monitorer les niveaux de confiance
- Utiliser température basse (0.3-0.5) pour précision

❌ **DON'T:**
- Ne pas désactiver `require_sources` en prod
- Ne pas ignorer les avertissements de confiance
- Ne pas utiliser température élevée (>0.8)
- Ne pas mélanger domaines incompatibles

---

## 📊 Statistiques

- **Lignes de code**: ~2000 lignes
- **Fichiers**: 11 fichiers Python
- **Prompts**: 13 templates prédéfinis
- **Configurations**: 3 configs YAML
- **Providers**: 4 LLM providers supportés

---

**Version**: 1.0.0  
**Date**: 2024  
**Status**: ✅ Production-ready
