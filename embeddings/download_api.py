#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API simple pour télécharger les fichiers d'embeddings calculés
"""

import os
import zipfile
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(
    title="API de téléchargement des embeddings",
    description="API pour télécharger les fichiers d'embeddings calculés",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "message": "API de téléchargement des embeddings",
        "endpoints": {
            "download_fr": "/download/fr",
            "download_en": "/download/en", 
            "download_all": "/download/all",
            "list_files": "/files"
        }
    }

@app.get("/files")
async def list_files():
    """Lister les fichiers disponibles"""
    files = {}
    
    # Vérifier les fichiers français
    fr_dir = Path("embeddings/fr")
    if fr_dir.exists():
        files["fr"] = [f.name for f in fr_dir.iterdir() if f.is_file()]
    
    # Vérifier les fichiers anglais
    en_dir = Path("embeddings/en")
    if en_dir.exists():
        files["en"] = [f.name for f in en_dir.iterdir() if f.is_file()]
    
    return {
        "available_files": files,
        "total_files": sum(len(files.get(lang, [])) for lang in files)
    }

@app.get("/download/fr")
async def download_fr():
    """Télécharger les fichiers français"""
    fr_dir = Path("embeddings/fr")
    if not fr_dir.exists():
        raise HTTPException(status_code=404, detail="Fichiers français non trouvés")
    
    # Créer un zip temporaire
    zip_path = "fr_embeddings.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in fr_dir.iterdir():
            if file_path.is_file():
                zipf.write(file_path, f"fr/{file_path.name}")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="fr_embeddings.zip"
    )

@app.get("/download/en")
async def download_en():
    """Télécharger les fichiers anglais"""
    en_dir = Path("embeddings/en")
    if not en_dir.exists():
        raise HTTPException(status_code=404, detail="Fichiers anglais non trouvés")
    
    # Créer un zip temporaire
    zip_path = "en_embeddings.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in en_dir.iterdir():
            if file_path.is_file():
                zipf.write(file_path, f"en/{file_path.name}")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="en_embeddings.zip"
    )

@app.get("/download/all")
async def download_all():
    """Télécharger tous les fichiers"""
    fr_dir = Path("embeddings/fr")
    en_dir = Path("embeddings/en")
    
    if not fr_dir.exists() and not en_dir.exists():
        raise HTTPException(status_code=404, detail="Aucun fichier d'embeddings trouvé")
    
    # Créer un zip temporaire
    zip_path = "all_embeddings.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Ajouter les fichiers français
        if fr_dir.exists():
            for file_path in fr_dir.iterdir():
                if file_path.is_file():
                    zipf.write(file_path, f"fr/{file_path.name}")
        
        # Ajouter les fichiers anglais
        if en_dir.exists():
            for file_path in en_dir.iterdir():
                if file_path.is_file():
                    zipf.write(file_path, f"en/{file_path.name}")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="all_embeddings.zip"
    )

if __name__ == "__main__":
    print("🚀 Démarrage de l'API de téléchargement")
    print("   URL: http://localhost:8001")
    print("   Endpoints:")
    print("   - GET /download/fr  - Télécharger fichiers français")
    print("   - GET /download/en  - Télécharger fichiers anglais")
    print("   - GET /download/all - Télécharger tous les fichiers")
    print("   - GET /files        - Lister les fichiers disponibles")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 