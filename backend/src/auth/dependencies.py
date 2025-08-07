#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from .database import get_db
from .security import verify_api_token

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Récupère l'utilisateur actuellement connecté via token API"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token API requis",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraire le token du header Authorization
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format de token invalide. Utilisez 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    user_info = verify_api_token(token, db)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token API invalide ou utilisateur inactif",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Récupère l'utilisateur actuel s'il est administrateur"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilèges administrateur requis"
        )
    return current_user

def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Récupère l'utilisateur actuel si le token est fourni, sinon None"""
    if not authorization:
        return None
    
    try:
        if not authorization.startswith("Bearer "):
            return None
        
        token = authorization.replace("Bearer ", "")
        user_info = verify_api_token(token, db)
        return user_info
    except:
        return None 