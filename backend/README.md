# Moteur de recherche sémantique

**Plus d'informations dans le Wiki**

## Sommaire
- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Historique des développements](#historique-des-développements)
- [Installation](#installation)
  - [Prérequis](#prérequis)
  - [Étapes d'installation](#étapes-dinstallation)
- [Docker](#Docker)
- [Utilisation](#utilisation)
  - [Mode CLI](#mode-cli)
  - [Mode API (FastAPI)](#mode-api-fastapi)
- [Intégration du module Excel](#intégration-du-module-excel)
- [Structure du projet](#structure-du-projet)
- [Format des fichiers JSON](#format-des-fichiers-json)
- [Paramètres](#paramètres)
- [Configuration Matérielle](#configuration-matérielle)
- [Roadmap et Prochaines Étapes](#roadmap-et-prochaines-étapes)


## Description

Moteur de recherche sémantique permettant d'extraire les questions et réponses les plus pertinentes à partir d'un Dataset de questionnaires de sécurité, PSSI interne, CGS et PAS.

Le projet repose sur FAISS pour l'indexation vectorielle et Sentence Transformers pour la représentation des questions sous forme d'embeddings. Un modèle de re-ranking (cross-encoder) améliore la pertinence des résultats. Il est disponible en mode CLI et via une API REST (FastAPI).

## Fonctionnalités

- Recherche sémantique sur le dataset.
- Support multilingue (Français et Anglais) avec détection automatique.
- Indexation rapide (relativement légère) avec FAISS.
- Interface CLI et API REST pour une intégration dans un module excel.
- Re-ranking avec Cross-Encoder pour amélioration des résultats.
- **🔐 Système d'authentification JWT complet** avec gestion des utilisateurs et rôles.
- **📊 Logs et statistiques** de recherche par utilisateur.
- **🛡️ Sécurité renforcée** avec validation des mots de passe et tokens.
- **👥 Gestion multi-utilisateurs** avec rôles (admin, user, viewer).

### Pipeline de Traitement

Le pipeline commence par le chargement et le parsing des documents JSON issus des répertoires `data/fr` et `data/en`. Ces fichiers contiennent des enregistrements avec des métadonnées (entreprise, date extraite en année) ainsi que des champs textuels (question, réponse, commentaire).

1. **Extraction et Parsing** : Lecture des fichiers JSON et extraction des données pertinentes.
2. **Encodage Sémantique** : Conversion des questions en embeddings denses via Sentence Transformer.
3. **Normalisation** : Normalisation des embeddings pour utilisation avec FAISS (produit scalaire en tant que mesure de similarité).
4. **Indexation FAISS** : Stockage des embeddings indexés pour des recherches optimisées.
5. **Interrogation du Système** :
   - Détection de la langue de la requête via langdetect.
   - Conversion de la requête en embedding.
   - Recherche des questions les plus proches dans FAISS.
6. **Re-ranking (optionnel)** : Ré-ordonnancement des résultats avec un cross-encoder.
7. **Renvoi des Résultats** :
   - Interface en ligne de commande.
   - API REST sous FastAPI.
   - Fourniture des résultats enrichis de métadonnées et d'un score de similarité.


## Installation

### Prérequis

- Python 3.8+
- pip installé
- Environnement virtuel recommandé (`venv` recommandé)

### Étapes d'installation

#### 🚀 Installation automatique (recommandée)

```bash
# 1. Cloner le dépôt
git clone <repository-url>
cd test_embedding

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows

# 3. Lancer l'installation automatique
python install.py
```

#### 🔧 Installation manuelle

1. Cloner le dépôt

2. Créer et activer un environnement virtuel
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux / macOS
   venv\Scripts\activate     # Windows
   ```

3. Installer les dépendances

   **Pour CPU (par défaut) :**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Pour GPU (si vous avez NVIDIA CUDA) :**
   ```bash
   pip install -r requirements-gpu.txt
   ```

4. **🔐 Initialiser l'authentification**
   ```bash
   python init_auth.py
   ```
   
   Choisissez l'option 1 pour initialiser la base de données avec les données par défaut.

5. Vérifier l'installation
   ```bash
   python main.py --help
   ```

#### 🩺 Dépannage

Si vous rencontrez des problèmes d'installation, consultez :
- **[Guide d'installation détaillé](install_guide.md)** pour les problèmes courants
- **[Documentation d'authentification](AUTHENTICATION.md)** pour la configuration

## Utilisation

### Mode CLI

Lancer une recherche en ligne de commande :

```bash
python main.py --mode cli --data_dir data --top_k 5
```

Entrer une question directement dans la console pour obtenir les résultats.

### Mode API (FastAPI)

Démarrer le serveur API :

```bash
python main.py --mode api --data_dir data --top_k 5
```

L'API est accessible à l'adresse :

```bash
http://localhost:8000
```

**🔐 Nouvelle version avec authentification :**

1. **Connexion** :
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

2. **Recherche authentifiée** :
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Chiffrez vous vos disques ?", "top_k": 5}'
```

3. **Recherche publique** (sans authentification) :
```bash
curl -X POST "http://localhost:8000/search/public" \
  -H "Content-Type: application/json" \
  -d '{"question": "Chiffrez vous vos disques ?", "top_k": 5}'
```

**📚 Documentation interactive** : `http://localhost:8000/docs`

**👤 Compte par défaut** : `admin` / `admin123`

Réponse JSON :

```json
{
    "results": [
        {
            "entreprise": "TENACY",
            "question": "Chiffrez vous vos disques ?",
            "reponse": "OUI",
            "commentaire": "Nous utilisons AES-256 pour chiffrer nos disques.",
            "annee": "2025",
            "score": 0.87
        }
    ],
    "metadata": {
        "query": "Chiffrez vous vos disques ?",
        "language": "fr",
        "results_count": 1,
        "response_time_ms": 45,
        "user_id": 1
    }
}
```

## 🔐 Authentification et sécurité

### Système de rôles

- **Admin** : Accès complet (gestion utilisateurs, statistiques globales)
- **User** : Recherche et gestion de profil
- **Viewer** : Accès en lecture seule

### Endpoints sécurisés

| Endpoint | Description | Auth requise |
|----------|-------------|--------------|
| `POST /auth/login` | Connexion | ❌ |
| `POST /search` | Recherche authentifiée | ✅ |
| `POST /search/public` | Recherche publique | ❌ |
| `GET /auth/me` | Profil utilisateur | ✅ |
| `GET /users` | Gestion utilisateurs | ✅ (Admin) |
| `GET /stats` | Statistiques | ✅ |

### Configuration sécurisée

Créez un fichier `.env` basé sur `env.example` :

```bash
SECRET_KEY=your-very-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./semantic_search.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**📖 Documentation complète** : [AUTHENTICATION.md](./AUTHENTICATION.md)

## Docker

1. Build du container :
```bash
sudo docker build .
```

2. Vérifier le build :
```bash
sudo docker images
```

3. Lancer le container :
```bash
sudo docker run -d -p 8000:8000 --name moteur-semantique <IMAGE ID>
```

4. Vérifier les logs :
```bash
sudo docker logs moteur-semantique
```

## Intégration du module Excel (Windows)

### Installation

1. Installer les dépendances du module :
   ```bash
   npm install
   ```

2. Démarrer le serveur du module :
   ```bash
   npm start
   ```

3. Placer le fichier `manifest.xml` dans un dossier accessible (qui ne demande pas de permissions d'administrateur).

4. Ouvrir Excel et ajouter le module :
   - Aller dans **Insertion** > **Compléments** > **Compléments Office**.
   - Cliquer sur **Ajouter un complément** et sélectionner `manifest.xml`.
   - Le module apparaîtra dans le ruban.

5. Afficher le module dans Excel :
   - Aller dans **Compléments** et activer le module pour interagir avec l'API.

## Structure du projet

```
Moteur-semantique-questionnaire-securite
├── data/                    # Données d'entrée
│   ├── fr/                 # Fichiers JSON en français
│   └── en/                 # Fichiers JSON en anglais
├── src/                    # Code source Python
│   ├── __init__.py        # Initialisation du package
│   ├── api.py             # Endpoints FastAPI
│   ├── cli.py             # Interface en ligne de commande
│   ├── engine.py          # Moteur de recherche sémantique
│   └── utils.py           # Fonctions utilitaires
├── tests/                  # Tests unitaires et d'intégration
├── module/                 # Module Excel
│   ├── node_modules/      # Dépendances Node.js
│   ├── manifest.xml       # Configuration du module Office
│   ├── server.js         # Serveur proxy pour Excel
│   ├── taskpane.html     # Interface utilisateur du module
│   ├── taskpane.css      # Styles de l'interface
│   └── taskpane.js       # Logique du module
├── .gitignore            # Fichiers ignorés par Git
├── Dockerfile            # Configuration Docker
├── main.py              # Point d'entrée principal (FastAPI)
├── requirements.txt     # Dépendances Python
└── README.md           # Documentation principale
```

## Format des fichiers JSON

Les fichiers JSON situés dans `data/fr` et `data/en` doivent respecter la structure suivante :

```json
{
    "date": "2025-01-01",
    "entreprise": "TENACY",
    "data": [
        {
            "question": "Chiffrez vous vos disques?",
            "reponse": "OUI",
            "commentaire": "Nous utilisons AES-256 pour chiffrer nos disques."
        }
    ]
}
```

## Paramètres

| Argument    | Description |
|-------------|------------|
| `--mode`    | Mode d'exécution : `cli` (ligne de commande) ou `api` (serveur FastAPI) |
| `--data_dir` | Dossier contenant le dataset (`data/` par défaut) |
| `--top_k`   | Nombre de résultats retournés par requête (par défaut : `5`) |
| `--rerank`  | Active le re-ranking avec un Cross-Encoder pour améliorer la précision |
| `--year_weighted` | Active la pondération par l'année (par défaut : `False`) |
| `--embedding_model` | Modèle d'embedding à utiliser (par défaut : `all-MiniLM-L6-v2`) |
| `--crossencoder_model` | Modèle de cross-encoder à utiliser (par défaut : `cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| `--batch_size` | Taille des batchs pour la vectorisation (par défaut : `64`) |


## Configuration Matérielle actuelle

| Composant  | Spécifications |
|------------|----------------|
| CPU        | Intel Xeon E5-2690 v4 @ 2.60GHz (6 cœurs) |
| RAM        | 112 Go |
| GPU        | NVIDIA Tesla A100 |
| Cache L1   | 192 KiB (x6) |
| Cache L2   | 1.5 MiB (x6) |
| Cache L3   | 35 MiB |

## Roadmap et Prochaines Étapes

| **Étape**                                      | **Description / Objectif**                                                                                                                                                                |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Benchmark (performances)**                   | Évaluer les performances du moteur (temps de réponse, utilisation des ressources, scalabilité) lors de l'indexation et de la recherche.                                                    |
| **Benchmark (résultats)**                        | Comparer la qualité des résultats (précision, rappel, F1-score) afin de valider l'efficacité du scoring et du re-ranking sur des jeux de données tests.                                   |
| **Ajout d'une échelle de réponse**             | Intégrer une échelle de réponse customisée (Actuellement OUI, NON, N/A, PARTIEL) et adaptée au questionnaire.         |
| **Génération d'un commentaire adapté**         | Développer un module capable de générer automatiquement un commentaire contextualisé en fonction de la question posée, potentiellement en exploitant des techniques de NLP fine-tuné cyber ou LLM (Mistral / DeepSeek / Llama).  |
| **Statistiques sur le dataset**           | Déterminer via un clusturing plus précis les questions qui reviennent le plus souvent pour améliorer la prédiction.                                                                              |
| Trouver un nom *sexy*  | PASsificateur, tour de PAS PAS, PAS décisive, PAS partout


## Historique des développements

### 🔧 Résolution du problème de spinner (Interface d'administration)

**Problème initial :**
- Spinner tournant en boucle sur la page `/admin/users`
- Appels AJAX échouant à cause de problèmes d'authentification JWT
- Interface utilisateur non fonctionnelle

**Solutions apportées :**
1. **Suppression des appels AJAX problématiques** dans `templates/admin/users.html`
2. **Intégration côté serveur** : Récupération directe des données via `UserCRUD.get_users(db)`
3. **Correction des imports** : `UserCRUD.assign_role` au lieu de `UserCRUD.add_role_to_user`
4. **Génération HTML côté serveur** : Tableau des utilisateurs rendu directement avec les données

**Résultat :** Interface d'administration fonctionnelle avec affichage correct des utilisateurs.

### 🎨 Amélioration du design (Interface moderne)

**Objectif :** Création d'un design plus sobre et moderne pour l'interface d'administration.

**Améliorations apportées :**
1. **Avatars cohérents** : Style uniforme avec fond gris `#6c757d` (cohérent avec la sidebar)
2. **Tableau modernisé** :
   - Suppression des bordures
   - Espacement amélioré
   - Effets hover élégants
3. **Badges modernisés** : Coins arrondis et couleurs contemporaines
4. **Boutons stylisés** : Style outline avec animations hover
5. **Typographie améliorée** : Headers en majuscules pour plus de caractère

**Résultat :** Interface d'administration avec un design moderne et professionnel.

### 👥 Développement de la fonctionnalité "Nouvel utilisateur"

**Objectif :** Rendre fonctionnel le bouton "Nouvel utilisateur" pour créer de nouveaux comptes.

**Développements réalisés :**

#### 1. Création du modal d'ajout d'utilisateur
- **Formulaire complet** avec validation côté client
- **Champs disponibles** :
  - Nom d'utilisateur (requis)
  - Email (requis avec validation)
  - Nom complet (optionnel)
  - Mot de passe (requis avec validation robuste)
  - Cases à cocher : Compte actif, Administrateur
- **Validation mot de passe** : 8 caractères minimum, majuscule, minuscule, chiffre

#### 2. Correction de l'endpoint backend
- **Endpoint utilisé** : `POST /admin/users/create`
- **Améliorations** :
  - Support du champ `full_name` (optionnel)
  - Gestion des erreurs de validation
  - Retour JSON structuré pour les erreurs

#### 3. Tentatives de résolution JavaScript
**Problème persistant** : Le bouton "Nouvel utilisateur" ne déclenche pas le modal mais provoque une navigation.

**Approches testées :**
1. **Première approche** : `onclick="showCreateUserModal()"` directement dans le HTML
2. **Deuxième approche** : `addEventListener` avec `DOMContentLoaded`
3. **Troisième approche** : `window.onload` avec `btn.onclick` (méthode basique)

**Diagnostic effectué** :
- Vérification de l'existence des éléments DOM
- Ajout de logs de debug
- Test de différentes méthodes d'attachement d'événements

**Problème non résolu** : Le clic sur le bouton provoque une navigation au lieu d'ouvrir le modal, suggérant un problème de routage ou de comportement par défaut.

### 🗂️ Fichiers de test supprimés

**Nettoyage du projet :**
- `test_admin.py` : Fichier de test temporaire
- `test_admin_login.py` : Test d'authentification admin
- `debug_login.py` : Script de debug pour l'authentification
- `templates/admin/test.html` : Template de test

**Raison :** Suppression des fichiers temporaires créés pendant le développement et debug.

### 📊 État actuel du projet

**Fonctionnalités opérationnelles :**
- ✅ Moteur de recherche sémantique complet
- ✅ Système d'authentification JWT
- ✅ Interface d'administration avec design moderne
- ✅ Gestion des utilisateurs (affichage, rôles)
- ✅ Logs et statistiques
- ✅ API REST documentée

**Problèmes en cours :**
- ❌ Bouton "Nouvel utilisateur" ne fonctionne pas (navigation au lieu de modal)
- ❌ Création d'utilisateurs via interface web non fonctionnelle

**Prochaines étapes suggérées :**
1. Investigation approfondie du problème de routage JavaScript
2. Alternative : Création d'une page dédiée pour l'ajout d'utilisateurs
3. Tests complets de l'interface d'administration
4. Documentation des procédures d'administration




