#!/usr/bin/env python3
"""
Exemple complet d'utilisation du moteur RAG DataAfriqueHub

Ce script démontre :
1. Téléchargement et chargement d'un modèle local
2. Ingestion de documents
3. Requête RAG avec citations
4. Utilisation de prompts personnalisés
"""

import os
import sys

# Ajouter le backend au path
sys.path.append(os.path.dirname(__file__))

from src.llm.ollama_llm import LocalLLM
from src.llm.openai_llm import OpenAILLM
from src.core.models import Document, RAGResponse


def example_1_simple_generation():
    """Exemple 1: Génération simple sans contexte"""
    print("\n" + "="*80)
    print("EXEMPLE 1: Génération Simple")
    print("="*80 + "\n")
    
    # Option A: Utiliser un modèle local (après téléchargement)
    # Décommentez ces lignes après avoir téléchargé un modèle avec:
    # uv run python scripts/download_model.py phi3
    
    # llm = LocalLLM(model_path="models/Phi-3-mini-4k-instruct-q4.gguf")
    # response = llm.generate("Explique ce qu'est le RAG en 2 phrases.")
    # print(f"Réponse: {response}\n")
    
    # Option B: Utiliser OpenAI (nécessite une clé API)
    # llm = OpenAILLM(api_key="sk-votre-clé")
    # response = llm.generate("Explique ce qu'est le RAG en 2 phrases.")
    # print(f"Réponse: {response}\n")
    
    print("⚠️ Décommentez le code ci-dessus pour tester avec votre modèle\n")


def example_2_rag_with_context():
    """Exemple 2: RAG avec contexte documentaire"""
    print("\n" + "="*80)
    print("EXEMPLE 2: RAG avec Contexte")
    print("="*80 + "\n")
    
    # Création de documents de test
    docs = [
        Document(
            content="L'ESATIC (École Supérieure Africaine des TIC) est située à Abidjan, Côte d'Ivoire.",
            metadata={"source": "esatic_info.pdf", "page": 1}
        ),
        Document(
            content="L'ESATIC forme des ingénieurs en télécommunications, réseaux et informatique depuis 1996.",
            metadata={"source": "esatic_info.pdf", "page": 2}
        ),
        Document(
            content="Les filières principales sont: Réseaux et Télécommunications, Génie Logiciel, et Cybersécurité.",
            metadata={"source": "esatic_programmes.pdf", "page": 5}
        )
    ]
    
    # Initialisation du LLM (décommenter selon votre configuration)
    # llm = LocalLLM(model_path="models/Phi-3-mini-4k-instruct-q4.gguf")
    # 
    # # Question avec contexte
    # response = llm.generate_with_context(
    #     query="Quelles sont les filières proposées à l'ESATIC ?",
    #     context=docs
    # )
    # 
    # print(f"Question: Quelles sont les filières proposées à l'ESATIC ?")
    # print(f"\nRéponse: {response}")
    # print(f"\nSources disponibles: {len(docs)} documents")
    
    print("⚠️ Décommentez le code ci-dessus pour tester le RAG avec contexte\n")


def example_3_custom_prompts():
    """Exemple 3: Utilisation de prompts personnalisés"""
    print("\n" + "="*80)
    print("EXEMPLE 3: Prompts Personnalisés")
    print("="*80 + "\n")
    
    # Prompt système personnalisé
    custom_system = """Tu es un assistant pédagogique expert en orientation scolaire.
    Tu dois répondre de manière claire et encourageante.
    Si l'information n'est pas dans le contexte, dis-le poliment."""
    
    # Template utilisateur personnalisé
    custom_user = """Contexte documentaire:
{context_str}

Question de l'étudiant: {query}

Réponds de manière concise et cite tes sources."""
    
    # llm = LocalLLM(
    #     model_path="models/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf",
    #     system_prompt=custom_system,
    #     temperature=0.5
    # )
    # 
    # docs = [Document(content="L'ESATIC propose un cycle préparatoire de 2 ans.")]
    # 
    # response = llm.generate_with_context(
    #     query="Combien de temps dure le cycle préparatoire ?",
    #     context=docs,
    #     user_prompt_template=custom_user
    # )
    # 
    # print(f"Réponse personnalisée: {response}\n")
    
    print("⚠️ Décommentez le code pour tester les prompts personnalisés\n")


def example_4_rag_pipeline_complete():
    """Exemple 4: Pipeline RAG complet avec orchestrateur"""
    print("\n" + "="*80)
    print("EXEMPLE 4: Pipeline RAG Complet (Architecture)")
    print("="*80 + "\n")
    
    print("""
Pour utiliser le pipeline complet avec orchestrateur :

1. Configurer les composants dans un fichier YAML (voir configs/free.yaml)
2. Utiliser RAGPipelineFactory pour créer le pipeline
3. Ingérer des documents
4. Effectuer des requêtes avec citations

Exemple de code :

```python
from src.core.factory import RAGPipelineFactory

# Charger la configuration
pipeline = RAGPipelineFactory.create_from_config('configs/free.yaml')

# Ingérer des documents
from src.loaders.pdf_loader import PDFLoader
from src.chunkers.recursive_chunker import RecursiveChunker

loader = PDFLoader()
chunker = RecursiveChunker()
pipeline.ingest(loader, chunker, 'path/to/documents/')

# Effectuer une requête avec citations
response = pipeline.query(
    "Quelles sont les conditions d'admission ?",
    top_k=5,
    include_citations=True  # ✨ Active les citations automatiques
)

print(response.answer)  # Inclut les citations [1], [2], etc.
for i, source in enumerate(response.sources, 1):
    print(f"[{i}] {source.metadata.get('source')}")
```
    """)


def main():
    """Fonction principale"""
    print("\n" + "🚀"*40)
    print("   EXEMPLES D'UTILISATION - Moteur RAG DataAfriqueHub")
    print("🚀"*40)
    
    print("\n📝 Note importante:")
    print("- Pour tester avec un modèle local, téléchargez d'abord un modèle:")
    print("  uv run python scripts/download_model.py phi3")
    print("- Pour tester avec OpenAI, assurez-vous d'avoir une clé API")
    print("- Décommentez les sections de code dans chaque exemple\n")
    
    # Exécuter les exemples
    example_1_simple_generation()
    example_2_rag_with_context()
    example_3_custom_prompts()
    example_4_rag_pipeline_complete()
    
    print("\n" + "="*80)
    print("✅ Exemples terminés!")
    print("="*80 + "\n")
    print("Pour plus d'informations, consultez presentation.md")


if __name__ == "__main__":
    main()
