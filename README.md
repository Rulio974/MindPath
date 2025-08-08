# MindPath - Recherche Sémantique

## 📋 Vue d'ensemble

MindPath est une solution de recherche sémantique multilingue (FR/EN) avec pondération temporelle, re-ranking et détection automatique de langue. Le projet est architecturé en 3 modules indépendants déployés sur 3 serveurs distincts.

## 🏗️ Architecture

### **Module 1 : Embeddings** (`embeddings/`)
- **Serveur** : Serveur de chargement des embeddings
- **Fonctionnalité** : Chargement et indexation des données sémantiques
- **Technologies** : Python, FAISS, Sentence Transformers

### **Module 2 : Backend** (`backend/`)
- **Serveur** : API REST avec interface d'administration
- **URL** : `https://api.mindpath-dev.fr`
- **Fonctionnalités** :
  - Recherche sémantique via API
  - Authentification par tokens API
  - Interface d'administration (gestion utilisateurs)
  - Logs de recherche
- **Technologies** : FastAPI, SQLAlchemy, SQLite, Uvicorn

### **Module 3 : Frontend** (`frontend/`)
- **Serveur** : Interface Excel Add-in
- **URL** : `https://mindpath-dev.fr`
- **Fonctionnalités** :
  - Add-in Excel pour recherche sémantique
  - Interface utilisateur moderne
  - Intégration avec Office.js
- **Technologies** : HTML5, CSS3, JavaScript, Office.js

## 🚀 Démarrage rapide

### **1. Backend (API + Admin)**
```bash
cd backend
pip install -r requirements.txt
python3 init_auth.py  # Initialiser la base de données
python3 main.py --mode api
```

### **2. Frontend (Excel Add-in)**
```bash
cd frontend
npm install
npm start
```

## 🔐 Authentification

### **Types d'utilisateurs**
- **Admin** : Accès complet à l'interface d'administration
- **Standard** : Accès à la recherche sémantique uniquement

### **Mécanismes d'authentification**
- **Interface Admin** : Email/Mot de passe + sessions
- **API Recherche** : Tokens API uniquement
- **Excel Add-in** : Tokens API pour les requêtes

## 📁 Structure du projet

```
MindPath/
├── embeddings/          # Module embeddings
├── backend/            # Module backend (API + Admin)
│   ├── src/
│   │   ├── api.py      # API principale
│   │   ├── auth/       # Authentification
│   │   └── admin.py    # Interface admin (déprécié)
│   ├── main.py         # Point d'entrée
│   └── requirements.txt
├── frontend/           # Module Excel Add-in
│   ├── taskpane.html   # Interface utilisateur
│   ├── taskpane.js     # Logique JavaScript
│   ├── taskpane.css    # Styles
│   ├── manifest.xml    # Manifest Excel
│   └── package.json
└── admin/              # Interface admin standalone
    ├── index.html      # Dashboard admin
    └── login.html      # Page de connexion
```

## 🌐 URLs de production

### **Interface d'administration**
- **URL** : `https://mindpath-dev.fr`
- **Fonctionnalités** : Gestion des utilisateurs, statistiques, génération de tokens

### **API Backend**
- **URL** : `https://api.mindpath-dev.fr`
- **Endpoints** :
  - `POST /search` : Recherche sémantique
  - `GET /stats` : Statistiques (admin)
  - `POST /auth/login` : Connexion admin
  - `GET /auth/verify-api-token` : Vérification token API

### **Excel Add-in**
- **URL** : `https://mindpath-dev.fr/taskpane.html`
- **Manifest** : `https://mindpath-dev.fr/manifest.xml`

## ⚠️ IMPORTANT - Certificats SSL en production

**Pour la production, vous DEVEZ remplacer les certificats auto-signés par des certificats Let's Encrypt valides :**

1. **Remplacer les certificats** :
   - `backend/certs/backend.key` → Certificat Let's Encrypt
   - `backend/certs/backend.crt` → Certificat Let's Encrypt

2. **Configurer Nginx** pour gérer SSL et rediriger vers le backend en HTTP

