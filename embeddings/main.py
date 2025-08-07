#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script principal pour le calcul des embeddings
Génère les fichiers .npy, .faiss et metadata dans le dossier embeddings/
"""

import os
import sys
from pathlib import Path

# Ajouter le dossier embeddings au path
sys.path.append(str(Path(__file__).parent))

from embedding_calculator import EmbeddingCalculator

def main():
    print("🚀 Démarrage du calcul des embeddings")
    print("   Paramètres par défaut :")
    print("   - Dossier de données: data/")
    print("   - Dossier de sortie: embeddings/")
    print("   - Modèle: paraphrase-multilingual-MiniLM-L12-v2")
    print("   - Type d'index: Flat")
    print("   - Langues: fr, en")
    print()
    
    # Paramètres par défaut
    data_dir = "data"
    output_dir = "embeddings"
    embedding_model = "paraphrase-multilingual-MiniLM-L12-v2"
    batch_size = 32
    index_type = "Flat"
    languages = ["fr", "en"]
    
    # Vérifier que le dossier de données existe
    if not os.path.exists(data_dir):
        print(f"❌ Erreur: Le dossier {data_dir} n'existe pas")
        print(f"   Créez le dossier {data_dir} avec les sous-dossiers fr/ et en/")
        sys.exit(1)
    
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Initialiser le calculateur
        calculator = EmbeddingCalculator()
        
        # Traiter toutes les langues
        calculator.process_all_languages(data_dir, languages)
        
        print("✅ Calcul des embeddings terminé avec succès !")
        print(f"📁 Fichiers générés dans: {output_dir}")
        print()
        print("📋 Prochaines étapes :")
        print("   1. Copier les fichiers vers backend/embeddings/")
        print("   2. Lancer le backend avec: python main.py --mode api")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des embeddings: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 