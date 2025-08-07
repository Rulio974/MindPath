# MindPath - Moteur de recherche sémantique pour questionnaires de sécurité

## 📋 Vue d'ensemble

MindPath est un système de recherche sémantique avancé conçu pour interroger des bases de données de questionnaires de sécurité. Le projet est architecturé en **3 modules indépendants** déployés sur **3 serveurs distincts** :

- **`embeddings/`** : Serveur de calcul et génération d'embeddings
- **`backend/`** : Serveur API avec authentification et recherche
- **`frontend/`** : Interface utilisateur web (à développer)

## 🏗️ Architecture multi-serveurs

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Serveur 1     │    │   Serveur 2     │    │   Serveur 3     │
│  embeddings/    │    │    backend/     │    │   frontend/     │
│                 │    │                 │    │                 │
│ • Calcul        │    │ • API REST      │    │ • Interface     │
│ • Génération    │    │ • Auth          │    │   utilisateur   │
│ • Stockage      │    │ • Recherche     │    │ • Dashboard     │
│ • Download API  │    │ • Gestion users │    │ • Formulaires   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Fonctionnalités principales

### Recherche sémantique
- **Multilingue** : Support français et anglais
- **Pondération temporelle** : Prise en compte de l'année des données
- **Re-ranking** : Amélioration des résultats avec cross-encoder
- **Détection automatique** de la langue des requêtes

### Authentification et gestion des utilisateurs
- **Tokens API** : Authentification simplifiée par tokens uniques
- **Rôles** : Administrateurs et utilisateurs standards
- **Gestion complète** : CRUD utilisateurs, régénération de tokens
- **Logs de recherche** : Traçabilité des requêtes

### Interface d'administration
- **Dashboard web** : Gestion des utilisateurs et statistiques
- **API REST** : Endpoints complets pour l'intégration
- **Documentation interactive** : Swagger/OpenAPI

## 📁 Structure du projet

```
MindPath/
├── embeddings/                    # Serveur 1 - Calcul d'embeddings
│   ├── data/                     # Données sources (JSON)
│   │   ├── fr/                   # Données françaises
│   │   └── en/                   # Données anglaises
│   ├── embeddings/               # Fichiers générés
│   │   ├── fr/                   # Embeddings français
│   │   │   ├── embeddings.npy    # Vecteurs d'embeddings
│   │   │   ├── faiss_index_flat.idx  # Index FAISS
│   │   │   ├── metadata.json     # Métadonnées JSON
│   │   │   └── metadata.pkl      # Métadonnées pickle
│   │   └── en/                   # Embeddings anglais
│   ├── main.py                   # Point d'entrée principal
│   ├── embedding_calculator.py   # Logique de calcul
│   ├── embedding_loader.py       # Chargement des embeddings
│   ├── download_api.py           # API de téléchargement
│   └── requirements.txt          # Dépendances
│
├── backend/                      # Serveur 2 - API et authentification
│   ├── src/                      # Code source
│   │   ├── auth/                 # Module d'authentification
│   │   │   ├── models.py         # Modèles SQLAlchemy
│   │   │   ├── schemas.py        # Schémas Pydantic
│   │   │   ├── crud.py           # Opérations base de données
│   │   │   ├── dependencies.py   # Dépendances FastAPI
│   │   │   ├── routes.py         # Routes d'authentification
│   │   │   ├── security.py       # Logique de sécurité
│   │   │   └── database.py       # Configuration DB
│   │   ├── api.py                # Application FastAPI principale
│   │   ├── admin.py              # Interface d'administration
│   │   ├── cli.py                # Interface ligne de commande
│   │   ├── utils.py              # Utilitaires (détection langue)
│   │   └── embedding_loader.py   # Chargement des embeddings
│   ├── embeddings/               # Embeddings copiés depuis serveur 1
│   │   ├── fr/                   # Fichiers français
│   │   └── en/                   # Fichiers anglais
│   ├── templates/                # Templates HTML
│   ├── main.py                   # Point d'entrée principal
│   ├── manage_users.py           # Script de gestion utilisateurs
│   ├── init_auth.py              # Initialisation base de données
│   ├── requirements.txt          # Dépendances
│   └── semantic_search.db        # Base de données SQLite
│
├── frontend/                     # Serveur 3 - Interface utilisateur
│   └── (à développer)            # Interface web future
│
├── .gitignore                    # Fichiers ignorés par Git
└── README.md                     # Cette documentation
```

