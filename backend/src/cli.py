#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.utils import detect_language

def run_cli_mode(engines, top_k, year_weighted):
    """
    Lance le mode CLI interactif pour effectuer des recherches.
    """
    print("Tapez 'exit' ou 'quit' pour arrêter.")
    while True:
        query = input("\nVotre question : ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        if not query:
            continue
        lang = detect_language(query)
        print(f"Langue détectée : {lang}")
        engine = engines.get(lang, engines.get("en"))
        results = engine.search(query, top_k=top_k, rerank=False, year_weighted=year_weighted)
        print("\n--- Résultats ---")
        for i, res in enumerate(results):
            print(f"\nRésultat {i+1}:")
            print(f"Entreprise  : {res['entreprise']}")
            print(f"Question    : {res['question']}")
            if res.get("reponse"):
                print(f"Reponse     : {res['reponse']}")
            if res.get("commentaire"):
                print(f"Commentaire : {res['commentaire']}")
            else:
                print("Commentaire : Aucun commentaire")
            print(f"Annee       : {res['annee']}")
            print(f"Score       : {res['score']:.4f}")
