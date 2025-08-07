const express = require('express');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const port = 3000;

// Chemin de base pour les ressources
const basePath = process.pkg ? path.dirname(process.execPath) : __dirname;

// Middleware pour les logs
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// Activation des CORS
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Accept']
}));

app.use(express.json());
app.use(express.static(basePath));

// Endpoint de santé pour tester la connexion
app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'Add-in Excel MindPath opérationnel' });
});

// Proxy pour l'API (maintenant géré côté client)
app.post('/api/search', (req, res) => {
    console.log('Requête proxy reçue:', req.body);

    // Cette route n'est plus utilisée car le client fait maintenant des appels directs
    // Gardée pour compatibilité si nécessaire
    res.status(400).json({
        error: 'Cette méthode est dépréciée. Utilisez l\'appel direct à l\'API configurée.'
    });
});

// Chemins des certificats
const certPath = process.env.USERPROFILE ?
    path.join(process.env.USERPROFILE, '.office-addin-dev-certs') :
    path.join(basePath, 'certs');

const options = {
    key: fs.readFileSync(path.join(certPath, 'localhost.key')),
    cert: fs.readFileSync(path.join(certPath, 'localhost.crt'))
};

const server = https.createServer(options, app);

app.get('/', (req, res) => {
    res.redirect('/taskpane.html');
});

server.listen(port, () => {
    console.log(`Serveur démarré sur https://localhost:${port}`);
    console.log('Pour tester le serveur, ouvrez https://localhost:3000/taskpane.html');
}); 