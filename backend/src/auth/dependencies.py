#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, Role, UserRole
from .security import verify_token
from .schemas import TokenData

# Configuration du schéma de sécurité
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Récupère l'utilisateur actuellement connecté"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Récupère l'utilisateur actuel s'il est actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )
    return current_user

def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Récupère l'utilisateur actuel s'il est superutilisateur"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilèges insuffisants"
        )
    return current_user

def get_user_roles(user: User, db: Session) -> List[str]:
    """Récupère les rôles d'un utilisateur"""
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles.append(role.name)
    return roles

def require_roles(required_roles: List[str]):
    """Décorateur pour exiger certains rôles"""
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        user_roles = get_user_roles(current_user, db)
        
        # Les superutilisateurs ont tous les droits
        if current_user.is_superuser:
            return current_user
            
        # Vérifier si l'utilisateur a au moins un des rôles requis
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôles requis: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

def require_admin():
    """Décorateur pour exiger le rôle admin"""
    return require_roles(["admin"])

def require_user_or_admin():
    """Décorateur pour exiger le rôle user ou admin"""
    return require_roles(["user", "admin"])

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Récupère l'utilisateur actuel si le token est fourni, sinon None"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if user and user.is_active:
            return user
    except:
        pass
    
    return None

class RoleChecker:
    """Classe pour vérifier les rôles de manière flexible"""
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if current_user.is_superuser:
            return current_user
            
        user_roles = get_user_roles(current_user, db)
        
        if not any(role in user_roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles autorisés: {', '.join(self.allowed_roles)}"
            )
        return current_user 