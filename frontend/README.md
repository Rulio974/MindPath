# Add-in Excel MindPath - Recherche Sémantique

## 🚀 Nouveautés v3.0

### 🔐 Authentification par Token API
- **Onglet Paramètres** : Configuration du serveur et du token API
- **Persistance** : Les paramètres sont sauvegardés localement
- **Sécurité** : Token masqué par défaut avec option de visibilité

### 📋 Fonctionnalités

#### Onglet Recherche
- Recherche sémantique dans les questionnaires de sécurité
- Sélection intelligente : clic sur une cellule → recherche automatique
- Remplissage automatique configurable
- Options avancées pliables

#### Onglet Paramètres
- **URL du serveur** : Adresse de l'API MindPath
- **Token API** : Token d'authentification (masqué par défaut)
- **Test de connexion** : Vérification de la connectivité
- **Sauvegarde** : Persistance des paramètres

### 🔧 Configuration

1. **Première utilisation** : L'add-in bascule automatiquement vers l'onglet Paramètres
2. **URL du serveur** : 
   - Développement : `http://localhost:8000`
   - Production : `https://api.lesphinx.mindpath.fr`
3. **Token API** : Récupéré depuis l'interface d'administration
4. **Test** : Utilisez le bouton "Tester la connexion" pour vérifier

### 💾 Persistance des Données
- **localStorage** : Sauvegarde automatique des paramètres
- **Sessions** : Les paramètres persistent entre les fermetures d'Excel
- **Sécurité** : Token chiffré dans le stockage local

### 🛠️ Architecture
- **Frontend** : Add-in Excel (HTTPS localhost:3000)
- **Backend** : API MindPath (configurable)
- **Authentification** : Bearer Token dans les headers
- **CORS** : Configuration pour les appels directs

### 📦 Déploiement
```bash
npm install
npm start          # Développement
npm run build      # Build exécutable
```

### 🔍 Utilisation
1. Configurer le serveur et le token dans l'onglet Paramètres
2. Basculer vers l'onglet Recherche
3. Cliquer sur une cellule contenant une question
4. La réponse s'affiche automatiquement
5. Optionnel : configurer le remplissage automatique

### 🚨 Gestion d'Erreurs
- **401** : Token API invalide
- **403** : Permissions insuffisantes
- **Connexion** : Erreur de réseau ou serveur inaccessible
- **Configuration** : Paramètres manquants ou invalides

