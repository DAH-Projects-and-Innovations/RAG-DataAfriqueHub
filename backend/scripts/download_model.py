import os
import argparse
from huggingface_hub import hf_hub_download

# Configuration par défaut
DEFAULT_MODEL = "mistral"
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# Presets de modèles (GGUF Quantized)
MODEL_PRESETS = {
    "mistral": {
        "repo": "MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF",
        "file": "Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"
    },
    "llama3": {
        "repo": "MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF",
        "file": "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    },
    "phi3": {
        "repo": "microsoft/Phi-3-mini-4k-instruct-gguf",
        "file": "Phi-3-mini-4k-instruct-q4.gguf"
    },
    "gemma2": {
        "repo": "bartowski/gemma-2-9b-it-GGUF",
        "file": "gemma-2-9b-it-Q4_K_M.gguf"
    }
}

def download_model(model_key: str):
    """Télécharge un modèle GGUF depuis HuggingFace en utilisant un preset ou des arguments"""
    
    if model_key not in MODEL_PRESETS:
        print(f"❌ Modèle inconnu dans les presets : {model_key}")
        print(f"Options disponibles : {', '.join(MODEL_PRESETS.keys())}")
        return

    config = MODEL_PRESETS[model_key]
    repo_id = config["repo"]
    filename = config["file"]
    
    print(f"⬇️  Téléchargement de {model_key} ({filename})...")
    print(f"   Source : {repo_id}")
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    try:
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=MODELS_DIR,
            local_dir_use_symlinks=False
        )
        print(f"✅ Modèle téléchargé avec succès : {file_path}")
        print(f"\n💡 Configuration à utiliser :")
        print(f"model_path: models/{filename}")
        return file_path
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Télécharger des modèles GGUF pour le RAG")
    parser.add_argument("model", nargs="?", default=DEFAULT_MODEL, help=f"Nom du modèle ({', '.join(MODEL_PRESETS.keys())})")
    parser.add_argument("--list", action="store_true", help="Lister les modèles disponibles")
    
    args = parser.parse_args()
    
    if args.list:
        print("Modèles disponibles :")
        for key, conf in MODEL_PRESETS.items():
            print(f"- {key}: {conf['file']}")
    else:
        download_model(args.model)
