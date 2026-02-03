Compris ! J'ai retiré toute référence personnelle pour rendre le document totalement professionnel et neutre. J'ai remplacé "Nancy" par "le noyau central (Core)" ou "le moteur de pipeline".

Voici le fichier README.md définitif, prêt à être exporté.

🚀 RAG-DataAfriqueHub Backend API
Ce backend est le moteur de service pour le système RAG (Retrieval-Augmented Generation) de DataAfriqueHub. Il repose sur une architecture modulaire qui permet de configurer et d'interchanger dynamiquement les composants de traitement (LLM, Vector Store, Embeddings).

🛠️ Installation et Démarrage
1. Prérequis
Python 3.9+

Un environnement virtuel (recommandé) :

Bash

python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
2. Installation des dépendances
Bash

pip install -r requirements.txt
3. Lancer l'API de développement
Bash

uvicorn src.api.main:app --reload
L'API sera disponible sur : http://127.0.0.1:8000

📡 Documentation et Tests (Swagger)
L'API intègre une documentation interactive permettant de tester les points d'entrée sans client externe : 👉 Lien local : http://127.0.0.1:8000/docs

🧪 Exemples de Requêtes Standardisées
🔹 1. Ingestion de Document (POST /ingest)
Cette route permet d'envoyer un document pour qu'il soit traité par le pipeline de données.

Corps de la requête (JSON) :

JSON

{
  "source": "data/test_doc.txt",
  "loader_name": "text_loader",
  "chunker_name": "overlap_chunker"
}
Réponse type (200 OK) :

JSON

{
  "status": "success",
  "message": "Document data/test_doc.txt ingéré avec succès"
}
🔹 2. Question / Réponse (POST /query)
Interroge le moteur RAG sur la base des connaissances indexées.

Corps de la requête (JSON) :

JSON

{
  "question": "Quelle est la mission de DataAfriqueHub ?",
  "top_k": 3,
  "streaming": false
}
Réponse type (200 OK) :

JSON

{
  "answer": "[STUB] Réponse du moteur RAG",
  "sources": [],
  "metadata": {
    "original_query": "Quelle est la mission de DataAfriqueHub ?",
    "steps": [
      { "step": "query_rewriting", "num_queries": 1 },
      { "step": "retrieval", "num_docs": 0 },
      { "step": "generation", "answer_length": 25 }
    ]
  }
}
🏗️ Structure de l'Architecture
Le projet est divisé en trois couches distinctes pour assurer la flexibilité :

Couche API (src/api/) : Gère les points d'entrée HTTP, la validation des données avec Pydantic et la sérialisation des réponses.

Le Noyau Central (src/core/) : Définit les interfaces (contrats) que chaque composant doit respecter et gère la Factory qui assemble le pipeline.

La Couche d'Implémentation (src/implementations/) : Contient le code technique spécifique (actuellement configuré avec des stubs pour valider l'architecture).

⚙️ Configuration du Pipeline
L'orchestration de l'ensemble du système est pilotée par le fichier principal de configuration : 📄 configs/hybrid.yaml

C'est dans ce fichier que vous définissez quel modèle d'IA utiliser, les seuils de recherche vectorielle et les paramètres de réécriture de requêtes.

⚠️ Notes de Développement
Le système est actuellement livré avec des implémentations simulées (Stubs). Pour activer les fonctions réelles :

Éditez le fichier src/implementations/__init__.py.

Remplacez les retours statiques par la logique métier réelle (ex: appels API OpenAI, requêtes ChromaDB).

Les composants enregistrés via register_all_components() seront automatiquement injectés dans l'API.