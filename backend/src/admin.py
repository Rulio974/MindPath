#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module d'administration pour la gestion des utilisateurs
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .auth.database import get_db
from .auth.models import User, SearchLog
from .auth.dependencies import get_current_admin
from .auth.schemas import UserCreate, UserUpdate, User as UserSchema
from .auth.crud import UserCRUD, SearchLogCRUD

# Import des templates depuis api.py
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Router pour l'administration
admin_router = APIRouter(prefix="/admin", tags=["Administration"])

# Route de test ultra-simple
@admin_router.get("/test-simple")
async def test_simple():
    return {"message": "Route admin fonctionne", "status": "OK"}

@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard d'administration"""
    # HTML simplifié et robuste
    html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { 
            background-color: #fafafa; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
            margin: 0;
            padding: 0;
            color: #2c3e50;
            line-height: 1.6;
        }
        .sidebar { 
            background-color: #ffffff; 
            min-height: 100vh; 
            border-right: 1px solid #e8ecef; 
            box-shadow: 0 0 20px rgba(0,0,0,0.04);
        }
        .main-content { 
            background-color: #ffffff; 
            border-radius: 12px; 
            margin: 24px; 
            padding: 32px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #f1f3f4;
        }
        .stats-card { 
            border: 1px solid #e8ecef; 
            border-radius: 12px; 
            background: #ffffff;
            transition: all 0.3s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .stats-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stats-card .card-body {
            padding: 24px;
        }
        .stats-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            font-size: 24px;
        }
        .icon-users { background: #f8f9ff; color: #6366f1; }
        .icon-active { background: #f0fdf4; color: #22c55e; }
        .icon-search { background: #fef3c7; color: #f59e0b; }
        .icon-globe { background: #ecfdf5; color: #10b981; }
        .stats-number {
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 4px;
        }
        .stats-label {
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }
        .nav-link { 
            border-radius: 8px; 
            margin: 2px 0; 
            transition: all 0.2s ease;
            color: #6b7280;
            font-weight: 500;
            padding: 12px 16px;
        }
        .nav-link:hover { 
            background-color: #f8f9fa; 
            color: #374151;
            transform: translateX(2px);
        }
        .nav-link.active { 
            background-color: #f8f9ff; 
            color: #6366f1;
            border-left: 3px solid #6366f1;
        }
        .btn { 
            border-radius: 8px; 
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid #e5e7eb;
        }
        .btn-outline-light {
            background: #ffffff;
            border-color: #e5e7eb;
            color: #374151;
        }
        .btn-outline-light:hover {
            background: #f9fafb;
            border-color: #d1d5db;
            color: #111827;
            transform: translateY(-1px);
        }
        .btn-primary {
            background: #6366f1;
            border-color: #6366f1;
        }
        .btn-primary:hover {
            background: #5855eb;
            border-color: #5855eb;
        }
        .alert { 
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            background: #f8f9fa;
        }
        .page-header {
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 20px;
            margin-bottom: 32px;
        }
        .page-title {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin: 0;
        }
        .page-subtitle {
            font-size: 14px;
            color: #6b7280;
            margin-top: 4px;
        }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 16px;
        }
        .card-header {
            background: #f9fafb !important;
            border-bottom: 1px solid #e5e7eb;
            border-radius: 12px 12px 0 0 !important;
        }
    </style>
</head>
<body>
    <div class="container-fluid p-0">
        <div class="row g-0">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2">
                <div class="sidebar p-3">
                    <div class="text-center mb-4">
                        <h4><i class="bi bi-shield-check text-primary"></i> Admin Panel</h4>
                    </div>
                    <nav class="nav nav-pills flex-column">
                        <a class="nav-link active" href="/admin/">
                            <i class="bi bi-speedometer2 me-2"></i> Dashboard
                        </a>
                        <a class="nav-link" href="/admin/users">
                            <i class="bi bi-people me-2"></i> Utilisateurs
                        </a>
                        <a class="nav-link" href="/admin/logs">
                            <i class="bi bi-journal-text me-2"></i> Logs de recherche
                        </a>
                        <hr class="my-3">
                        <a class="nav-link" href="/docs" target="_blank">
                            <i class="bi bi-book me-2"></i> Documentation API
                        </a>
                        <a class="nav-link" href="/login">
                            <i class="bi bi-box-arrow-right me-2"></i> Déconnexion
                        </a>
                    </nav>
                    <div class="mt-auto pt-4">
                        <div class="d-flex align-items-center">
                            <div class="me-2" style="width:36px;height:36px;background:#6c757d;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:600;">A</div>
                            <div>
                                <small class="d-block fw-semibold">admin</small>
                                <small class="text-muted">Administrateur</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10">
                <div class="main-content">
                    <div class="page-header">
                        <h1 class="page-title">Dashboard</h1>
                        <p class="page-subtitle">Vue d'ensemble de votre système de recherche sémantique</p>
                    </div>

                    <!-- Statistiques -->
                    <div class="row mb-5">
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-users">
                                        <i class="bi bi-people"></i>
                                    </div>
                                    <div class="stats-number">1</div>
                                    <div class="stats-label">Utilisateurs totaux</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-active">
                                        <i class="bi bi-person-check"></i>
                                    </div>
                                    <div class="stats-number">1</div>
                                    <div class="stats-label">Utilisateurs actifs</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-search">
                                        <i class="bi bi-search"></i>
                                    </div>
                                    <div class="stats-number">0</div>
                                    <div class="stats-label">Recherches totales</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-globe">
                                        <i class="bi bi-globe"></i>
                                    </div>
                                    <div class="stats-number">2</div>
                                    <div class="stats-label">Langues supportées</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Actions rapides -->
                    <div class="mb-5">
                        <h2 class="section-title">Actions rapides</h2>
                        <div class="row">
                            <div class="col-lg-3 col-md-6 mb-3">
                                <a href="/admin/users" class="btn btn-outline-light w-100 py-3 text-decoration-none">
                                    <i class="bi bi-people d-block mb-2" style="font-size: 24px;"></i>
                                    <span>Gérer les utilisateurs</span>
                                </a>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-3">
                                <a href="/admin/logs" class="btn btn-outline-light w-100 py-3 text-decoration-none">
                                    <i class="bi bi-journal-text d-block mb-2" style="font-size: 24px;"></i>
                                    <span>Voir les logs</span>
                                </a>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-3">
                                <a href="/docs" target="_blank" class="btn btn-outline-light w-100 py-3 text-decoration-none">
                                    <i class="bi bi-book d-block mb-2" style="font-size: 24px;"></i>
                                    <span>Documentation API</span>
                                </a>
                            </div>
                            <div class="col-lg-3 col-md-6 mb-3">
                                <a href="/health" target="_blank" class="btn btn-primary w-100 py-3 text-decoration-none">
                                    <i class="bi bi-activity d-block mb-2" style="font-size: 24px;"></i>
                                    <span>Statut système</span>
                                </a>
                            </div>
                        </div>
                    </div>

                    <!-- Informations système -->
                    <div class="alert">
                        <div class="d-flex align-items-start">
                            <i class="bi bi-info-circle me-3 mt-1" style="font-size: 20px; color: #6366f1;"></i>
                            <div>
                                <h6 class="mb-1" style="color: #374151; font-weight: 600;">Système opérationnel</h6>
                                <p class="mb-0" style="color: #6b7280; font-size: 14px;">
                                    Votre moteur de recherche sémantique est configuré et prêt à l'emploi. 
                                    Utilisez la navigation latérale pour accéder aux différentes fonctionnalités.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@admin_router.get("/api/dashboard")
async def admin_dashboard_data(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Données du dashboard d'administration"""
    
    # Statistiques générales
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_searches = db.query(SearchLog).count()
    
    # Dernières recherches
    recent_searches = db.query(SearchLog).order_by(desc(SearchLog.created_at)).limit(10).all()
    
    # Utilisateurs récents
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(5).all()
    
    # Statistiques par langue
    search_stats = db.query(
        SearchLog.language,
        func.count(SearchLog.id).label('count')
    ).group_by(SearchLog.language).all()
    
    return {
        "current_user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "is_admin": current_user.is_admin
        },
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "total_searches": total_searches,
            "recent_searches": [
                {
                    "id": search.id,
                    "query": search.query,
                    "language": search.language,
                    "response_time": search.response_time,
                    "created_at": search.created_at.isoformat()
                } for search in recent_searches
            ],
            "recent_users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "created_at": user.created_at.isoformat()
                } for user in recent_users
            ],
            "search_stats": [
                {
                    "language": stat.language,
                    "count": stat.count
                } for stat in search_stats
            ]
        }
    }

