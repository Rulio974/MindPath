#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import (
    User as UserSchema, UserCreate, UserUpdate, SearchLog as SearchLogSchema,
    SuccessResponse, ErrorResponse, TokenAuth, LoginRequest, LoginResponse
)
from .crud import UserCRUD, SearchLogCRUD
from .dependencies import get_current_user, get_current_admin, get_current_admin_session
from .security import verify_password, generate_api_token
from .sessions import create_session

# Routeur pour l'authentification
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Connexion avec email et mot de passe"""
    user = UserCRUD.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte non configuré pour l'authentification par mot de passe"
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé"
        )
    
    # Créer une session pour l'interface d'administration
    user_info = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }
    session_token = create_session(user.id, user_info)
    
    return LoginResponse(
        access_token=session_token,
        token_type="bearer",
        user=UserSchema(
            id=user.id,
            api_token=user.api_token,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )

@auth_router.post("/verify-api-token", response_model=UserSchema)
async def verify_api_token(
    token_data: TokenAuth,
    db: Session = Depends(get_db)
):
    """Vérifie un token API et retourne les informations de l'utilisateur"""
    user = UserCRUD.get_user_by_token(db, token_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token API invalide"
        )
    
    return UserSchema(
        id=user.id,
        api_token=user.api_token,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@auth_router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: dict = Depends(get_current_admin_session),
    db: Session = Depends(get_db)
):
    """Récupère les informations de l'utilisateur admin actuel"""
    user = UserCRUD.get_user(db, current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return UserSchema(
        id=user.id,
        api_token=user.api_token,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@auth_router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_admin_session),
    db: Session = Depends(get_db)
):
    """Met à jour les informations de l'utilisateur admin actuel"""
    updated_user = UserCRUD.update_user(db, current_user["id"], user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return UserSchema(
        id=updated_user.id,
        api_token=updated_user.api_token,
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_admin=updated_user.is_admin,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@auth_router.post("/regenerate-token", response_model=SuccessResponse)
async def regenerate_token(
    current_user: dict = Depends(get_current_admin_session),
    db: Session = Depends(get_db)
):
    """Régénère le token API de l'utilisateur admin actuel"""
    new_token = UserCRUD.regenerate_token(db, current_user["id"])
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return SuccessResponse(message=f"Nouveau token généré: {new_token}")

# Routeur pour la gestion des utilisateurs (admin)
users_router = APIRouter(prefix="/users", tags=["Users Management"])

@users_router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_session)
):
    """Crée un nouvel utilisateur (admin seulement)"""
    # Vérifier si l'utilisateur existe déjà
    if UserCRUD.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    if UserCRUD.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec ce nom d'utilisateur existe déjà"
        )
    
    created_user = UserCRUD.create_user(db, user)
    
    return UserSchema(
        id=created_user.id,
        api_token=created_user.api_token,
        email=created_user.email,
        username=created_user.username,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        is_admin=created_user.is_admin,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at
    )

@users_router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_session)
):
    """Récupère la liste des utilisateurs (admin seulement)"""
    users = UserCRUD.get_users(db, skip=skip, limit=limit)
    result = []
    
    for user in users:
        result.append(UserSchema(
            id=user.id,
            api_token=user.api_token,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        ))
    
    return result

@users_router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_session)
):
    """Récupère un utilisateur par son ID (admin seulement)"""
    user = UserCRUD.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return UserSchema(
        id=user.id,
        api_token=user.api_token,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@users_router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_session)
):
    """Met à jour un utilisateur (admin seulement)"""
    updated_user = UserCRUD.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return UserSchema(
        id=updated_user.id,
        api_token=updated_user.api_token,
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_admin=updated_user.is_admin,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@users_router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_session)
):
    """Supprime un utilisateur (admin seulement)"""
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )
    
    if not UserCRUD.delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return SuccessResponse(message="Utilisateur supprimé avec succès")

@users_router.post("/{user_id}/regenerate-token", response_model=SuccessResponse)
async def regenerate_user_token(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_session)
):
    """Régénère le token API d'un utilisateur (admin seulement)"""
    new_token = UserCRUD.regenerate_token(db, user_id)
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return SuccessResponse(message=f"Nouveau token généré pour l'utilisateur: {new_token}") 