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

def test_auth_mode():
    """Mode de test pour l'authentification sans charger les embeddings"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    from src.auth.database import init_db
    from src.auth.routes import auth_router, users_router
    from src.admin import admin_router
    
    # Initialiser la base de données
    init_db()
    
    app = FastAPI(
        title="Test Authentification",
        description="API de test pour l'authentification",
        version="3.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclure les routeurs d'authentification
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(admin_router)

    @app.get("/")
    async def root():
        return {
            "message": "Mode test authentification - Embeddings non chargés",
            "version": "3.0.0",
            "endpoints": {
                "admin": "/admin",
                "auth": "/auth",
                "users": "/users",
                "docs": "/docs"
            }
        }

    # Configuration du serveur
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Configuration HTTPS
    ssl_keyfile = os.getenv("SSL_KEYFILE", "certs/backend.key")
    ssl_certfile = os.getenv("SSL_CERTFILE", "certs/backend.crt")
    
    # Vérifier si les certificats SSL existent
    if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        print(f"🔒 Démarrage du serveur de test HTTPS sur {host}:{port}")
        print(f"📚 Documentation disponible sur https://{host}:{port}/docs")
        uvicorn.run(app, host=host, port=port, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
    else:
        print(f"⚠️  Certificats SSL non trouvés, démarrage en HTTP sur {host}:{port}")
        print(f"📚 Documentation disponible sur http://{host}:{port}/docs")
        uvicorn.run(app, host=host, port=port)

def main():
    parser = argparse.ArgumentParser(
        description="Recherche sémantique dense pour FAQ / Q&R"
    )
    parser.add_argument("--embeddings_dir", type=str, default="embeddings", help="Répertoire contenant les embeddings calculés")
    parser.add_argument("--top_k", type=int, default=5, help="Nombre de résultats à retourner")
    parser.add_argument("--mode", choices=["cli", "api", "test-auth"], default="cli", help="Mode d'exécution : 'cli', 'api' ou 'test-auth'")
    parser.add_argument("--rerank", action="store_true", help="Activer le re-ranking avec un cross-encoder")
    parser.add_argument("--year_weighted", action="store_true", help="Activer le scoring pondéré par l'année")
    parser.add_argument("--embedding_model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", help="Nom du modèle d'embedding")
    parser.add_argument("--crossencoder_model", type=str, default="cross-encoder/ms-marco-MiniLM-L-12-v2", help="Nom du modèle de cross-encoder pour le re-ranking")
    parser.add_argument("--batch_size", type=int, default=64, help="Taille des batchs pour la vectorisation")
    args = parser.parse_args()

    if args.mode == "test-auth":
        test_auth_mode()
        return

    engines = load_all_engines(
        args.embeddings_dir,
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

