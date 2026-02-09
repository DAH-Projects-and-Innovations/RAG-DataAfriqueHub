# README — Moteur RAG Générique

## 1. Objectif

Fournir un **moteur RAG (Retrieval-Augmented Generation) générique** capable de produire :

- des **réponses fiables**,
- des **réponses traçables avec sources citées**,
- des réponses **adaptées au grand public**.

Le moteur doit être **réutilisable**, **configurable** et **sécurisé contre les réponses hors contexte**.

---

## 2. Périmètre fonctionnel

Le projet couvre uniquement les fonctionnalités suivantes :

- Abstraction des LLM (open source + API)
- Implémentation de deux modes :
  - RAG simple
  - RAG avec citations
- Gestion des prompts via templates versionnés
- Génération de réponses structurées (texte + sources)
- Mécanismes de sécurisation contre les hallucinations

---

## 3. LLM supportés

### 3.1 LLM open source (local)

Utilisés pour le développement et les environnements à faible budget.

- **Llama 3.1 (8B / 70B)** — via Ollama
- **Mistral 7B** — via Ollama

---

### 3.2 LLM via API (cloud)

Utilisés pour de meilleures performances et une latence réduite.

- **GPT-4o-mini** (OpenAI)
- **Gemini 1.5 Flash** (Google)
- **Claude Haiku / Sonnet** (Anthropic)

👉 Le moteur doit permettre de **changer de LLM sans modifier le code métier**.

> **Implémentation actuelle** :
> Les adaptateurs suivants sont disponibles dans `src/llm/` :
>
> - `OpenAILLM` (`src/llm/openai_llm.py`) : Interface pour l'API OpenAI.
> - `OllamaLLM` (`src/llm/ollama_llm.py`) : Interface pour Ollama (local).

---

## 4. Sources de données pour le RAG

Le moteur RAG peut être alimenté par les sources suivantes :

### 4.1 Documents fichiers

- PDF (règlements, rapports, guides)
- Word / Excel
- Présentations

Outils possibles :

- PyMuPDF
- Unstructured
- Docling

---

### 4.2 Sources web

- Sites institutionnels
- Pages HTML statiques ou dynamiques

Outils possibles :

- BeautifulSoup
- Scrapy
- Playwright

---

### 4.3 APIs (optionnel)

- APIs publiques ou privées
- Données structurées

---

## 5. Modes de fonctionnement du RAG

### 5.1 RAG simple

Mode utilisé pour le MVP.

Flux :

1. Question utilisateur
2. Recherche vectorielle
3. Sélection des passages pertinents
4. Génération de la réponse

---

### 5.2 RAG avec citations

Mode recommandé pour les réponses fiables et traçables.

Flux :

1. Question utilisateur
2. Reformulation de la requête (query rewriting)
3. Recherche vectorielle
4. Re-ranking des résultats
5. Génération de la réponse avec obligation de citer les sources

---

## 6. Gestion des prompts

Les prompts sont :

- stockés sous forme de **templates**,
- versionnés (v1, v2, etc.),
- modifiables sans changer le code.

Exemples de prompts :

- prompt de réponse simple
- prompt de réponse avec citations
- prompt de refus hors contexte

---

## 7. Format de réponse attendu

Toutes les réponses doivent respecter un format structuré :

```json
{
  "answer": "Réponse en français",
  "sources": [
    {
      "document": "Nom du document",
      "page": 2,
      "excerpt": "Extrait utilisé"
    }
  ]
}
```

## 8. Sécurisation contre les réponses hors contexte

Le moteur RAG respecte strictement la consigne de refus. Si aucune information n'est trouvée, il retourne :

> "Je ne dispose pas d’informations fiables dans les documents fournis pour répondre à cette question."

Cette phrase est codée par défaut dans le prompt système des adaptateurs LLM.

## 9. Configuration des Prompts

Les prompts sont configurables via le fichier YAML de configuration. Exemple :

```yaml
llm:
  name: "openai"
  params:
    model_name: "gpt-4o-mini"
    system_prompt: |
      Tu es un expert juridique. Utilise les documents pour répondre.
      Si tu ne trouves pas l'info, réponds exactement :
      'Je ne dispose pas d’informations fiables dans les documents fournis pour répondre à cette question.'
    user_prompt_template: |
      Voici le contexte :
      {context_str}

      Question : {query}
```

## 10. Livrables attendus

À la fin du projet, les livrables obligatoires sont :

- un **moteur RAG opérationnel**, utilisable via API,
- des **réponses avec sources citées** (documents, pages, extraits),
- des **exemples de prompts configurables et versionnés**.

Tout livrable ne respectant pas ces critères est considéré comme incomplet.

---

## 10. Règle clé du projet

👉 **Toute réponse doit être strictement justifiée par les données indexées.**

Si l’information demandée n’existe pas dans les documents fournis,  
le moteur doit **refuser de répondre**, sans extrapolation ni supposition.

Cette règle prime sur toute autre considération (performance, fluidité, complétude).

## 11. Liens et sources de données fiables (pour les tests RAG)

Les sources ci-dessous sont **officielles, stables et vérifiables**.  
Elles sont recommandées pour tester la qualité, la traçabilité et la sécurité du moteur RAG.

---

### 11.1 Institutions internationales

- Banque mondiale  
  https://www.worldbank.org

- Organisation mondiale de la santé (OMS)  
  https://www.who.int

- UNESCO  
  https://www.unesco.org

- Organisation internationale du travail (OIT)  
  https://www.ilo.org

---

### 11.2 Institutions et services publics francophones

- Service Public (France)  
  https://www.service-public.fr

- Légifrance (textes juridiques officiels)  
  https://www.legifrance.gouv.fr

- Campus France (mobilité étudiante, bourses)  
  https://www.campusfrance.org

---

### 11.3 Institutions africaines (exemples)

- Gouvernement de Côte d’Ivoire  
  https://www.gouv.ci

- Gouvernement du Sénégal  
  https://www.gouv.sn

- UEMOA  
  https://www.uemoa.int

- CEDEAO (ECOWAS)  
  https://www.ecowas.int

---

### 11.4 Sources académiques et éducation (open access)

- MIT OpenCourseWare  
  https://ocw.mit.edu

- HAL (archives scientifiques ouvertes)  
  https://hal.science

- arXiv  
  https://arxiv.org

- PubMed Central (PMC)  
  https://www.ncbi.nlm.nih.gov/pmc/

---

### 11.5 Open Data

- data.gouv.fr  
  https://www.data.gouv.fr

- World Bank Open Data  
  https://data.worldbank.org

- UN Data  
  https://data.un.org

---

### 11.6 Jeux de données spécialisés RAG (benchmark)

- RAGBench  
  https://github.com/amazon-science/RAGBench

- BEIR Dataset  
  https://github.com/beir-cellar/beir

- HotpotQA  
  https://hotpotqa.github.io

---

### 11.7 Recommandation pour les tests

Pour les tests initiaux du moteur RAG, il est recommandé d’utiliser :

- des documents **officiels en PDF** (institutions, règlements),
- des documents **internes fictifs** (guides RH, règlements),
- un nombre limité de sources afin de contrôler les résultats.

👉 Toute réponse générée doit pouvoir être reliée explicitement à l’un de ces documents.
