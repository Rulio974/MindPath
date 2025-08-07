#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# Schémas pour l'authentification
class Token(BaseModel):
    """Schéma de réponse pour les tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Données contenues dans le token"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    roles: List[str] = []

class RefreshTokenRequest(BaseModel):
    """Requête pour rafraîchir un token"""
    refresh_token: str

# Schémas pour les utilisateurs
class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schéma pour créer un utilisateur"""
    password: str
    is_active: bool = True
    is_superuser: bool = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    hashed_password: Optional[str] = None

class UserChangePassword(BaseModel):
    """Schéma pour changer le mot de passe"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le nouveau mot de passe doit contenir au moins 8 caractères')
        if not any(c.isupper() for c in v):
            raise ValueError('Le nouveau mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le nouveau mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le nouveau mot de passe doit contenir au moins un chiffre')
        return v

class User(UserBase):
    """Schéma de réponse pour les utilisateurs"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    username: str
    password: str

# Schémas pour les rôles
class RoleBase(BaseModel):
    """Schéma de base pour les rôles"""
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """Schéma pour créer un rôle"""
    pass

class Role(RoleBase):
    """Schéma de réponse pour les rôles"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Schémas pour les logs de recherche
class SearchLogCreate(BaseModel):
    """Schéma pour créer un log de recherche"""
    query: str
    language: str
    results_count: int
    response_time: int

class SearchLog(BaseModel):
    """Schéma de réponse pour les logs de recherche"""
    id: int
    user_id: Optional[int]
    query: str
    language: str
    results_count: int
    response_time: int
    created_at: datetime

    class Config:
        orm_mode = True

# Schémas pour les réponses d'erreur
class ErrorResponse(BaseModel):
    """Schéma de réponse d'erreur"""
    detail: str
    error_code: Optional[str] = None

class SuccessResponse(BaseModel):
    """Schéma de réponse de succès"""
    message: str
    data: Optional[dict] = None 