3. **Mettre à jour les URLs frontend** pour utiliser HTTPS

## 🚀 Plan détaillé pour la migration en production (après propagation DNS)

### **Étape 1 : Vérification DNS**
```bash
nslookup mindpath-dev.fr
nslookup api.mindpath-dev.fr
```

### **Étape 2 : Configuration Nginx**
```bash
sudo nano /etc/nginx/sites-available/mindpath-dev.fr
sudo nano /etc/nginx/sites-available/api.mindpath-dev.fr
```

### **Étape 3 : Activation des sites**
```bash
sudo ln -s /etc/nginx/sites-available/mindpath-dev.fr /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api.mindpath-dev.fr /etc/nginx/sites-enabled/
```

### **Étape 4 : Test Nginx**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### **Étape 5 : Certificats SSL**
```bash
sudo certbot --nginx -d mindpath-dev.fr
sudo certbot --nginx -d api.mindpath-dev.fr
```

### **Étape 6 : Modification backend**
- Modifier le backend pour écouter en HTTP (Nginx gère SSL)
- Redémarrer le service backend

### **Étape 7 : Mise à jour frontend**
- Vérifier que les URLs pointent vers les bons domaines
- Tester l'interface admin et l'add-in Excel

### **Étape 8 : Redémarrage des services**
```bash
sudo systemctl restart mindpath-backend
sudo systemctl reload nginx
```

### **Étape 9 : Tests finaux**
- Test de l'interface admin
- Test de l'API
- Test de l'add-in Excel
- Test des certificats SSL

## 🔧 Configuration Nginx

### **Site principal (mindpath-dev.fr)**
```nginx
server {
    listen 80;
    server_name mindpath-dev.fr;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name mindpath-dev.fr;
    
    ssl_certificate /etc/letsencrypt/live/mindpath-dev.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mindpath-dev.fr/privkey.pem;
    
    root /home/ubuntu/MindPath/admin;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location /assets/ {
        alias /home/ubuntu/MindPath/frontend/assets/;
    }
}
```

### **API (api.mindpath-dev.fr)**
```nginx
server {
    listen 80;
    server_name api.mindpath-dev.fr;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.mindpath-dev.fr;
    
    ssl_certificate /etc/letsencrypt/live/api.mindpath-dev.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.mindpath-dev.fr/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Fonctionnalités

### **Recherche sémantique**
- **Multilingue** : Français et Anglais
- **Pondération temporelle** : Priorité aux documents récents
- **Re-ranking** : Amélioration de la pertinence
- **Détection de langue** : Automatique

### **Interface d'administration**
- **Gestion des utilisateurs** : Création, modification, suppression
- **Génération de tokens** : Tokens API sécurisés
- **Statistiques** : Nombre d'utilisateurs, entrées, documents
- **Logs** : Historique des recherches

### **Excel Add-in**
- **Recherche intégrée** : Dans les cellules Excel
- **Auto-remplissage** : Colonnes réponse et commentaire
- **Paramètres persistants** : URL serveur et token API
- **Interface moderne** : Design Bootstrap 5

## 🔒 Sécurité

- **Tokens API** : Génération sécurisée et rotation
- **Hachage des mots de passe** : bcrypt
- **Sessions admin** : Gestion en mémoire
- **CORS** : Configuration stricte
- **HTTPS** : Obligatoire en production

## 📝 Logs

### **Backend**
- Logs de recherche dans la base SQLite
- Logs d'authentification
- Logs d'erreurs

### **Frontend**
- Logs de connexion dans la console
- Logs d'erreurs utilisateur

## 🚀 Déploiement

### **Services systemd**
```bash
# Backend
sudo systemctl enable mindpath-backend
sudo systemctl start mindpath-backend

# Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### **Monitoring**
```bash
# Vérifier les services
sudo systemctl status mindpath-backend
sudo systemctl status nginx

# Vérifier les logs
sudo journalctl -u mindpath-backend -f
sudo tail -f /var/log/nginx/error.log
``` 