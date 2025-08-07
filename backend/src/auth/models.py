#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Modèle utilisateur simplifié avec token"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    api_token = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SearchLog(Base):
    """Modèle pour logger les recherches des utilisateurs"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Peut être null pour les recherches anonymes
    username = Column(String(100), nullable=True)  # Stocker le username pour les logs
    query = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    results_count = Column(Integer, nullable=False)
    response_time = Column(Integer, nullable=False)  # en millisecondes
    created_at = Column(DateTime, default=datetime.utcnow) 