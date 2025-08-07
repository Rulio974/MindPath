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
    from .models import User
    from .security import generate_api_token
    
    create_tables()
    
    db = SessionLocal()
    try:
        # Créer un utilisateur admin par défaut
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="Administrateur",
                api_token=generate_api_token(),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Utilisateur admin créé avec le token: {admin_user.api_token}")
        
        db.commit()
        print("Base de données initialisée avec succès")
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        db.rollback()
    finally:
        db.close() 