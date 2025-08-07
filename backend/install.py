#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'installation automatique pour le moteur de recherche sémantique
"""

import subprocess
import sys
import os
import platform

def run_command(command, description=""):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur:")
        print(f"   {e.stderr}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    print(f"🐍 Version Python détectée: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ requis")
        return False
    
    print("✅ Version Python compatible")
    return True

def detect_gpu():
    """Détecte si un GPU NVIDIA est disponible"""
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("🎮 GPU NVIDIA détecté")
            return True
    except:
        pass
    
    print("💻 Pas de GPU NVIDIA détecté - Installation CPU")
    return False

def install_dependencies(use_gpu=False):
    """Installe les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    # Mettre à jour pip
    if not run_command("python -m pip install --upgrade pip", "Mise à jour de pip"):
        return False
    
    # Installer les dépendances de base
    base_packages = [
        "numpy>=1.18.0",
        "sentence-transformers>=2.2.2",
        "langdetect>=1.0.9",
        "fastapi>=0.70.0",
        "uvicorn>=0.15.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "sqlalchemy>=1.4.0",
        "alembic>=1.8.0",
        "python-dotenv>=0.19.0",
        "requests>=2.25.0"
    ]
    
    for package in base_packages:
        if not run_command(f"pip install {package}", f"Installation de {package.split('>=')[0]}"):
            print(f"⚠️  Échec de l'installation de {package}")
    
    # Installer FAISS
    if use_gpu:
        print("🎮 Installation de FAISS GPU...")
        if not run_command("pip install faiss-gpu>=1.7.1", "Installation de FAISS GPU"):
            print("⚠️  Échec de FAISS GPU, installation de la version CPU...")
            run_command("pip install faiss-cpu>=1.7.1", "Installation de FAISS CPU (fallback)")
    else:
        run_command("pip install faiss-cpu>=1.7.1", "Installation de FAISS CPU")
    
    return True

def test_installation():
    """Teste l'installation"""
    print("\n🧪 Test de l'installation...")
    
    tests = [
        ("import numpy", "NumPy"),
        ("import faiss", "FAISS"),
        ("import sentence_transformers", "Sentence Transformers"),
        ("import fastapi", "FastAPI"),
        ("import uvicorn", "Uvicorn"),
        ("import jose", "python-jose"),
        ("import passlib", "Passlib"),
        ("import sqlalchemy", "SQLAlchemy"),
        ("import dotenv", "python-dotenv"),
        ("import requests", "Requests")
    ]
    
    success_count = 0
    for test_code, package_name in tests:
        try:
            exec(test_code)
            print(f"✅ {package_name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package_name} - {e}")
    
    print(f"\n📊 Résultat: {success_count}/{len(tests)} packages installés correctement")
    return success_count == len(tests)

def create_env_file():
    """Crée le fichier .env s'il n'existe pas"""
    if not os.path.exists('.env'):
        print("📄 Création du fichier .env...")
        try:
            with open('env.example', 'r') as source:
                content = source.read()
            with open('.env', 'w') as target:
                target.write(content)
            print("✅ Fichier .env créé")
        except FileNotFoundError:
            print("⚠️  Fichier env.example non trouvé")
    
    # Vérifier et ajouter la variable OpenMP si nécessaire
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        if 'KMP_DUPLICATE_LIB_OK' not in content:
            print("🔧 Ajout de la configuration OpenMP...")
            with open('.env', 'a') as f:
                f.write('\n# Configuration OpenMP pour éviter les conflits\n')
                f.write('KMP_DUPLICATE_LIB_OK=TRUE\n')
            print("✅ Configuration OpenMP ajoutée")
    except:
        pass

def main():
    """Fonction principale d'installation"""
    print("🚀 Installation du moteur de recherche sémantique")
    print("=" * 60)
    
    # Vérifier Python
    if not check_python_version():
        return False
    
    # Détecter GPU
    has_gpu = detect_gpu()
    
    # Demander confirmation pour GPU
    if has_gpu:
        response = input("\n🎮 GPU détecté. Installer la version GPU de FAISS ? (y/N): ")
        use_gpu = response.lower() in ['y', 'yes', 'oui']
    else:
        use_gpu = False
    
    # Installer les dépendances
    if not install_dependencies(use_gpu):
        print("❌ Échec de l'installation des dépendances")
        return False
    
    # Tester l'installation
    if not test_installation():
        print("⚠️  Certains packages ne sont pas installés correctement")
        print("💡 Consultez install_guide.md pour le dépannage")
    
    # Créer le fichier .env
    create_env_file()
    
    # Instructions finales
    print("\n" + "=" * 60)
    print("🎉 Installation terminée !")
    print("\n📋 Prochaines étapes :")
    print("1. Initialiser la base de données :")
    print("   python init_auth.py")
    print("\n2. Démarrer le serveur :")
    print("   python main.py --mode api")
    print("\n3. Tester l'installation :")
    print("   python test_auth.py")
    print("\n4. Accéder à la documentation :")
    print("   http://localhost:8000/docs")
    print("\n🔐 Compte par défaut : admin / admin123")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        print("💡 Consultez install_guide.md pour le dépannage")
        sys.exit(1) 