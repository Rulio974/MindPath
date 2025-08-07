#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from .models import User, Role, UserRole, RefreshToken, SearchLog
from .schemas import UserCreate, UserUpdate, UserChangePassword, RoleCreate, SearchLogCreate
from .security import get_password_hash, verify_password, create_refresh_token
import secrets

class UserCRUD:
    """Opérations CRUD pour les utilisateurs"""
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Récupère une liste d'utilisateurs"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Crée un nouvel utilisateur"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Assigner le rôle "user" par défaut
        user_role = RoleCRUD.get_role_by_name(db, "user")
        if user_role:
            UserCRUD.assign_role(db, db_user.id, user_role.id)
        
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Met à jour un utilisateur"""
        db_user = UserCRUD.get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Supprime un utilisateur"""
        db_user = UserCRUD.get_user(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            user = UserCRUD.get_user_by_email(db, username)
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def change_password(db: Session, user_id: int, password_change: UserChangePassword) -> bool:
        """Change le mot de passe d'un utilisateur"""
        user = UserCRUD.get_user(db, user_id)
        if not user:
            return False
        
        if not verify_password(password_change.current_password, user.hashed_password):
            return False
        
        user.hashed_password = get_password_hash(password_change.new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def assign_role(db: Session, user_id: int, role_id: int) -> bool:
        """Assigne un rôle à un utilisateur"""
        existing = db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        ).first()
        
        if existing:
            return False
        
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        db.commit()
        return True
    
    @staticmethod
    def remove_role(db: Session, user_id: int, role_id: int) -> bool:
        """Retire un rôle d'un utilisateur"""
        user_role = db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        ).first()
        
        if not user_role:
            return False
        
        db.delete(user_role)
        db.commit()
        return True
    
    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[Role]:
        """Récupère les rôles d'un utilisateur"""
        user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
        roles = []
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                roles.append(role)
        return roles

class RoleCRUD:
    """Opérations CRUD pour les rôles"""
    
    @staticmethod
    def get_role(db: Session, role_id: int) -> Optional[Role]:
        """Récupère un rôle par son ID"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        """Récupère un rôle par son nom"""
        return db.query(Role).filter(Role.name == name).first()
    
    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """Récupère une liste de rôles"""
        return db.query(Role).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_role(db: Session, role: RoleCreate) -> Role:
        """Crée un nouveau rôle"""
        db_role = Role(name=role.name, description=role.description)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Supprime un rôle"""
        db_role = RoleCRUD.get_role(db, role_id)
        if not db_role:
            return False
        
        db.delete(db_role)
        db.commit()
        return True

class RefreshTokenCRUD:
    """Opérations CRUD pour les refresh tokens"""
    
    @staticmethod
    def create_refresh_token(db: Session, user_id: int) -> RefreshToken:
        """Crée un nouveau refresh token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    
    @staticmethod
    def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
        """Récupère un refresh token"""
        return db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).first()
    
    @staticmethod
    def revoke_refresh_token(db: Session, token: str) -> bool:
        """Révoque un refresh token"""
        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if not db_token:
            return False
        
        db_token.is_revoked = True
        db.commit()
        return True
    
    @staticmethod
    def revoke_user_tokens(db: Session, user_id: int) -> bool:
        """Révoque tous les tokens d'un utilisateur"""
        tokens = db.query(RefreshToken).filter(
            and_(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
        ).all()
        
        for token in tokens:
            token.is_revoked = True
        
        db.commit()
        return True

class SearchLogCRUD:
    """Opérations CRUD pour les logs de recherche"""
    
    @staticmethod
    def create_search_log(db: Session, user_id: Optional[int], log_data: SearchLogCreate) -> SearchLog:
        """Crée un nouveau log de recherche"""
        db_log = SearchLog(
            user_id=user_id,
            query=log_data.query,
            language=log_data.language,
            results_count=log_data.results_count,
            response_time=log_data.response_time
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    
    @staticmethod
    def get_search_logs(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[SearchLog]:
        """Récupère les logs de recherche"""
        query = db.query(SearchLog)
        if user_id:
            query = query.filter(SearchLog.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_search_statistics(db: Session, user_id: Optional[int] = None) -> dict:
        """Récupère les statistiques de recherche"""
        query = db.query(SearchLog)
        if user_id:
            query = query.filter(SearchLog.user_id == user_id)
        
        total_searches = query.count()
        avg_response_time = query.with_entities(func.avg(SearchLog.response_time)).scalar()
        
        return {
            "total_searches": total_searches,
            "average_response_time": avg_response_time or 0
        } 