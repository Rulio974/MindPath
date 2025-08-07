#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .database import get_db
from .models import User
from .schemas import (
    Token, User as UserSchema, UserCreate, UserUpdate, UserChangePassword,
    Role as RoleSchema, RoleCreate, SearchLog as SearchLogSchema,
    SuccessResponse, ErrorResponse, UserLogin
)
from .crud import UserCRUD, RoleCRUD, RefreshTokenCRUD, SearchLogCRUD
from .dependencies import (
    get_current_active_user, get_current_superuser, require_admin,
    require_user_or_admin, get_user_roles
)
from .security import (
    create_access_token, create_refresh_token, verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Routeur pour l'authentification
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Connexion d'un utilisateur (formulaire)"""
    user = UserCRUD.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur inactif"
        )
    
    # Récupérer les rôles de l'utilisateur
    user_roles = get_user_roles(user, db)
    
    # Créer les tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "roles": user_roles
        },
        expires_delta=access_token_expires
    )
    
    refresh_token_obj = RefreshTokenCRUD.create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_obj.token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@auth_router.post("/login-json", response_model=Token)
async def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Connexion d'un utilisateur (JSON)"""
    user = UserCRUD.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur inactif"
        )
    
    # Récupérer les rôles de l'utilisateur
    user_roles = get_user_roles(user, db)
    
    # Créer les tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "roles": user_roles
        },
        expires_delta=access_token_expires
    )
    
    refresh_token_obj = RefreshTokenCRUD.create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_obj.token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Rafraîchit un token d'accès"""
    token_obj = RefreshTokenCRUD.get_refresh_token(db, refresh_token)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide ou expiré"
        )
    
    user = UserCRUD.get_user(db, token_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé ou inactif"
        )
    
    # Révoquer l'ancien token
    RefreshTokenCRUD.revoke_refresh_token(db, refresh_token)
    
    # Récupérer les rôles de l'utilisateur
    user_roles = get_user_roles(user, db)
    
    # Créer de nouveaux tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "roles": user_roles
        },
        expires_delta=access_token_expires
    )
    
    new_refresh_token = RefreshTokenCRUD.create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token.token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@auth_router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Déconnexion d'un utilisateur"""
    RefreshTokenCRUD.revoke_user_tokens(db, current_user.id)
    return SuccessResponse(message="Déconnexion réussie")

@auth_router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère les informations de l'utilisateur actuel"""
    user_roles = get_user_roles(current_user, db)
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "roles": user_roles
    }
    return UserSchema(**user_dict)

@auth_router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Met à jour les informations de l'utilisateur actuel"""
    updated_user = UserCRUD.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user_roles = get_user_roles(updated_user, db)
    user_dict = {
        "id": updated_user.id,
        "email": updated_user.email,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "is_active": updated_user.is_active,
        "is_superuser": updated_user.is_superuser,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
        "roles": user_roles
    }
    return UserSchema(**user_dict)

@auth_router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_change: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change le mot de passe de l'utilisateur actuel"""
    if not UserCRUD.change_password(db, current_user.id, password_change):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )
    
    return SuccessResponse(message="Mot de passe changé avec succès")

# Routeur pour la gestion des utilisateurs (admin)
users_router = APIRouter(prefix="/users", tags=["Users Management"])

@users_router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
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
    user_roles = get_user_roles(created_user, db)
    
    user_dict = {
        "id": created_user.id,
        "email": created_user.email,
        "username": created_user.username,
        "full_name": created_user.full_name,
        "is_active": created_user.is_active,
        "is_superuser": created_user.is_superuser,
        "created_at": created_user.created_at,
        "updated_at": created_user.updated_at,
        "roles": user_roles
    }
    return UserSchema(**user_dict)

@users_router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Récupère la liste des utilisateurs (admin seulement)"""
    users = UserCRUD.get_users(db, skip=skip, limit=limit)
    result = []
    
    for user in users:
        user_roles = get_user_roles(user, db)
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": user_roles
        }
        result.append(UserSchema(**user_dict))
    
    return result

@users_router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Récupère un utilisateur par son ID (admin seulement)"""
    user = UserCRUD.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user_roles = get_user_roles(user, db)
    user_dict = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": user_roles
    }
    return UserSchema(**user_dict)

@users_router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Met à jour un utilisateur (admin seulement)"""
    updated_user = UserCRUD.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user_roles = get_user_roles(updated_user, db)
    user_dict = {
        "id": updated_user.id,
        "email": updated_user.email,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "is_active": updated_user.is_active,
        "is_superuser": updated_user.is_superuser,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
        "roles": user_roles
    }
    return UserSchema(**user_dict)

@users_router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Supprime un utilisateur (admin seulement)"""
    if user_id == current_user.id:
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

# Routeur pour la gestion des rôles
roles_router = APIRouter(prefix="/roles", tags=["Roles Management"])

@roles_router.get("/", response_model=List[RoleSchema])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Récupère la liste des rôles (admin seulement)"""
    return RoleCRUD.get_roles(db, skip=skip, limit=limit)

@roles_router.post("/", response_model=RoleSchema)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Crée un nouveau rôle (admin seulement)"""
    if RoleCRUD.get_role_by_name(db, role.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un rôle avec ce nom existe déjà"
        )
    
    return RoleCRUD.create_role(db, role)

@roles_router.post("/{user_id}/assign/{role_id}", response_model=SuccessResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Assigne un rôle à un utilisateur (admin seulement)"""
    if not UserCRUD.assign_role(db, user_id, role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de l'assignation du rôle"
        )
    
    return SuccessResponse(message="Rôle assigné avec succès")

@roles_router.delete("/{user_id}/remove/{role_id}", response_model=SuccessResponse)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """Retire un rôle d'un utilisateur (admin seulement)"""
    if not UserCRUD.remove_role(db, user_id, role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la suppression du rôle"
        )
    
    return SuccessResponse(message="Rôle retiré avec succès") 