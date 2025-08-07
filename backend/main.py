#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse

# Configurer OpenMP pour éviter les conflits
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Charger le fichier .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from src.utils import load_all_engines
from src.cli import run_cli_mode
from src.api import run_api_mode

def main():
    parser = argparse.ArgumentParser(
        description="Recherche sémantique dense pour FAQ / Q&R (supporte data/fr et data/en)"
    )
    parser.add_argument("--data_dir", type=str, default="data", help="Répertoire contenant les sous-dossiers 'fr' et 'en'")
    parser.add_argument("--top_k", type=int, default=5, help="Nombre de résultats à retourner")
    parser.add_argument("--mode", choices=["cli", "api"], default="cli", help="Mode d'exécution : 'cli' ou 'api'")
    parser.add_argument("--rerank", action="store_true", help="Activer le re-ranking avec un cross-encoder")
    parser.add_argument("--year_weighted", action="store_true", help="Activer le scoring pondéré par l'année")
    parser.add_argument("--embedding_model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", help="Nom du modèle d'embedding")
    parser.add_argument("--crossencoder_model", type=str, default="cross-encoder/ms-marco-MiniLM-L-12-v2", help="Nom du modèle de cross-encoder pour le re-ranking")
    parser.add_argument("--batch_size", type=int, default=64, help="Taille des batchs pour la vectorisation")
    args = parser.parse_args()

    engines = load_all_engines(
        args.data_dir,
        args.embedding_model,
        crossencoder_model=args.crossencoder_model if args.rerank else None,
        batch_size=args.batch_size
    )

    if args.mode == "cli":
        run_cli_mode(engines, args.top_k, args.year_weighted)
    else:
        run_api_mode(engines, args.top_k, args.year_weighted)

if __name__ == "__main__":
    main()
