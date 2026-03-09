# Répartition pour 6 personnes

## Vue globale par semaine

|      | Sem 1 | Sem 2 | Sem 3 |
|------|-------|-------|-------|
| **P1** | Auth + Rate limit | Async pipeline | Providers OpenAI/Anthropic |
| **P2** | Docker + Compose | CI/CD GitHub | Guide déploiement |
| **P3** | Persistance chat | Delete fichiers | Stats + polish UI |
| **P4** | Tests unitaires | Tests intégration | Pre-commit + lint |
| **P5** | README + Licence | CONTRIBUTING | Notebooks exemples |
| **P6** | Validation fichiers | Env check | Repo public setup |

---

# P1 — Backend Sécurité & Performance
**Auth · Rate limiting · Async pipeline · Providers**

| Sem | Tâches |
|-----|--------|
| 1 | Middleware auth par clé API sur `/query` et `/ingest` + rate limiting (slowapi) |
| 2 | Pipeline async avec `run_in_executor` pour ne plus bloquer l'event loop |
| 3 | Enregistrer OpenAI, Anthropic, Cohere → `hybrid.yaml` et `premium.yaml` fonctionnels |

---

# P2 — Infrastructure & DevOps
**Docker · CI/CD · Déploiement**

| Sem | Tâches |
|-----|--------|
| 1 | Dockerfile backend + frontend, `.dockerignore`, vérif builds |
| 2 | `docker-compose.yml` (backend + frontend + volume ChromaDB) + GitHub Actions (tests + lint sur PR) |
| 3 | Guide déploiement Railway / Fly.io / VPS + variables d'env production |

---

# P3 — Frontend
**Persistance · Gestion fichiers · Polish**

| Sem | Tâches |
|-----|--------|
| 1 | Persistance chat `localStorage` + variable `VITE_API_URL` pour build prod |
| 2 | UI suppression de fichiers indexés (+ endpoint `DELETE /ingest/{file}` avec P1) |
| 3 | Page stats (nb docs, nb requêtes) + badge modèle réellement utilisé + responsive mobile |

---

# P4 — Qualité & Tests
**Pytest · Intégration · Hooks**

| Sem | Tâches |
|-----|--------|
| 1 | Setup pytest + tests unitaires : loaders, chunkers, embedder, BM25 |
| 2 | Tests intégration : pipeline complet ingest → query → réponse |
| 3 | Tests routes API + pre-commit hooks (ruff, black, eslint) + couverture ≥ 70% |

---

# P5 — Documentation & Open Source
**README · CONTRIBUTING · Exemples**

| Sem | Tâches |
|-----|--------|
| 1 | LICENSE (MIT) + README production (install, usage, screenshots, architecture) |
| 2 | CONTRIBUTING.md + templates issues/PR GitHub + diagramme architecture |
| 3 | Notebooks d'exemples dans `/examples/` + FAQ |

---

# P6 — Setup Repo Public & Validation globale
**Fork propre · Variables d'env · QA**

| Sem | Tâches |
|-----|--------|
| 1 | Validation des variables d'env au démarrage (erreur claire si `MISTRAL_API_KEY` manquante) + validation MIME/taille fichiers |
| 2 | Créer et nettoyer le repo public (retirer configs partenaires, anonymiser) |
| 3 | QA end-to-end sur les 2 repos (`docker-compose up` → ingest → query → réponse) + rapport de bugs |

---

# Vue Swimlane

## Backend / DevOps / Frontend

|        | P1 Backend Sécu | P2 DevOps | P3 Frontend |
|--------|-----------------|-----------|-------------|
| **Sem 1** | Auth + Rate limit | Docker + `.dockerignore` | LocalStorage + `VITE_API_URL` |
| **Sem 2** | Pipeline async | docker-compose + GitHub Actions | Delete fichiers + endpoint DELETE |
| **Sem 3** | OpenAI / Anthropic / Cohere enregistrés | Guide déploiement | Stats + Badge + Mobile |

---

## Tests / Docs / Repo Public

|        | P4 Tests | P5 Docs | P6 Repo Public |
|--------|----------|---------|----------------|
| **Sem 1** | Setup + Unit (loaders, chunks) | LICENSE + README | Env check + validation MIME |
| **Sem 2** | Intégration pipeline | CONTRIBUTING + templates | Créer repo public (nettoyage) |
| **Sem 3** | API tests + pre-commit | Notebooks + FAQ | QA end-to-end 2 repos |

---

# Points de synchronisation équipe

| Moment | Quoi |
|--------|------|
| Fin sem 1 | P1 ↔ P3 : interface de l'endpoint DELETE pour les fichiers |
| Fin sem 1 | P2 ↔ P4 : Docker doit faire tourner les tests en CI |
| Fin sem 2 | P6 ↔ tous : review du repo public avant nettoyage final |
| Fin sem 3 | P6 QA valide que `docker-compose up` fonctionne sur les 2 repos |

---

## Rôle stratégique de P6

Le 6ème rôle (P6) est stratégique :

- Validation des env vars au démarrage  
- Validation MIME/taille fichiers  
- QA final  

C'est la personne qui joue le rôle de **testeur utilisateur** et s'assure que tout marche de bout en bout avant le lancement public.