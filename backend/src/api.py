#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
# Note: Imports HTML retirés - interface d'administration séparée
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv

# Configurer OpenMP pour éviter les conflits
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from src.utils import detect_language
from src.auth.database import get_db, init_db
from src.auth.models import User
from src.auth.dependencies import get_current_user, get_current_admin, get_current_admin_session, get_optional_user
from src.auth.routes import auth_router, users_router
from src.auth.crud import SearchLogCRUD
from src.auth.schemas import SearchLogCreate
# Note: Import admin_router retiré - interface d'administration séparée

# Charger les variables d'environnement
load_dotenv()

# Note: Configuration templates retirée - interface d'administration séparée

def run_api_mode(engines, top_k, year_weighted):
    """
    Lance l'API FastAPI pour servir les recherches avec authentification.
    """
    # Initialiser la base de données
    init_db()
    
    # Créer un loader pour les recherches
    from .embedding_loader import EmbeddingLoader
    loader = EmbeddingLoader()
    
    app = FastAPI(
        title="Moteur de recherche sémantique",
        description="API de recherche sémantique avec authentification pour questionnaires de sécurité",
        version="3.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://lesphinx.mindpath.fr", 
            "http://lesphinx.mindpath.fr",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://164.132.58.187",
            "file://"
        ], 
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Inclure les routeurs d'authentification et API
    app.include_router(auth_router)
    app.include_router(users_router)
    # Note: admin_router retiré - interface d'administration séparée

    @app.get("/")
    async def root():
        """Point d'entrée de l'API"""
        return {
            "message": "Moteur de recherche sémantique avec authentification",
            "version": "3.0.0",
            "endpoints": {
                "search": "/search",
                "auth": "/auth",
                "users": "/users",
                "docs": "/docs"
            }
        }

    # Note: Page de connexion retirée - interface d'administration séparée

    @app.post("/search")
    async def search_endpoint(
        request: Request,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Recherche sémantique (authentification requise)
        """
        start_time = time.time()
        
        data = await request.json()
        query = data.get("question", "")
        if not query:
            return {"error": "Aucune question fournie."}
        
        # Permet de spécifier top_k dans la requête
        top_k_req = data.get("top_k", top_k)
        lang = detect_language(query)
        engine = engines.get(lang, engines.get("en"))
        
        if not engine:
            return {"error": f"Aucun moteur disponible pour la langue {lang}"}
        
        results = loader.search(engine, query, top_k=top_k_req, year_weighted=year_weighted)
        
        # Calculer le temps de réponse
        response_time = int((time.time() - start_time) * 1000)  # en millisecondes
        
        # Logger la recherche
        try:
            log_data = SearchLogCreate(
                query=query,
                language=lang,
                results_count=len(results),
                response_time=response_time
            )
            SearchLogCRUD.create_search_log(db, current_user["user_id"], log_data)
        except Exception as e:
            print(f"Erreur lors du logging de la recherche : {e}")
        
        return jsonable_encoder({
            "results": results,
            "metadata": {
                "query": query,
                "language": lang,
                "results_count": len(results),
                "response_time_ms": response_time,
                "user_id": current_user["user_id"]
            }
        })

    @app.post("/search/public")
    async def search_public_endpoint(
        request: Request,
        current_user: Optional[dict] = Depends(get_optional_user),
        db: Session = Depends(get_db)
    ):
        """
        Recherche sémantique publique (authentification optionnelle)
        """
        start_time = time.time()
        
        data = await request.json()
        query = data.get("question", "")
        if not query:
            return {"error": "Aucune question fournie."}
        
        # Permet de spécifier top_k dans la requête
        top_k_req = data.get("top_k", top_k)
        lang = detect_language(query)
        engine = engines.get(lang, engines.get("en"))
        
        if not engine:
            return {"error": f"Aucun moteur disponible pour la langue {lang}"}
        
        results = loader.search(engine, query, top_k=top_k_req, year_weighted=year_weighted)
        
        # Calculer le temps de réponse
        response_time = int((time.time() - start_time) * 1000)  # en millisecondes
        
        # Logger la recherche (avec ou sans utilisateur)
        try:
            log_data = SearchLogCreate(
                query=query,
                language=lang,
                results_count=len(results),
                response_time=response_time
            )
            user_id = current_user["user_id"] if current_user else None
            SearchLogCRUD.create_search_log(db, user_id, log_data)
        except Exception as e:
            print(f"Erreur lors du logging de la recherche : {e}")
        
        return jsonable_encoder({
            "results": results,
            "metadata": {
                "query": query,
                "language": lang,
                "results_count": len(results),
                "response_time_ms": response_time,
                "authenticated": current_user is not None
            }
        })

    @app.get("/health")
    async def health_check():
        """Vérification de l'état de l'API"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "engines_loaded": len(engines),
            "available_languages": list(engines.keys())
        }

    @app.get("/stats")
    async def get_stats(
        current_user: dict = Depends(get_current_admin_session),
        db: Session = Depends(get_db)
    ):
        """Statistiques de recherche pour l'utilisateur actuel"""
        stats = SearchLogCRUD.get_search_statistics(db, current_user["id"])
        return stats

    # Note: Endpoint admin/stats retiré - interface d'administration séparée

    # Configuration du serveur
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Démarrage du serveur sur {host}:{port}")
    print(f"📚 Documentation disponible sur http://{host}:{port}/docs")
    print(f"🔐 Compte admin par défaut : admin / admin123")
    
    uvicorn.run(app, host=host, port=port)

