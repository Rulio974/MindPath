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
from src.auth.models import User, SearchLog
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
            "https://lesphinx.mindpath-dev.fr",
            "http://lesphinx.mindpath-dev.fr",
            "https://api.lesphinx.mindpath-dev.fr",
            "http://api.lesphinx.mindpath-dev.fr",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://164.132.58.187",
            "https://etesiea-my.sharepoint.com",
            "https://office.live.com",
            "https://*.office.com",
            "file://",
            "*"
        ],
        allow_credentials=False,
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

    @app.get("/debug/stats")
    async def debug_stats(db: Session = Depends(get_db)):
        """Endpoint de debug pour les statistiques"""
        try:
            import json
            import os
            
            users_count = db.query(User).count()
            logs_count = db.query(SearchLog).count()
            
            # Lire le fichier metadata.json
            metadata_info = {}
            metadata_paths = [
                "backend/embeddings/metadata.json",
                "embeddings/metadata.json",
                "embeddings/fr/metadata.json",
                "embeddings/en/metadata.json"
            ]
            
            for metadata_path in metadata_paths:
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        metadata_info = {
                            "file_path": metadata_path,
                            "statistics": metadata.get('statistics', {}),
                            "model_info": metadata.get('model_info', {})
                        }
                    break
            
            return {
                "users_count": users_count,
                "logs_count": logs_count,
                "engines_count": len(engines),
                "engines": list(engines.keys()),
                "metadata": metadata_info
            }
        except Exception as e:
            return {"error": str(e)}

    @app.get("/stats")
    async def get_stats(
        current_user: dict = Depends(get_current_admin_session),
        db: Session = Depends(get_db)
    ):
        """Statistiques générales du système"""
        try:
            # Compter les utilisateurs
            total_users = db.query(User).count()
            print(f"DEBUG: Nombre d'utilisateurs = {total_users}")
            
            # Compter les entrées dans la base (logs de recherche)
            total_entries = db.query(SearchLog).count()
            print(f"DEBUG: Nombre d'entrées = {total_entries}")
            
            # Lire les statistiques depuis le fichier metadata.json
            total_questions = 0
            total_entreprises = 0
            try:
                import json
                import os
                
                # Chercher le fichier metadata.json dans les dossiers d'embeddings
                metadata_paths = [
                    "backend/embeddings/metadata.json",
                    "embeddings/metadata.json",
                    "embeddings/fr/metadata.json",
                    "embeddings/en/metadata.json"
                ]
                
                for metadata_path in metadata_paths:
                    if os.path.exists(metadata_path):
                        print(f"DEBUG: Fichier metadata trouvé: {metadata_path}")
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            
                        if 'statistics' in metadata:
                            if 'total_questions' in metadata['statistics']:
                                total_questions = metadata['statistics']['total_questions']
                                print(f"DEBUG: {metadata_path} - {total_questions} questions")
                            if 'unique_entreprises' in metadata['statistics']:
                                total_entreprises = metadata['statistics']['unique_entreprises']
                                print(f"DEBUG: {metadata_path} - {total_entreprises} entreprises")
                        elif 'model_info' in metadata and 'num_questions' in metadata['model_info']:
                            total_questions = metadata['model_info']['num_questions']
                            print(f"DEBUG: {metadata_path} - {total_questions} questions (model_info)")
                        break
                else:
                    print("DEBUG: Aucun fichier metadata.json trouvé")
                    
            except Exception as e:
                print(f"DEBUG: Erreur lecture metadata.json: {e}")
                # Fallback: essayer de compter depuis les moteurs
                for engine_name, engine in engines.items():
                    if hasattr(engine, 'documents') and engine.documents:
                        total_questions = len(engine.documents)
                        break
            
            result = {
                "total_users": total_users,
                "total_entries": total_questions,  # Nombre de questions
                "total_documents": total_entreprises  # Nombre d'entreprises
            }
            print(f"DEBUG: Résultat final = {result}")
            return result
            
        except Exception as e:
            print(f"Erreur dans get_stats: {e}")
            import traceback
            traceback.print_exc()
            return {
                "total_users": 0,
                "total_entries": 0,
                "total_documents": 0,
                "error": str(e)
            }

    # Note: Endpoint admin/stats retiré - interface d'administration séparée

    # Configuration du serveur
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Configuration HTTPS
    ssl_keyfile = os.getenv("SSL_KEYFILE", "certs/backend.key")
    ssl_certfile = os.getenv("SSL_CERTFILE", "certs/backend.crt")
    
    # Vérifier si les certificats SSL existent
    if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        print(f"🔒 Démarrage du serveur HTTPS sur {host}:{port}")
        print(f"📚 Documentation disponible sur https://{host}:{port}/docs")
        print(f"🔐 Compte admin par défaut : admin / admin123")
        uvicorn.run(app, host=host, port=port, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
    else:
        print(f"⚠️  Certificats SSL non trouvés, démarrage en HTTP sur {host}:{port}")
        print(f"📚 Documentation disponible sur http://{host}:{port}/docs")
        print(f"🔐 Compte admin par défaut : admin / admin123")
        uvicorn.run(app, host=host, port=port)