@admin_router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    """Page de gestion des utilisateurs"""
    
    # Récupérer les vrais utilisateurs depuis la base de données
    from .auth.crud import UserCRUD
    users = UserCRUD.get_users(db)
    
    # Convertir en format pour l'affichage
    users_data = []
    for user in users:
        # Récupérer les rôles de l'utilisateur
        user_roles = UserCRUD.get_user_roles(db, user.id)
        role_names = [role.name for role in user_roles] if user_roles else []
        
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.strftime("%d/%m/%Y %H:%M") if user.created_at else "N/A",
            "roles": role_names
        })
    
    # Convertir en JSON pour JavaScript (même si on ne l'utilise plus)
    import json
    users_json = json.dumps(users_data)
    html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Utilisateurs - Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { 
            background-color: #fafafa; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
            margin: 0;
            padding: 0;
            color: #2c3e50;
            line-height: 1.6;
        }
        .sidebar { 
            background-color: #ffffff; 
            min-height: 100vh; 
            border-right: 1px solid #e8ecef; 
            box-shadow: 0 0 20px rgba(0,0,0,0.04);
        }
        .main-content { 
            background-color: #ffffff; 
            border-radius: 12px; 
            margin: 24px; 
            padding: 32px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #f1f3f4;
        }
        .nav-link { 
            border-radius: 8px; 
            margin: 2px 0; 
            transition: all 0.2s ease;
            color: #6b7280;
            font-weight: 500;
            padding: 12px 16px;
        }
        .nav-link:hover { 
            background-color: #f8f9fa; 
            color: #374151;
            transform: translateX(2px);
        }
        .nav-link.active { 
            background-color: #f8f9ff; 
            color: #6366f1;
            border-left: 3px solid #6366f1;
        }
        .page-header {
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 20px;
            margin-bottom: 32px;
        }
        .page-title {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin: 0;
        }
        .page-subtitle {
            font-size: 14px;
            color: #6b7280;
            margin-top: 4px;
        }
        .btn { 
            border-radius: 8px; 
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid #e5e7eb;
        }
        .btn-primary {
            background: #6366f1;
            border-color: #6366f1;
        }
        .btn-primary:hover {
            background: #5855eb;
            border-color: #5855eb;
        }
        .table {
            border-radius: 12px;
            overflow: hidden;
            border: none;
        }
        .table th {
            background: #f8fafc;
            border: none;
            font-weight: 600;
            color: #475569;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 16px 20px;
        }
        .table td {
            border: none;
            padding: 16px 20px;
            vertical-align: middle;
            border-bottom: 1px solid #f1f5f9;
        }
        .table tbody tr:hover {
            background: #f8fafc;
            transition: background-color 0.2s ease;
        }
        .table tbody tr:last-child td {
            border-bottom: none;
        }
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #6c757d;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 16px;
        }
        .badge {
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge.bg-success {
            background: #10b981 !important;
            color: white;
        }
        .badge.bg-secondary {
            background: #6b7280 !important;
            color: white;
        }
        .btn-group-sm .btn {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            margin: 0 2px;
        }
        .btn-outline-primary {
            border-color: #e5e7eb;
            color: #6b7280;
        }
        .btn-outline-primary:hover {
            background: #6366f1;
            border-color: #6366f1;
            color: white;
        }
        .btn-outline-danger {
            border-color: #e5e7eb;
            color: #6b7280;
        }
        .btn-outline-danger:hover {
            background: #ef4444;
            border-color: #ef4444;
            color: white;
        }
        .card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .card-header {
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            border-radius: 12px 12px 0 0;
            padding: 16px 24px;
        }
        .card-body {
            padding: 24px;
        }
        .alert {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 12px 16px;
        }
        .alert-success {
            background: #f0fdf4;
            border-color: #bbf7d0;
            color: #166534;
        }
        .alert-danger {
            background: #fef2f2;
            border-color: #fecaca;
            color: #991b1b;
        }
    </style>
</head>
<body>
    <div class="container-fluid p-0">
        <div class="row g-0">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2">
                <div class="sidebar p-3">
                    <div class="text-center mb-4">
                        <h4><i class="bi bi-shield-check text-primary"></i> Admin Panel</h4>
                    </div>
                    <nav class="nav nav-pills flex-column">
                        <a class="nav-link" href="/admin/">
                            <i class="bi bi-speedometer2 me-2"></i> Dashboard
                        </a>
                        <a class="nav-link active" href="/admin/users">
                            <i class="bi bi-people me-2"></i> Utilisateurs
                        </a>
                        <a class="nav-link" href="/admin/logs">
                            <i class="bi bi-journal-text me-2"></i> Logs de recherche
                        </a>
                        <hr class="my-3">
                        <a class="nav-link" href="/docs" target="_blank">
                            <i class="bi bi-book me-2"></i> Documentation API
                        </a>
                        <a class="nav-link" href="/login">
                            <i class="bi bi-box-arrow-right me-2"></i> Déconnexion
                        </a>
                    </nav>
                    <div class="mt-auto pt-4">
                        <div class="d-flex align-items-center">
                            <div class="me-2" style="width:36px;height:36px;background:#6c757d;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:600;">A</div>
                            <div>
                                <small class="d-block fw-semibold">admin</small>
                                <small class="text-muted">Administrateur</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10">
                <div class="main-content">
                    <div class="page-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h1 class="page-title">Utilisateurs</h1>
                                <p class="page-subtitle">Gérez les comptes utilisateurs et leurs permissions</p>
                            </div>
                            <button class="btn btn-primary" id="createUserBtn">
                                <i class="bi bi-person-plus me-2"></i>
                                Nouvel utilisateur
                            </button>
                        </div>
                    </div>

                    <!-- Alertes -->
                    <div id="alertContainer"></div>

                    <!-- Modal de création d'utilisateur -->
                    <div class="modal fade" id="createUserModal" tabindex="-1" aria-labelledby="createUserModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="createUserModalLabel">
                                        <i class="bi bi-person-plus me-2"></i>
                                        Créer un nouvel utilisateur
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <form id="createUserForm">
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label for="username" class="form-label">Nom d'utilisateur</label>
                                            <input type="text" class="form-control" id="username" name="username" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="email" name="email" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="full_name" class="form-label">Nom complet (optionnel)</label>
                                            <input type="text" class="form-control" id="full_name" name="full_name">
                                        </div>
                                        <div class="mb-3">
                                            <label for="password" class="form-label">Mot de passe</label>
                                            <input type="password" class="form-control" id="password" name="password" required>
                                            <div class="form-text">
                                                Le mot de passe doit contenir au moins 8 caractères avec au moins une majuscule, une minuscule et un chiffre.
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="is_active" name="is_active" checked>
                                                <label class="form-check-label" for="is_active">
                                                    Compte actif
                                                </label>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="is_admin" name="is_admin">
                                                <label class="form-check-label" for="is_admin">
                                                    Administrateur
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                                        <button type="submit" class="btn btn-primary">
                                            <i class="bi bi-check-lg me-2"></i>
                                            Créer l'utilisateur
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- Tableau des utilisateurs -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-people me-2"></i>
                                Liste des utilisateurs
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Utilisateur</th>
                                            <th>Email</th>
                                            <th>Statut</th>
                                            <th>Créé le</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="usersTableBody">""" + ''.join([f"""
                                        <tr>
                                            <td>
                                                <div class="d-flex align-items-center">
                                                    <div class="user-avatar me-3">
                                                        {user['username'][0].upper()}
                                                    </div>
                                                    <div>
                                                        <strong>{user['username']}</strong>
                                                        {'<i class="bi bi-shield-check text-primary ms-1" title="Administrateur"></i>' if user['is_admin'] else ''}
                                                    </div>
                                                </div>
                                            </td>
                                            <td>{user['email']}</td>
                                            <td>
                                                <span class="badge {'bg-success' if user['is_active'] else 'bg-secondary'}">
                                                    {'Actif' if user['is_active'] else 'Inactif'}
                                                </span>
                                            </td>
                                            <td>{user['created_at']}</td>
                                            <td>
                                                <div class="btn-group btn-group-sm">
                                                    <button class="btn btn-outline-primary" onclick="editUser({user['id']})" title="Modifier">
                                                        <i class="bi bi-pencil"></i>
                                                    </button>
                                                    <button class="btn btn-outline-danger" onclick="deleteUser({user['id']}, '{user['username']}')" title="Supprimer">
                                                        <i class="bi bi-trash"></i>
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>""" for user in users_data]) + """
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        console.log('Script chargé');
        
        // Version ultra-simple qui marche à coup sûr
        window.onload = function() {
            console.log('Page complètement chargée');
            
            // Bouton créer utilisateur
            const btn = document.getElementById('createUserBtn');
            console.log('Bouton:', btn);
            
            if (btn) {
                btn.onclick = function() {
                    console.log('CLIC DETECTE !');
                    alert('Bouton cliqué ! Modal va s\'ouvrir...');
                    
                    const modal = document.getElementById('createUserModal');
                    if (modal) {
                        const bsModal = new bootstrap.Modal(modal);
                        bsModal.show();
                        console.log('Modal ouvert');
                    } else {
                        alert('Modal non trouvé !');
                    }
                };
            } else {
                console.error('BOUTON NON TROUVE !');
                alert('Bouton non trouvé !');
            }
            
            // Formulaire
            const form = document.getElementById('createUserForm');
            if (form) {
                form.onsubmit = async function(e) {
                    e.preventDefault();
                    console.log('Formulaire soumis');
                    
                    const formData = new FormData(form);
                    const submitBtn = form.querySelector('button[type="submit"]');
                    
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = 'Création...';
                    
                    try {
                        const response = await fetch('/admin/users/create', {
                            method: 'POST',
                            body: formData
                        });
                        
                        if (response.ok) {
                            alert('Utilisateur créé avec succès !');
                            window.location.reload();
                        } else {
                            const error = await response.json();
                            alert('Erreur: ' + (error.detail || 'Erreur inconnue'));
                        }
                    } catch (error) {
                        console.error('Erreur:', error);
                        alert('Erreur de connexion');
                    } finally {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '<i class="bi bi-check-lg me-2"></i>Créer l\'utilisateur';
                    }
                };
            }
        };
        
        // Fonctions pour les boutons du tableau
        function editUser(id) {
            alert('Édition utilisateur ' + id + ' (en développement)');
        }

        function deleteUser(id, username) {
            if (confirm('Supprimer ' + username + ' ?')) {
                alert('Suppression (en développement)');
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@admin_router.get("/api/users")
async def admin_users_data(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Données des utilisateurs pour l'interface d'administration"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    roles = db.query(Role).all()
    
    # Enrichir les utilisateurs avec leurs rôles
    users_data = []
    for user in users:
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        user_role_names = []
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                user_role_names.append(role.name)
        
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat(),
            "roles": user_role_names
        })
    
    roles_data = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description
        } for role in roles
    ]
    
    return {
        "users": users_data,
        "roles": roles_data
    }

