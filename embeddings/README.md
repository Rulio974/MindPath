# Calcul des Embeddings

Ce dossier contient tous les scripts nécessaires pour calculer les embeddings et générer les fichiers nécessaires à la recherche sémantique.

## Structure

```
embeddings/
├── main.py                 # Script principal pour orchestrer le calcul
├── embedding_calculator.py # Classe pour calculer les embeddings
├── embedding_loader.py     # Classe pour charger les embeddings (utilisée par le backend)
├── requirements.txt        # Dépendances pour le calcul
└── README.md              # Ce fichier
```

## Installation

```bash
cd embeddings
pip install -r requirements.txt
```

## Utilisation

### Calcul des embeddings

```bash
# Calcul de base
python main.py --data-dir /path/to/json/files

# Avec options avancées
python main.py \
  --data-dir /path/to/json/files \
  --output-dir ./output \
  --embedding-model paraphrase-multilingual-MiniLM-L12-v2 \
  --batch-size 64 \
  --index-type HNSW \
  --languages fr en
```

### Options disponibles

- `--data-dir` : Dossier contenant les fichiers JSON (obligatoire)
- `--output-dir` : Dossier de sortie (défaut: dossier courant)
- `--embedding-model` : Modèle d'embedding (défaut: paraphrase-multilingual-MiniLM-L12-v2)
- `--batch-size` : Taille des batchs (défaut: 32)
- `--index-type` : Type d'index FAISS (Flat, IVF, HNSW) (défaut: Flat)
- `--languages` : Langues à traiter (défaut: fr en)

## Fichiers générés

Pour chaque langue, les scripts génèrent :

- `{lang}_embeddings.npy` : Vecteurs d'embeddings
- `{lang}_index.faiss` : Index FAISS
- `{lang}_metadata.pkl` : Métadonnées complètes
- `{lang}_metadata.json` : Métadonnées lisibles
- `calculation_summary.json` : Résumé global

## Types d'index FAISS

- **Flat** : Recherche exacte, plus lente mais plus précise
- **IVF** : Recherche approximative, bon compromis vitesse/précision
- **HNSW** : Recherche approximative, très rapide

## Intégration avec le backend

Le backend utilise `embedding_loader.py` pour charger les fichiers générés et exposer l'API de recherche sémantique.

## Exemple complet

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Calculer les embeddings
python main.py --data-dir ../data --output-dir ./output

# 3. Vérifier les fichiers générés
ls -la output/
```

## Notes

- Le calcul peut prendre du temps selon la taille des données
- Assurez-vous d'avoir suffisamment d'espace disque
- Les modèles sont téléchargés automatiquement au premier usage 