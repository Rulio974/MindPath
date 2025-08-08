# 🚀 Checklist de déploiement - mindpath-dev.fr

## 📋 Prérequis

### **1. Achat du domaine**
- [ ] Acheter le domaine `mindpath-dev.fr` chez un registrar (OVH, Namecheap, etc.)
- [ ] Vérifier que le domaine est actif et configurable

### **2. Configuration DNS**
- [ ] Ajouter les enregistrements A dans la zone DNS :
  ```
  A record: mindpath-dev.fr → 164.132.58.187
  A record: api.mindpath-dev.fr → 164.132.58.187
  ```
- [ ] Attendre la propagation DNS (peut prendre 24-48h)

## 🔧 Configuration serveur

### **3. Installation des dépendances**
```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Nginx et Certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# Vérifier que Nginx fonctionne
sudo systemctl status nginx
```

### **4. Configuration Nginx**
```bash
# Copier les configurations
sudo cp nginx-mindpath-dev.fr.conf /etc/nginx/sites-available/mindpath-dev.fr
sudo cp nginx-api.mindpath-dev.fr.conf /etc/nginx/sites-available/api.mindpath-dev.fr

# Activer les sites
sudo ln -s /etc/nginx/sites-available/mindpath-dev.fr /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api.mindpath-dev.fr /etc/nginx/sites-enabled/

# Supprimer le site par défaut si nécessaire
sudo rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### **5. Obtention des certificats SSL**
```bash
# Certificat pour le site principal
sudo certbot --nginx -d mindpath-dev.fr

# Certificat pour l'API
sudo certbot --nginx -d api.mindpath-dev.fr

# Vérifier les certificats
sudo certbot certificates
```

### **6. Configuration du backend**
```bash
# Arrêter le backend actuel
cd /home/ubuntu/MindPath/backend
pkill -f "python.*main.py"

# Modifier le backend pour écouter en HTTP (Nginx gère SSL)
# Les fichiers sont déjà configurés pour détecter automatiquement les certificats

# Redémarrer le backend
python3 main.py --mode api
```

### **7. Création du service systemd**
```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/mindpath-backend.service
```

**Contenu du service :**
```ini
[Unit]
Description=MindPath Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MindPath/backend
ExecStart=/usr/bin/python3 main.py --mode api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable mindpath-backend
sudo systemctl start mindpath-backend

# Vérifier le statut
sudo systemctl status mindpath-backend
```

## 🎨 Préparation des assets

### **8. Création des icônes**
- [ ] Créer les icônes PNG aux bonnes dimensions :
  - `frontend/assets/icon-16.png` (16x16 pixels)
  - `frontend/assets/icon-32.png` (32x32 pixels)
  - `frontend/assets/icon-80.png` (80x80 pixels)
- [ ] Utiliser le logo MindPath avec fond transparent
- [ ] Vérifier que les fichiers sont accessibles via HTTPS

### **9. Vérification des fichiers**
```bash
# Vérifier que tous les fichiers sont en place
ls -la /home/ubuntu/MindPath/admin/
ls -la /home/ubuntu/MindPath/frontend/
ls -la /home/ubuntu/MindPath/frontend/assets/