@admin_router.post("/users/create")
async def create_user_admin(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: Optional[str] = Form(None),
    is_active: bool = Form(True),
    is_admin: bool = Form(False),
    role_ids: List[int] = Form([]),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Créer un nouvel utilisateur (admin)"""
    
    # Vérifier si l'utilisateur existe déjà
    if UserCRUD.get_user_by_username(db, username):
        raise HTTPException(
            status_code=400,
            detail="Un utilisateur avec ce nom d'utilisateur existe déjà"
        )
    
    if UserCRUD.get_user_by_email(db, email):
        raise HTTPException(
            status_code=400,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Créer l'utilisateur
    try:
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_active=is_active,
            is_admin=is_admin
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    user = UserCRUD.create_user(db, user_data)
    
    # Assigner les rôles
    for role_id in role_ids:
        UserCRUD.assign_role(db, user.id, role_id)
    
    return {"message": "Utilisateur créé avec succès", "user_id": user.id}

@admin_router.post("/users/{user_id}/update")
async def update_user_admin(
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    is_active: bool = Form(True),
    is_admin: bool = Form(False),
    password: Optional[str] = Form(None),
    role_ids: List[int] = Form([]),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Mettre à jour un utilisateur (admin)"""
    
    user = UserCRUD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Préparer les données de mise à jour
    update_data = {
        "username": username,
        "email": email,
        "is_active": is_active,
        "is_admin": is_admin
    }
    
    if password:
        update_data["hashed_password"] = get_password_hash(password)
    
    # Mettre à jour l'utilisateur
    UserCRUD.update_user(db, user_id, UserUpdate(**update_data))
    
    # Mettre à jour les rôles
    # Supprimer les anciens rôles
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    # Ajouter les nouveaux rôles
    for role_id in role_ids:
        UserCRUD.assign_role(db, user_id, role_id)
    
    db.commit()
    
    return {"message": "Utilisateur mis à jour avec succès"}

@admin_router.post("/users/{user_id}/delete")
async def delete_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Supprimer un utilisateur (admin)"""
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )
    
    user = UserCRUD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Supprimer les rôles de l'utilisateur
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    # Supprimer l'utilisateur
    UserCRUD.delete_user(db, user_id)
    
    return {"message": "Utilisateur supprimé avec succès"}

@admin_router.get("/logs", response_class=HTMLResponse)
async def admin_logs(request: Request):
    """Page des logs de recherche"""
    html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logs de recherche - Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { 
            background-color: #fafafa; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
            margin: 0;
            padding: 0;
            color: #2c3e50;
            line-height: 1.6;
        }
        .sidebar { 
            background-color: #ffffff; 
            min-height: 100vh; 
            border-right: 1px solid #e8ecef; 
            box-shadow: 0 0 20px rgba(0,0,0,0.04);
        }
        .main-content { 
            background-color: #ffffff; 
            border-radius: 12px; 
            margin: 24px; 
            padding: 32px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #f1f3f4;
        }
        .nav-link { 
            border-radius: 8px; 
            margin: 2px 0; 
            transition: all 0.2s ease;
            color: #6b7280;
            font-weight: 500;
            padding: 12px 16px;
        }
        .nav-link:hover { 
            background-color: #f8f9fa; 
            color: #374151;
            transform: translateX(2px);
        }
        .nav-link.active { 
            background-color: #f8f9ff; 
            color: #6366f1;
            border-left: 3px solid #6366f1;
        }
        .page-header {
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 20px;
            margin-bottom: 32px;
        }
        .page-title {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin: 0;
        }
        .page-subtitle {
            font-size: 14px;
            color: #6b7280;
            margin-top: 4px;
        }
        .stats-card { 
            border: 1px solid #e8ecef; 
            border-radius: 12px; 
            background: #ffffff;
            transition: all 0.3s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .stats-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stats-card .card-body {
            padding: 24px;
        }
        .stats-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            font-size: 24px;
        }
        .icon-search { background: #fef3c7; color: #f59e0b; }
        .icon-users { background: #f0fdf4; color: #22c55e; }
        .icon-globe { background: #ecfdf5; color: #10b981; }
        .icon-speed { background: #fef2f2; color: #ef4444; }
        .stats-number {
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 4px;
        }
        .stats-label {
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }
        .table {
            border-radius: 8px;
            overflow: hidden;
        }
        .table th {
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            font-weight: 600;
            color: #374151;
        }
        .user-avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #6366f1;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 12px;
        }
        .badge {
            font-weight: 500;
            padding: 4px 8px;
        }
        .card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .card-header {
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            border-radius: 12px 12px 0 0;
            padding: 16px 24px;
        }
        .card-body {
            padding: 24px;
        }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <div class="container-fluid p-0">
        <div class="row g-0">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2">
                <div class="sidebar p-3">
                    <div class="text-center mb-4">
                        <h4><i class="bi bi-shield-check text-primary"></i> Admin Panel</h4>
                    </div>
                    <nav class="nav nav-pills flex-column">
                        <a class="nav-link" href="/admin/">
                            <i class="bi bi-speedometer2 me-2"></i> Dashboard
                        </a>
                        <a class="nav-link" href="/admin/users">
                            <i class="bi bi-people me-2"></i> Utilisateurs
                        </a>
                        <a class="nav-link active" href="/admin/logs">
                            <i class="bi bi-journal-text me-2"></i> Logs de recherche
                        </a>
                        <hr class="my-3">
                        <a class="nav-link" href="/docs" target="_blank">
                            <i class="bi bi-book me-2"></i> Documentation API
                        </a>
                        <a class="nav-link" href="/login">
                            <i class="bi bi-box-arrow-right me-2"></i> Déconnexion
                        </a>
                    </nav>
                    <div class="mt-auto pt-4">
                        <div class="d-flex align-items-center">
                            <div class="me-2" style="width:36px;height:36px;background:#6c757d;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:600;">A</div>
                            <div>
                                <small class="d-block fw-semibold">admin</small>
                                <small class="text-muted">Administrateur</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10">
                <div class="main-content">
                    <div class="page-header">
                        <h1 class="page-title">Logs de recherche</h1>
                        <p class="page-subtitle">Analysez l'activité de recherche sémantique</p>
                    </div>

                    <!-- Statistiques -->
                    <div class="row mb-5">
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-search">
                                        <i class="bi bi-search"></i>
                                    </div>
                                    <div class="stats-number" id="totalSearches">0</div>
                                    <div class="stats-label">Recherches totales</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-users">
                                        <i class="bi bi-people"></i>
                                    </div>
                                    <div class="stats-number" id="authSearches">0</div>
                                    <div class="stats-label">Recherches authentifiées</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-globe">
                                        <i class="bi bi-globe"></i>
                                    </div>
                                    <div class="stats-number" id="uniqueLanguages">0</div>
                                    <div class="stats-label">Langues utilisées</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-4">
                            <div class="card stats-card">
                                <div class="card-body text-center">
                                    <div class="stats-icon icon-speed">
                                        <i class="bi bi-speedometer"></i>
                                    </div>
                                    <div class="stats-number" id="avgTime">0</div>
                                    <div class="stats-label">Temps moyen (ms)</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tableau des logs -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-journal-text me-2"></i>
                                Historique des recherches (100 dernières)
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Date/Heure</th>
                                            <th>Utilisateur</th>
                                            <th>Requête</th>
                                            <th>Langue</th>
                                            <th>Résultats</th>
                                            <th>Temps (ms)</th>
                                        </tr>
                                    </thead>
                                    <tbody id="logsTableBody">
                                        <tr>
                                            <td colspan="6" class="text-center py-4">
                                                <div class="spinner-border text-primary" role="status">
                                                    <span class="visually-hidden">Chargement...</span>
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Données statiques pour les logs (pour éviter les appels AJAX)
        const logsData = {
            total_searches: 0,
            auth_searches: 0,
            unique_languages: 2,
            avg_response_time: 0,
            recent_searches: []
        };
        
        // Charger les logs
        function loadLogs() {
            try {
                displayStats(logsData);
                displayLogs(logsData.recent_searches || []);
            } catch (error) {
                console.error('Erreur lors du chargement des logs:', error);
                document.getElementById('logsTableBody').innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-4">
                            <i class="bi bi-exclamation-triangle display-4 text-warning"></i>
                            <p class="text-muted mt-2">Erreur lors du chargement des logs</p>
                        </td>
                    </tr>
                `;
            }
        }

        // Afficher les statistiques
        function displayStats(stats) {
            document.getElementById('totalSearches').textContent = stats.total_searches || 0;
            
            // Calculer les recherches authentifiées
            const authSearches = (stats.recent_searches || []).filter(search => search.user_id).length;
            document.getElementById('authSearches').textContent = authSearches;
            
            // Calculer les langues uniques
            const languages = new Set((stats.recent_searches || []).map(search => search.language));
            document.getElementById('uniqueLanguages').textContent = languages.size;
            
            // Calculer le temps moyen
            const searches = stats.recent_searches || [];
            const avgTime = searches.length > 0 
                ? Math.round(searches.reduce((sum, search) => sum + search.response_time, 0) / searches.length)
                : 0;
            document.getElementById('avgTime').textContent = avgTime;
        }

        // Afficher les logs
        function displayLogs(logs) {
            const tbody = document.getElementById('logsTableBody');
            
            if (logs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-4">
                            <i class="bi bi-search display-4 text-muted"></i>
                            <p class="text-muted mt-2">Aucun log de recherche disponible</p>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = logs.map(log => `
                <tr>
                    <td>
                        <small class="text-muted">${new Date(log.created_at).toLocaleString('fr-FR')}</small>
                    </td>
                    <td>
                        <span class="text-muted">Anonyme</span>
                    </td>
                    <td>
                        <span class="text-truncate" style="max-width: 200px; display: inline-block;" title="${log.query}">
                            ${log.query}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-info">${log.language.toUpperCase()}</span>
                    </td>
                    <td>
                        <span class="badge bg-success">N/A</span>
                    </td>
                    <td>
                        <span class="badge ${log.response_time < 500 ? 'bg-success' : log.response_time < 1000 ? 'bg-warning' : 'bg-danger'}">
                            ${log.response_time}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        // Initialisation
        document.addEventListener('DOMContentLoaded', loadLogs);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@admin_router.get("/api/stats")
async def admin_api_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """API pour récupérer les statistiques (pour les graphiques)"""
    
    # Statistiques par jour (7 derniers jours)
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    daily_stats = db.query(
        func.date(SearchLog.created_at).label('date'),
        func.count(SearchLog.id).label('searches')
    ).filter(
        SearchLog.created_at >= start_date
    ).group_by(
        func.date(SearchLog.created_at)
    ).order_by('date').all()
    
    # Statistiques par langue
    language_stats = db.query(
        SearchLog.language,
        func.count(SearchLog.id).label('count')
    ).group_by(SearchLog.language).all()
    
    # Temps de réponse moyen
    avg_response_time = db.query(
        func.avg(SearchLog.response_time)
    ).scalar() or 0
    
    return {
        "daily_stats": [{"date": str(stat.date), "searches": stat.searches} for stat in daily_stats],
        "language_stats": [{"language": stat.language, "count": stat.count} for stat in language_stats],
        "avg_response_time": round(avg_response_time, 2)
    } 