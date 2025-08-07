#!/usr/bin/env python
# -*- coding: utf-8 -*-

import secrets
import bcrypt
from typing import Optional
from fastapi import HTTPException, status

def generate_api_token() -> str:
    """Génère un token API sécurisé"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def verify_api_token(token: str, db) -> Optional[dict]:
    """
    Vérifie un token API et retourne les informations de l'utilisateur
    
    Args:
        token: Token API à vérifier
        db: Session de base de données
        
    Returns:
        dict: Informations de l'utilisateur ou None si invalide
    """
    from .models import User
    
    user = db.query(User).filter(
        User.api_token == token,
        User.is_active == True
    ).first()
    
    if not user:
        return None
    
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }

def require_token():
    """Décorateur pour exiger un token API valide"""
    def token_checker(token: str):
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token API requis",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    return token_checker

def require_admin():
    """Décorateur pour exiger un token admin"""
    def admin_checker(user_info: dict):
        if not user_info.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilèges administrateur requis"
            )
        return user_info
    return admin_checker 