# Vérifier les permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/MindPath/
chmod 644 /home/ubuntu/MindPath/admin/*.html
chmod 644 /home/ubuntu/MindPath/frontend/*.html
chmod 644 /home/ubuntu/MindPath/frontend/*.css
chmod 644 /home/ubuntu/MindPath/frontend/*.js
chmod 644 /home/ubuntu/MindPath/frontend/*.xml
```

## 🧪 Tests

### **10. Tests DNS**
```bash
# Vérifier la propagation DNS
nslookup mindpath-dev.fr
nslookup api.mindpath-dev.fr

# Tester la résolution
ping mindpath-dev.fr
ping api.mindpath-dev.fr
```

### **11. Tests SSL**
```bash
# Vérifier les certificats
curl -I https://mindpath-dev.fr
curl -I https://api.mindpath-dev.fr

# Tester avec openssl
openssl s_client -connect mindpath-dev.fr:443 -servername mindpath-dev.fr
openssl s_client -connect api.mindpath-dev.fr:443 -servername api.mindpath-dev.fr
```

### **12. Tests fonctionnels**
```bash
# Test de l'interface admin
curl -I https://mindpath-dev.fr

# Test de l'API
curl -I https://api.mindpath-dev.fr/health

# Test de l'authentification
curl -X POST https://api.mindpath-dev.fr/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Test de recherche (avec un token valide)
curl -X POST https://api.mindpath-dev.fr/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question":"test","top_k":1}'
```

### **13. Tests Excel Add-in**
- [ ] Tester l'add-in dans Excel Online
- [ ] Vérifier que le manifest.xml est accessible
- [ ] Tester la connexion avec l'API
- [ ] Vérifier que les icônes s'affichent correctement

## 📊 Monitoring

### **14. Configuration des logs**
```bash
# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/mindpath-dev.fr.access.log
sudo tail -f /var/log/nginx/api.mindpath-dev.fr.access.log

# Vérifier les logs du backend
sudo journalctl -u mindpath-backend -f

# Vérifier les erreurs Nginx
sudo tail -f /var/log/nginx/error.log
```

### **15. Surveillance**
```bash
# Vérifier les services
sudo systemctl status nginx
sudo systemctl status mindpath-backend

# Vérifier l'espace disque
df -h

# Vérifier la mémoire
free -h
```

## 🔄 Maintenance

### **16. Renouvellement automatique des certificats**
```bash
# Tester le renouvellement automatique
sudo certbot renew --dry-run

# Ajouter au crontab si nécessaire
sudo crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

### **17. Sauvegarde**
```bash
# Créer un script de sauvegarde
nano /home/ubuntu/backup-mindpath.sh
```

**Contenu du script :**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"

mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
cp /home/ubuntu/MindPath/backend/semantic_search.db $BACKUP_DIR/semantic_search_$DATE.db

# Sauvegarder les configurations
tar -czf $BACKUP_DIR/mindpath_config_$DATE.tar.gz \
  /home/ubuntu/MindPath/admin/ \
  /home/ubuntu/MindPath/frontend/ \
  /home/ubuntu/MindPath/backend/src/ \
  /etc/nginx/sites-available/mindpath-dev.fr \
  /etc/nginx/sites-available/api.mindpath-dev.fr

echo "Sauvegarde terminée : $DATE"
```

```bash
# Rendre le script exécutable
chmod +x /home/ubuntu/backup-mindpath.sh

# Ajouter au crontab pour une sauvegarde quotidienne
crontab -e
# Ajouter : 0 2 * * * /home/ubuntu/backup-mindpath.sh
```

## 🚀 Publication sur Microsoft AppSource

### **18. Préparation pour l'AppSource**
- [ ] Créer un compte développeur Microsoft Partner Center
- [ ] Préparer les métadonnées de l'application
- [ ] Créer les captures d'écran et vidéos de démonstration
- [ ] Rédiger la description et les instructions d'utilisation
- [ ] Tester l'add-in sur différents environnements Excel

### **19. Soumission**
- [ ] Upload du manifest.xml sur Partner Center
- [ ] Remplir tous les champs requis
- [ ] Soumettre pour validation
- [ ] Répondre aux feedbacks Microsoft
- [ ] Publier sur l'AppSource

## ✅ Validation finale

### **20. Checklist de validation**
- [ ] Interface admin accessible : https://mindpath-dev.fr
- [ ] API fonctionnelle : https://api.mindpath-dev.fr
- [ ] Certificats SSL valides
- [ ] Excel Add-in fonctionnel
- [ ] Logs sans erreurs
- [ ] Services démarrés automatiquement
- [ ] Sauvegardes configurées
- [ ] Monitoring en place

## 📞 Support

### **21. Documentation**
- [ ] Mettre à jour le README.md
- [ ] Créer un guide utilisateur
- [ ] Documenter les procédures de maintenance
- [ ] Préparer les contacts de support

### **22. Contacts d'urgence**
- **Nginx** : `sudo systemctl restart nginx`
- **Backend** : `sudo systemctl restart mindpath-backend`
- **Certificats** : `sudo certbot renew`
- **Logs** : `sudo journalctl -u mindpath-backend -f`

---

**🎉 Félicitations ! Votre application MindPath est maintenant prête pour la production !**
