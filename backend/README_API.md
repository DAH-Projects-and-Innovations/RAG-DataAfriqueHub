

## 1. Route : Ingestion de Document (`POST /ingest`)

Cette route sert à "nourrir" le cerveau de l'IA avec de nouvelles connaissances.

### **Exemple d'Entrée (Request Body)**

C'est ce que ton code attend dans `src/api/schemas.py`.

```json
{
  "source": "data/afrique_hub_rapport.txt",
  "loader_name": "text_loader",
  "chunker_name": "overlap_chunker"
}

```

* **`source`** : Le chemin ou l'URL du document à lire.
* **`loader_name`** : L'outil spécifique pour lire ce format (ici, notre `TextLoader`).
* **`chunker_name`** : L'algorithme qui va découper le texte en morceaux (indispensable pour que l'IA ne sature pas).

### **Exemple de Sortie (Response Body)**

C'est ce que l'utilisateur reçoit si tout se passe bien.

```json
{
  "status": "success",
  "message": "Document data/afrique_hub_rapport.txt ingéré avec succès",
  "task_id": "ingest_2026_02_03_12345"
}

```

---

## 2. Route : Question / Réponse (`POST /query`)

C'est la route "Star", celle qui simule le moteur RAG complet.

### **Exemple d'Entrée (Request Body)**

L'utilisateur pose sa question ici.

```json
{
  "question": "Quelles sont les opportunités économiques en Afrique de l'Ouest ?",
  "top_k": 3,
  "streaming": false
}

```

* **`question`** : La requête en langage naturel.
* **`top_k`** : On demande à l'API de chercher les **3 meilleurs documents** en base pour répondre.
* **`streaming`** : Défini sur `false` pour recevoir la réponse d'un bloc (plus simple pour le test).

### **Exemple de Sortie (Response Body)**

Voici le JSON riche que ton API génère.

```json
{
  "answer": "[STUB] Réponse RAG : L'Afrique de l'Ouest présente des opportunités majeures dans le secteur du numérique et de l'énergie solaire.",
  "sources": [
    {
      "content": "...le secteur du numérique en Côte d'Ivoire connaît une croissance de 15%...",
      "metadata": { "source": "rapport_eco_2025.txt", "page": 12 }
    }
  ],
  "metadata": {
    "original_query": "Quelles sont les opportunités économiques en Afrique de l'Ouest ?",
    "steps": [
      { "step": "query_rewriting", "num_queries": 1 },
      { "step": "retrieval", "num_docs": 3 },
      { "step": "generation", "answer_length": 112 }
    ],
    "top_k": 3
  },
  "timestamp": "2026-02-03T21:45:12.456Z"
}

```

---
