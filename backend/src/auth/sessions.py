#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Système de gestion des sessions pour l'interface d'administration
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import secrets

# Stockage des sessions en mémoire (pour simplifier)
# En production, utilisez Redis ou une base de données
sessions: Dict[str, dict] = {}

def create_session(user_id: int, user_info: dict) -> str:
    """Crée une nouvelle session pour un utilisateur"""
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = {
        "user_id": user_id,
        "user_info": user_info,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24)  # Session de 24h
    }
    return session_token

def get_session(session_token: str) -> Optional[dict]:
    """Récupère les informations d'une session"""
    if session_token not in sessions:
        return None
    
    session = sessions[session_token]
    
    # Vérifier l'expiration
    if datetime.utcnow() > session["expires_at"]:
        del sessions[session_token]
        return None
    
    return session

def delete_session(session_token: str) -> bool:
    """Supprime une session"""
    if session_token in sessions:
        del sessions[session_token]
        return True
    return False

def cleanup_expired_sessions():
    """Nettoie les sessions expirées"""
    current_time = datetime.utcnow()
    expired_tokens = [
        token for token, session in sessions.items()
        if current_time > session["expires_at"]
    ]
    
    for token in expired_tokens:
        del sessions[token]