## 🚀 Déploiement multi-serveurs

### Serveur 1 - Embeddings (Calcul)

**Objectif** : Calculer et générer les embeddings sémantiques

```bash
# Installation
cd embeddings/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Calcul des embeddings
python3 main.py

# API de téléchargement (optionnel)
python3 download_api.py
```

**Fichiers générés** :
- `embeddings/fr/` : Embeddings français
- `embeddings/en/` : Embeddings anglais
- `calculation_summary.json` : Résumé du calcul

### Serveur 2 - Backend (API)

**Objectif** : Exposer l'API avec authentification et recherche

```bash
# Installation
cd backend/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copier les embeddings depuis le serveur 1
mkdir -p embeddings/
# (copie manuelle des fichiers depuis serveur 1)

# Initialiser la base de données
python3 init_auth.py

# Lancer l'API
python3 main.py --mode api
```

**Modes disponibles** :
- `--mode api` : API complète avec recherche
- `--mode test-auth` : Test authentification seulement
- `--mode cli` : Interface ligne de commande

### Serveur 3 - Frontend (Interface)

**Objectif** : Interface utilisateur web (à développer)

```bash
# (Développement futur)
cd frontend/
# Interface utilisateur
```

## 🔧 Configuration technique

### Modèles utilisés

**Embeddings** :
- `paraphrase-multilingual-MiniLM-L12-v2` : Modèle multilingue Sentence Transformers
- **Dimensions** : 384
- **Langues** : Français, Anglais
- **Normalisation** : L2

**Index FAISS** :
- **Type** : Flat (recherche exacte)
- **Métrique** : Distance cosinus
- **Optimisation** : Pour la précision

### Base de données

**SQLite** : `semantic_search.db`

**Tables** :
```sql
-- Utilisateurs
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    api_token VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at DATETIME,
    updated_at DATETIME
);

-- Logs de recherche
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    query TEXT,
    language VARCHAR(10),
    results_count INTEGER,
    response_time INTEGER,
    created_at DATETIME
);
```

### Authentification

**Système** : Tokens API uniques
- **Génération** : `secrets.token_urlsafe(32)`
- **Stockage** : Base de données SQLite
- **Validation** : À chaque requête API
- **Révocation** : Régénération de token

**Types d'utilisateurs** :
- **Administrateurs** (`is_admin: true`) : Accès complet
- **Utilisateurs** (`is_admin: false`) : Recherche seulement

## 📡 API REST

### Endpoints principaux

#### Authentification
```
POST /auth/verify-token     # Vérifier un token
GET  /auth/me              # Infos utilisateur actuel
PUT  /auth/me              # Modifier son profil
POST /auth/regenerate-token # Régénérer son token
```

#### Gestion des utilisateurs (Admin)
```
GET    /users/                    # Lister tous les utilisateurs
POST   /users/                    # Créer un utilisateur
GET    /users/{id}                # Voir un utilisateur
PUT    /users/{id}                # Modifier un utilisateur
DELETE /users/{id}                # Supprimer un utilisateur
POST   /users/{id}/regenerate-token # Régénérer un token
```

#### Recherche
```
POST /search              # Recherche authentifiée
POST /search/public       # Recherche publique (optionnel)
```

#### Administration
```
GET /admin/               # Dashboard web
GET /admin/stats          # Statistiques globales
GET /stats                # Statistiques utilisateur
```

#### Utilitaires
```
GET /health               # État de l'API
GET /docs                 # Documentation Swagger
```

### Exemples d'utilisation

#### Recherche sémantique
```bash
curl -X POST "http://server2:8000/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "question": "sécurité informatique",
    "top_k": 5
  }'
```

