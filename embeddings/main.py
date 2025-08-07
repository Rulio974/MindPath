#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script principal pour le calcul des embeddings
Génère les fichiers .npy, .faiss et metadata dans le dossier embeddings/
"""

import argparse
import os
import sys
from pathlib import Path

# Ajouter le dossier embeddings au path
sys.path.append(str(Path(__file__).parent))

from embedding_calculator import EmbeddingCalculator

def main():
    parser = argparse.ArgumentParser(description="Calcul des embeddings pour la recherche sémantique")
    parser.add_argument("--data-dir", type=str, required=True, help="Dossier contenant les fichiers JSON")
    parser.add_argument("--output-dir", type=str, default=".", help="Dossier de sortie pour les embeddings")
    parser.add_argument("--embedding-model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", 
                       help="Modèle d'embedding à utiliser")
    parser.add_argument("--batch-size", type=int, default=32, help="Taille des batchs")
    parser.add_argument("--index-type", type=str, default="Flat", choices=["Flat", "IVF", "HNSW"], 
                       help="Type d'index FAISS")
    parser.add_argument("--languages", type=str, nargs="+", default=["fr", "en"], 
                       help="Langues à traiter")
    
    args = parser.parse_args()
    
    # Vérifier que le dossier de données existe
    if not os.path.exists(args.data_dir):
        print(f"❌ Erreur: Le dossier {args.data_dir} n'existe pas")
        sys.exit(1)
    
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("🚀 Démarrage du calcul des embeddings")
    print(f"   Dossier de données: {args.data_dir}")
    print(f"   Dossier de sortie: {args.output_dir}")
    print(f"   Modèle: {args.embedding_model}")
    print(f"   Type d'index: {args.index_type}")
    print(f"   Langues: {args.languages}")
    print()
    
    try:
        # Initialiser le calculateur
        calculator = EmbeddingCalculator(
            embedding_model=args.embedding_model,
            batch_size=args.batch_size,
            index_type=args.index_type
        )
        
        # Traiter toutes les langues
        calculator.process_all_languages(args.data_dir, args.output_dir, args.languages)
        
        print("✅ Calcul des embeddings terminé avec succès !")
        print(f"📁 Fichiers générés dans: {args.output_dir}")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des embeddings: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 