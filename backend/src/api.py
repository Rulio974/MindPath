#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv

# Configurer OpenMP pour éviter les conflits
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from src.utils import detect_language
from src.auth.database import get_db, init_db
from src.auth.dependencies import get_current_user, get_current_admin
from src.auth.routes import auth_router, users_router
from src.auth.crud import SearchLogCRUD
from src.auth.schemas import SearchLogCreate
from src.admin import admin_router

# Charger les variables d'environnement
load_dotenv()

# Configuration des templates
templates = Jinja2Templates(directory="templates")

def run_api_mode(engines, top_k, year_weighted):
    """
    Lance l'API FastAPI pour servir les recherches avec authentification par token.
    """
    # Initialiser la base de données
    init_db()
    
    app = FastAPI(
        title="Moteur de recherche sémantique",
        description="API de recherche sémantique avec authentification par token pour questionnaires de sécurité",
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
            "message": "Moteur de recherche sémantique avec authentification par token",
            "version": "3.0.0",
            "endpoints": {
                "auth": "/auth",
                "users": "/users",
                "search": "/search",
                "admin": "/admin",
                "docs": "/docs"
            }
        }

    @app.post("/search")
    async def search_endpoint(
        request: Request,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Recherche sémantique (authentification par token requise)
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
            return {"error": "Aucun moteur de recherche disponible pour cette langue."}
        
        # Utiliser la méthode search de l'embedding_loader
        results = engine.search(query, top_k=top_k_req, year_weighted=year_weighted)
        
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
            SearchLogCRUD.create_search_log(db, current_user, log_data)
        except Exception as e:
            print(f"Erreur lors du logging de la recherche : {e}")
        
        return {
            "results": results,
            "query": query,
            "language": lang,
            "response_time": response_time,
            "user": current_user["username"]
        }

    @app.get("/health")
    async def health_check():
        """Vérification de l'état du serveur"""
        return {"status": "healthy", "engines_loaded": len(engines)}

    @app.get("/stats")
    async def get_stats(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Statistiques de recherche pour l'utilisateur"""
        stats = SearchLogCRUD.get_search_statistics(db, current_user["user_id"])
        return {
            "user_stats": stats,
            "engines_info": {lang: engine.get_engine_info() for lang, engine in engines.items()}
        }

    @app.get("/admin/stats")
    async def get_admin_stats(
        current_user: dict = Depends(get_current_admin),
        db: Session = Depends(get_db)
    ):
        """Statistiques globales (admin seulement)"""
        stats = SearchLogCRUD.get_search_statistics(db)
        return {
            "global_stats": stats,
            "engines_info": {lang: engine.get_engine_info() for lang, engine in engines.items()}
        }

    # Démarrer le serveur
    uvicorn.run(app, host="0.0.0.0", port=8000)
