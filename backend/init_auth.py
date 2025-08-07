#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation pour le système d'authentification
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Charger les variables d'environnement
load_dotenv()

def init_database():
    """Initialise la base de données avec les données par défaut"""
    try:
        from src.auth.database import init_db, SessionLocal
        from src.auth.crud import UserCRUD
        from src.auth.schemas import UserCreate
        
        print("🔄 Initialisation de la base de données...")
        init_db()
        print("✅ Base de données initialisée avec succès !")
        
        # Créer un utilisateur admin par défaut
        print("🔄 Création de l'utilisateur admin par défaut...")
        db = SessionLocal()
        try:
            # Vérifier si l'admin existe déjà
            existing_admin = UserCRUD.get_user_by_email(db, "admin@example.com")
            if existing_admin:
                print("✅ Utilisateur admin existe déjà")
                print(f"   - Email : {existing_admin.email}")
                print(f"   - Token API : {existing_admin.api_token}")
                return True
            
            # Créer l'admin par défaut
            admin_data = UserCreate(
                email="admin@example.com",
                username="admin",
                full_name="Administrateur Principal",
                password="admin123",
                is_admin=True
            )
            
            user = UserCRUD.create_user(db, admin_data)
            print("✅ Utilisateur admin créé avec succès !")
            print(f"   - Email : {user.email}")
            print(f"   - Token API : {user.api_token}")
            print(f"   - Mot de passe : admin123")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        return False

def create_user_interactive():
    """Crée un utilisateur de manière interactive"""
    try:
        from src.auth.database import SessionLocal, init_db
        from src.auth.crud import UserCRUD
        from src.auth.schemas import UserCreate
        
        print("\n🧑‍💼 Création d'un nouvel utilisateur")
        print("=" * 40)
        
        email = input("📧 Email : ")
        username = input("👤 Nom d'utilisateur : ")
        full_name = input("🏷️  Nom complet (optionnel) : ")
        password = input("🔒 Mot de passe : ")
        
        if not full_name:
            full_name = None
        
        user_data = UserCreate(
            email=email,
            username=username,
            full_name=full_name,
            password=password,
            is_admin=True
        )
        
        db = SessionLocal()
        try:
            # Vérifier si l'utilisateur existe déjà
            if UserCRUD.get_user_by_email(db, email):
                print(f"❌ Un utilisateur avec l'email {email} existe déjà")
                return False
            
            if UserCRUD.get_user_by_username(db, username):
                print(f"❌ Un utilisateur avec le nom d'utilisateur {username} existe déjà")
                return False
            
            user = UserCRUD.create_user(db, user_data)
            print(f"✅ Utilisateur créé avec succès !")
            print(f"   - ID : {user.id}")
            print(f"   - Email : {user.email}")
            print(f"   - Nom d'utilisateur : {user.username}")
            print(f"   - Nom complet : {user.full_name}")
            print(f"   - Token API : {user.api_token}")
            print(f"   - Admin : {'Oui' if user.is_admin else 'Non'}")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur : {e}")
        return False

def show_menu():
    """Affiche le menu principal"""
    print("\n🔐 Système d'authentification - Menu principal")
    print("=" * 50)
    print("1. Initialiser la base de données")
    print("2. Créer un nouvel utilisateur")
    print("3. Afficher les informations de connexion")
    print("4. Quitter")
    print("=" * 50)

def show_connection_info():
    """Affiche les informations de connexion"""
    print("\n🌐 Informations de connexion")
    print("=" * 40)
    print("URL de l'API : http://localhost:8000")
    print("Documentation : http://localhost:8000/docs")
    print("Redoc : http://localhost:8000/redoc")
    print("\n🔐 Compte admin par défaut :")
    print("   - Nom d'utilisateur : admin")
    print("   - Mot de passe : admin123")
    print("   - Email : admin@example.com")
    print("\n📝 Endpoints principaux :")
    print("   - POST /auth/login - Connexion")
    print("   - POST /search - Recherche (authentifié)")
    print("   - POST /search/public - Recherche publique")
    print("   - GET /auth/me - Profil utilisateur")

def main():
    """Fonction principale"""
    print("🚀 Initialisation du moteur de recherche sémantique")
    print("   Version 2.0.0 avec authentification")
    
    while True:
        show_menu()
        choice = input("\nChoisissez une option (1-4) : ").strip()
        
        if choice == "1":
            init_database()
        elif choice == "2":
            create_user_interactive()
        elif choice == "3":
            show_connection_info()
        elif choice == "4":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Option invalide, veuillez choisir entre 1 et 4")

if __name__ == "__main__":
    main() 