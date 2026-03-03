FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

# Installation des outils pour les PDF et la base de données
RUN apt-get update && apt-get install -y build-essential libmagic-dev && rm -rf /var/lib/apt/lists/*

# Installation de tes dépendances (ton environnement)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copie de tes scripts Python
COPY . .

# On lance le moteur pour que l'interface puisse l'utiliser
# (Remplace src.api.main:app par le fichier qui gère tes réponses si besoin)
CMD ["uv", "run", "python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]