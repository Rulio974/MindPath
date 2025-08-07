#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from langdetect import detect_langs

def detect_language(text):
    """
    Détecte la langue d'un texte.
    """
    try:
        langs = detect_langs(text)
        best = max(langs, key=lambda x: x.prob)
        if best.lang.startswith("fr"):
            return "fr"
        elif best.lang.startswith("en"):
            return "en"
        else:
            return "en"
    except:
        return "en"

def load_all_engines(embeddings_dir, embedding_model=None, crossencoder_model=None, batch_size=64):
    """
    Charge tous les moteurs d'embeddings pré-calculés depuis le dossier embeddings.
    """
    print(f"\n--- Chargement des embeddings depuis {embeddings_dir} ---")
    
    try:
        # Import local depuis le même dossier
        from .embedding_loader import EmbeddingLoader
        
        loader = EmbeddingLoader(embeddings_dir)
        engines = loader.load_all_engines()
        
        print(f"✅ {len(engines)} moteurs chargés avec succès")
        for lang, engine in engines.items():
            print(f"   - {lang}: {len(engine['questions'])} questions")
        
        return engines
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement des embeddings: {e}")
        print("💡 Assurez-vous d'avoir calculé les embeddings avec le script embeddings/main.py")
        print(f"   Les fichiers doivent être dans: {embeddings_dir}")
        return {}

