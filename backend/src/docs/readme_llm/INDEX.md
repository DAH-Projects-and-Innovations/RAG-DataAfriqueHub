# 📑 INDEX - Tâche 4 : Moteur RAG avec Génération Contrôlée et Citations

## 📂 Structure des Fichiers

```
task4_rag/
├── README.md                        ⭐ COMMENCER ICI - Vue d'ensemble
├── TASK4_DELIVERABLES.md            📦 Liste complète des livrables
├── requirements.txt                 📋 Dépendances Python
│
├── src/
│   ├── llm/                         🔌 Abstraction LLM multi-provider
│   │   ├── __init__.py              - Exports du module
│   │   ├── base_llm.py              - Classes LLM (OpenAI, Anthropic, Ollama, HF)
│   │   └── prompt_manager.py        - Gestion prompts versionnés
│   │
│   ├── rag/                         🤖 Moteur RAG principal
│   │   ├── __init__.py              - Exports du module
│   │   ├── engine.py                - RAGEngine, SimpleRAG, CitationRAG
│   │   └── models.py                - RAGResponse, RAGQuery, Source, Citation
│   │
│   └── prompts/                     📝 Bibliothèque de prompts
│       ├── __init__.py              - Exports du module
│       └── example_prompts.py       - 13 prompts prêts à l'emploi
│
├── configs/rag/                     ⚙️ Configurations YAML
│   ├── simple.yaml                  - Config RAG simple
│   ├── citations.yaml               - Config avec citations
│   └── secure.yaml                  - Config sécurisée
│
└── examples/                        📚 Exemples d'utilisation
    └── rag_examples.py              - 10 exemples commentés
```

---

## 🚀 Guide de Démarrage Rapide

### 1️⃣ Lire la Documentation (10 min)

1. **README.md** - Vue d'ensemble, installation, quick start
2. **TASK4_DELIVERABLES.md** - Détails des livrables
3. **examples/rag_examples.py** - 10 exemples pratiques

### 2️⃣ Installer les Dépendances (5 min)

```bash
# Option 1: Ollama (gratuit, local) - RECOMMANDÉ pour débuter
pip install pyyaml ollama

# Option 2: OpenAI
pip install pyyaml openai

# Option 3: Tout installer
pip install -r requirements.txt
```

### 3️⃣ Tester les Exemples (10 min)

```bash
# Exécuter les exemples
python examples/rag_examples.py
```

### 4️⃣ Intégrer dans Votre Code (30 min)

```python
from src.rag import RAGEngine, RAGQuery
from src.llm import create_llm, create_default_prompt_manager

# 1. Créer le LLM
llm = create_llm("ollama", "llama2")  # ou "openai", "gpt-4"

# 2. Créer le moteur
engine = RAGEngine(
    retriever=your_retriever,  # Depuis Tâche 3
    llm=llm,
    prompt_manager=create_default_prompt_manager()
)

# 3. Utiliser
response = engine.query(RAGQuery(question="..."))
print(response.answer)
```

---

## 📋 Checklist d'Utilisation

### Pour Débuter
- [ ] Lire README.md
- [ ] Installer les dépendances : `pip install pyyaml ollama`
- [ ] Installer Ollama : https://ollama.ai/download
- [ ] Télécharger un modèle : `ollama pull llama2`
- [ ] Tester examples/rag_examples.py

### Pour Comprendre
- [ ] Étudier src/llm/base_llm.py (abstraction LLM)
- [ ] Étudier src/rag/engine.py (moteur RAG)
- [ ] Étudier src/llm/prompt_manager.py (prompts)
- [ ] Examiner les 13 prompts dans src/prompts/example_prompts.py

### Pour Utiliser en Production
- [ ] Choisir le provider LLM approprié
- [ ] Choisir la configuration (simple/citations/secure)
- [ ] Adapter les prompts à votre domaine
- [ ] Configurer prevent_hallucinations=True
- [ ] Tester avec questions hors contexte
- [ ] Monitorer les niveaux de confiance

---

## 🎯 Fichiers Clés par Objectif

### Je veux comprendre le système
→ **README.md** (architecture, fonctionnalités)

### Je veux voir des exemples
→ **examples/rag_examples.py** (10 exemples)

### Je veux utiliser immédiatement
→ **README.md** section "Quick Start"
→ **configs/rag/simple.yaml** (config simple)

### Je veux la meilleure qualité
→ **configs/rag/citations.yaml** (avec citations)
→ **configs/rag/secure.yaml** (sécurisé)

### Je veux comprendre le code
→ **src/rag/engine.py** (moteur principal)
→ **src/llm/base_llm.py** (abstraction LLM)
→ **src/llm/prompt_manager.py** (gestion prompts)

### Je veux créer mes propres prompts
→ **src/prompts/example_prompts.py** (13 exemples)
→ **src/llm/prompt_manager.py** (PromptTemplate)

### Je veux tout savoir
→ **TASK4_DELIVERABLES.md** (détails complets)

---

## 📊 Statistiques du Projet

