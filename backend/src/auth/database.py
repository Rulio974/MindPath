#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .models import Base

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./semantic_search.db")

# Configuration pour SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # Configuration pour PostgreSQL ou autres
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Crée toutes les tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialise la base de données avec les données par défaut"""
    from .models import Role, User, UserRole
    from .security import get_password_hash
    
    create_tables()
    
    db = SessionLocal()
    try:
        # Créer les rôles par défaut
        default_roles = [
            {"name": "admin", "description": "Administrateur avec tous les droits"},
            {"name": "user", "description": "Utilisateur standard avec accès à la recherche"},
            {"name": "viewer", "description": "Utilisateur en lecture seule"},
        ]
        
        for role_data in default_roles:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
        
        # Créer un utilisateur admin par défaut
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="Administrateur",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            
            # Assigner le rôle admin
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                db.add(user_role)
        
        db.commit()
        print("Base de données initialisée avec succès")
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        db.rollback()
    finally:
        db.close() 