#### Créer un utilisateur
```bash
curl -X POST "http://server2:8000/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "full_name": "Nouveau Utilisateur",
    "is_admin": false
  }'
```

## 🛠️ Outils de gestion

### Script de gestion des utilisateurs

```bash
cd backend/
python3 manage_users.py
```

**Fonctionnalités** :
- Lister tous les utilisateurs
- Afficher les tokens
- Créer/modifier/supprimer des utilisateurs
- Régénérer des tokens

### Interface web d'administration

```
http://server2:8000/admin/
```

**Fonctionnalités** :
- Dashboard avec statistiques
- Gestion des utilisateurs
- Interface graphique complète

## 🔒 Sécurité

### Authentification
- **Tokens uniques** par utilisateur
- **Validation** à chaque requête
- **Révocation** par régénération
- **Pas de mots de passe** (simplification)

### Autorisation
- **Rôles** : Admin vs Utilisateur
- **Endpoints protégés** par rôles
- **Logs** de toutes les recherches

### Données
- **Base SQLite** locale
- **Tokens sécurisés** (32 caractères aléatoires)
- **Validation** des entrées (Pydantic)

## 📊 Monitoring et logs

### Logs de recherche
- **Requête** : Texte de la recherche
- **Langue** : Détectée automatiquement
- **Résultats** : Nombre de résultats
- **Performance** : Temps de réponse
- **Utilisateur** : Qui a fait la recherche

### Statistiques
- **Par utilisateur** : Historique personnel
- **Globales** : Statistiques système (admin)
- **Performance** : Temps de réponse moyens

## 🔄 Workflow de déploiement

### 1. Serveur Embeddings
```bash
# Calculer les embeddings
python3 main.py

# Vérifier les fichiers générés
ls -la embeddings/fr/
ls -la embeddings/en/
```

### 2. Serveur Backend
```bash
# Copier les embeddings
cp -r ../embeddings/fr embeddings/
cp -r ../embeddings/en embeddings/

# Initialiser la DB
python3 init_auth.py

# Lancer l'API
python3 main.py --mode api
```

### 3. Tests
```bash
# Test authentification
curl -X GET "http://server2:8000/health"

# Test recherche
curl -X POST "http://server2:8000/search" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"question": "test"}'
```

## 🐛 Dépannage

### Problèmes courants

#### Embeddings non trouvés
```
❌ Erreur lors du chargement des embeddings
```
**Solution** : Vérifier que les fichiers sont copiés dans `backend/embeddings/`

#### Module non trouvé
```
ModuleNotFoundError: No module named 'embedding_loader'
```
**Solution** : Vérifier que `embedding_loader.py` est dans `backend/src/`

#### Token invalide
```
401 Unauthorized
```
**Solution** : Régénérer le token avec `/users/{id}/regenerate-token`

#### Base de données
```
sqlite3.OperationalError: no such table
```
**Solution** : Exécuter `python3 init_auth.py`

### Logs utiles

```bash
# Logs du serveur
tail -f /var/log/mindpath/backend.log

# Base de données
sqlite3 semantic_search.db ".tables"

# Vérifier les embeddings
ls -la backend/embeddings/fr/
```

## 📈 Évolutions futures

### Fonctionnalités prévues
- **Interface web** complète (frontend/)
- **Plus de langues** (espagnol, allemand)
- **Index FAISS avancés** (IVF, HNSW)
- **Cache Redis** pour les performances
- **API GraphQL** alternative
- **Webhooks** pour les notifications

### Optimisations
- **Compression** des embeddings
- **Index quantifiés** pour réduire la taille
- **Load balancing** pour l'API
- **Monitoring** avancé (Prometheus/Grafana)

## 📞 Support

### Documentation
- **API** : `http://server2:8000/docs`
- **Admin** : `http://server2:8000/admin/`

### Commandes utiles
```bash
# État du système
curl http://server2:8000/health

# Statistiques
curl -H "Authorization: Bearer TOKEN" http://server2:8000/stats

# Gestion utilisateurs
cd backend && python3 manage_users.py
```

---

**MindPath** - Recherche sémantique intelligente pour la sécurité informatique 