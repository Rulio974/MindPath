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
    print("🔐 Mode test d'authentification")
    print("   Le serveur démarre sans charger les embeddings")
    print("   Utilisez curl pour tester l'authentification")
    print()
    
    # Initialiser la base de données
    from src.auth.database import init_db
    init_db()
    
    # Créer l'application FastAPI
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from src.auth.routes import auth_router, users_router
    from src.admin import admin_router
    
    app = FastAPI(
        title="Test Auth - Moteur de recherche sémantique",
        description="Mode test pour l'authentification par token",
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
        """Point d'entrée de l'API"""
        return {
            "message": "Mode test d'authentification - Moteur de recherche sémantique",
            "version": "3.0.0",
            "mode": "test-auth",
            "endpoints": {
                "auth": "/auth",
                "users": "/users", 
                "admin": "/admin",
                "docs": "/docs"
            }
        }

    @app.get("/health")
    async def health_check():
        """Vérification de l'état du serveur"""
        return {"status": "healthy", "mode": "test-auth"}

    # Démarrer le serveur
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def main():
    parser = argparse.ArgumentParser(
        description="Recherche sémantique dense pour FAQ / Q&R"
    )
    parser.add_argument("--embeddings_dir", type=str, default="embeddings", 
                       help="Répertoire contenant les embeddings pré-calculés")
    parser.add_argument("--top_k", type=int, default=5, help="Nombre de résultats à retourner")
    parser.add_argument("--mode", choices=["cli", "api", "test-auth"], default="api", 
                       help="Mode d'exécution : 'cli', 'api' ou 'test-auth'")
    parser.add_argument("--year_weighted", action="store_true", 
                       help="Activer le scoring pondéré par l'année")
    args = parser.parse_args()

    if args.mode == "test-auth":
        test_auth_mode()
        return

    # Charger les embeddings pré-calculés
    engines = load_all_engines(args.embeddings_dir)

    if args.mode == "cli":
        run_cli_mode(engines, args.top_k, args.year_weighted)
    else:
        run_api_mode(engines, args.top_k, args.year_weighted)

if __name__ == "__main__":
    main()
