#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from .models import User, SearchLog
from .schemas import UserCreate, UserUpdate, SearchLogCreate
from .security import generate_api_token

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
    def get_user_by_token(db: Session, api_token: str) -> Optional[User]:
        """Récupère un utilisateur par son token API"""
        return db.query(User).filter(
            and_(User.api_token == api_token, User.is_active == True)
        ).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Récupère une liste d'utilisateurs"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Crée un nouvel utilisateur"""
        api_token = generate_api_token()
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            api_token=api_token,
            is_admin=user.is_admin
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
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
    def regenerate_token(db: Session, user_id: int) -> Optional[str]:
        """Régénère le token API d'un utilisateur"""
        db_user = UserCRUD.get_user(db, user_id)
        if not db_user:
            return None
        
        new_token = generate_api_token()
        db_user.api_token = new_token
        db_user.updated_at = datetime.utcnow()
        db.commit()
        return new_token

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