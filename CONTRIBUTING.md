# Contribuer à RAG-DataAfriqueHub

Merci de vouloir contribuer ! Ce projet vise à fournir un moteur RAG
modulaire et accessible à l'échelle africaine, et toute contribution —
code, documentation, tests, traduction, issue bien décrite — est la
bienvenue.

En participant, tu acceptes de respecter notre [Code de conduite](CODE_OF_CONDUCT.md).

## Avant de commencer

- Regarde les [issues ouvertes](../../issues), en particulier celles
  labellisées `good first issue` si c'est ta première contribution.
- Si tu veux proposer une fonctionnalité ou un changement significatif,
  ouvre d'abord une issue pour en discuter avant d'écrire du code — ça évite
  le travail perdu si la direction ne convient pas.
- Si une issue existe déjà, indique dans un commentaire que tu la prends en
  charge pour éviter que deux personnes travaillent dessus en parallèle.

## Mise en place de l'environnement de développement

### Backend (Python / FastAPI)

```bash
cd backend
uv sync              # installe les dépendances, y compris les outils de dev
cd ..
uv run --project backend pre-commit install   # active les hooks de pre-commit (voir plus bas)
```

Lance l'API en local :

```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

### Frontend (React)

```bash
cd frontend/rag-afrique-hub
npm install
npm run dev
```

## Qualité de code

### Lint et formatage (backend)

Le projet utilise [ruff](https://docs.astral.sh/ruff/) pour le lint et le
formatage du code Python.

```bash
cd backend
uv run ruff check .      # lint
uv run ruff format .     # formatage
```

### Lint (frontend)

```bash
cd frontend/rag-afrique-hub
npm run lint
```

### Pre-commit hooks

Des hooks [pre-commit](https://pre-commit.com/) sont configurés à la racine
du repo (`.pre-commit-config.yaml`) pour éviter de committer des fichiers
indésirables (`__pycache__`, `.DS_Store`, gros fichiers, conflits de merge
non résolus) et pour lancer `ruff` automatiquement. Installe-les une fois :

```bash
uv run --project backend pre-commit install
```

### Tests

```bash
cd backend
uv run pytest src/tests/ -v
```

Toute nouvelle fonctionnalité ou correction de bug dans le backend doit être
accompagnée d'un test. Les tests utilisent `dependency_overrides` pour mocker
le pipeline — aucune clé API réelle n'est nécessaire pour les exécuter.

## Convention de commits

Les messages de commit suivent, autant que possible, le format
[Conventional Commits](https://www.conventionalcommits.org/) :

```text
<type>(<scope optionnel>): <description courte>
```

Types courants : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.

Exemples :

```text
fix(orchestrator): corrige la clé de filtre utilisée par delete_document
feat(loaders): ajoute le support des fichiers .docx
docs: met à jour le README avec le mode hybrid
```

## Processus de Pull Request

1. Fork le repo (ou crée une branche si tu as les droits d'écriture).
2. Crée une branche depuis `main` : `git checkout -b feat/ma-fonctionnalite`.
3. Fais tes changements, avec des commits clairs.
4. Vérifie que les tests et le lint passent en local.
5. Ouvre une Pull Request vers `main` en remplissant le
   [template de PR](.github/PULL_REQUEST_TEMPLATE.md).
6. La CI (lint + tests) doit passer au vert avant la review.
7. Un mainteneur review et merge une fois la PR approuvée.

## Style et conventions du projet

- Dossiers Python en minuscules (`chunkers`, `embedders`, `loaders`,
  `retrieval`, etc.), un module par composant.
- Chaque nouveau composant (embedder, loader, chunker, vector store, llm...)
  doit implémenter l'interface abstraite correspondante dans
  `backend/src/core/interfaces.py` et être enregistré dans
  `backend/src/implementations/__init__.py` — voir la section
  [Ajouter un composant personnalisé](README.md#ajouter-un-composant-personnalisé)
  du README.
- Pas de clé API ou secret en dur dans le code : utilise les variables
  d'environnement documentées dans `.env.example`.

## Questions

Pour toute question, ouvre une [discussion ou une issue](../../issues).