- **Fichiers de code** : 11 modules Python (~2000 lignes)
- **Configurations** : 3 configs YAML prêtes
- **Prompts** : 13 templates professionnels
- **Exemples** : 10 exemples commentés
- **Providers LLM** : 4 supportés (OpenAI, Anthropic, Ollama, HF)
- **Modes RAG** : 3 (Simple, Citation, Secure)

---

## 🔗 Liens Rapides

| Fichier | Description | Temps lecture |
|---------|-------------|---------------|
| README.md | README principal | 10 min |
| TASK4_DELIVERABLES.md | Liste des livrables | 5 min |
| examples/rag_examples.py | 10 exemples | 15 min |
| src/rag/engine.py | Moteur RAG | 10 min |
| src/llm/base_llm.py | Abstraction LLM | 10 min |
| src/prompts/example_prompts.py | 13 prompts | 10 min |

---

## 💡 Conseils d'Utilisation

### Pour Apprendre
1. Commencer par README.md
2. Exécuter examples/rag_examples.py
3. Étudier un provider LLM (commencer par OllamaLLM)
4. Étudier RAGEngine
5. Créer son propre prompt

### Pour Utiliser
1. Choisir un provider LLM (Ollama pour débuter)
2. Choisir une config dans configs/rag/
3. Créer le moteur RAG
4. Tester avec vos questions
5. Ajuster température et paramètres

### Pour Optimiser
1. Tester plusieurs providers
2. Comparer les configurations
3. Mesurer temps de réponse et qualité
4. Ajuster les prompts
5. Monitorer les niveaux de confiance

---

## 🌟 Fonctionnalités Clés

### 1. Multi-Provider LLM
```python
# Facile de changer de provider
llm = create_llm("ollama", "llama2")      # Gratuit, local
llm = create_llm("openai", "gpt-4")       # Meilleure qualité
llm = create_llm("anthropic", "claude-3") # Excellent pour citations
```

### 2. RAG avec Citations
```python
# Citations automatiques
response = engine.query(RAGQuery(
    question="What is Python?",
    include_citations=True
))

# Output:
# "Python is a programming language [1] created in 1991 [2]."
# 
# Sources:
# [1] Python Introduction (python.org)
# [2] History of Python (wikipedia.org)
```

### 3. Protection Anti-Hallucination
```python
# Configuration sécurisée
config = RAGConfig(
    prevent_hallucinations=True,
    require_sources=True,
    min_relevance_score=0.7
)

# Réponse si pas de sources trouvées:
# "I don't have enough information in my knowledge base..."
```

### 4. Prompts Configurables
```python
# Utiliser un prompt prédéfini
manager.render_template(
    "technical_doc_system",
    sources="..."
)

# Créer un prompt personnalisé
custom = PromptTemplate(
    name="my_prompt",
    version="1.0",
    template="You are a {role}. {context}",
    variables=["role", "context"]
)
```

---

## 📞 Support

**Questions sur l'architecture ?**
→ Voir README.md section "Architecture"

**Questions sur l'utilisation ?**
→ Voir examples/rag_examples.py

**Questions sur les prompts ?**
→ Voir src/prompts/example_prompts.py

**Problème avec un provider ?**
→ Voir src/llm/base_llm.py

**Configuration ne marche pas ?**
→ Vérifier configs/rag/*.yaml

---

## ✅ Prochaines Étapes

Après avoir exploré ce module RAG :

1. **Intégration** : Connecter avec le retrieval (Tâche 3)
2. **Personnalisation** : Adapter les prompts à votre domaine
3. **Test** : Tester avec vos données
4. **Optimisation** : Ajuster température, top_k, etc.
5. **Production** : Déployer avec monitoring

---

## 🔄 Intégration avec Tâches Précédentes

```
Tâche 3 (Retrieval) → Tâche 4 (RAG)
       ↓                    ↓
  IRetriever  ──────→  RAGEngine
                           ↓
                      RAGResponse
                    (avec citations)
```

**Exemple d'intégration :**
```python
# Tâche 3
from src.retrieval import create_retriever
retriever = create_retriever(mode="hybrid", ...)

# Tâche 4
from src.rag import RAGEngine
from src.llm import create_llm

llm = create_llm("ollama", "llama2")
engine = RAGEngine(retriever, llm, ...)

# Utilisation
response = engine.query(RAGQuery(question="..."))
```

---

## 🎓 Cas d'Usage Recommandés

| Use Case | Provider | Config | Prompt |
|----------|----------|--------|--------|
| **FAQ Basic** | Ollama | simple.yaml | generic_qa |
| **Documentation** | OpenAI | citations.yaml | technical_doc |
| **Support Client** | OpenAI | simple.yaml | customer_support |
| **Recherche** | Anthropic | citations.yaml | detailed_analysis |
| **Médical/Légal** | Anthropic | secure.yaml | medical_info/legal |
| **Développement** | Ollama | simple.yaml | generic_qa |
| **Production** | OpenAI/Anthropic | citations.yaml | [selon domaine] |

---

**Version** : 1.0.0  
**Date** : 2024  
**Status** : ✅ Production-ready  
**Support** : Ollama (gratuit) + OpenAI + Anthropic + HuggingFace
