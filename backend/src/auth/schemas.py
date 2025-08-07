#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schémas pour l'authentification
class TokenAuth(BaseModel):
    """Schéma pour l'authentification par token API"""
    token: str

# Schémas pour les utilisateurs
class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schéma pour créer un utilisateur"""
    is_active: bool = True
    is_admin: bool = False

class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    """Schéma de réponse pour les utilisateurs"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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
        from_attributes = True

# Schémas pour les réponses d'erreur
class ErrorResponse(BaseModel):
    """Schéma de réponse d'erreur"""
    detail: str
    error_code: Optional[str] = None

class SuccessResponse(BaseModel):
    """Schéma de réponse de succès"""
    message: str
    data: Optional[dict] = None 