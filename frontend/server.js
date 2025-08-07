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

// Proxy pour l'API
app.post('/api/search', (req, res) => {
    console.log('Requête reçue:', req.body);

    const options = {
        hostname: '127.0.0.1',
        port: 8000,
        path: '/search',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    };

    console.log('Envoi de la requête à:', `http://${options.hostname}:${options.port}${options.path}`);

    const apiReq = http.request(options, (apiRes) => {
        console.log('Statut de la réponse API:', apiRes.statusCode);
        let data = '';

        apiRes.on('data', (chunk) => {
            data += chunk;
            console.log('Chunk reçu:', chunk.toString());
        });

        apiRes.on('end', () => {
            console.log('Réponse API complète:', data);
            try {
                const jsonData = JSON.parse(data);
                res.status(apiRes.statusCode).json(jsonData);
            } catch (e) {
                console.error('Erreur de parsing JSON:', e);
                res.status(500).json({ error: 'Erreur de parsing de la réponse' });
            }
        });
    });

    apiReq.on('error', (error) => {
        console.error('Erreur API détaillée:', error);
        res.status(500).json({
            error: 'Erreur de communication avec l\'API',
            details: error.message,
            code: error.code,
            host: options.hostname,
            port: options.port
        });
    });

    apiReq.write(JSON.stringify(req.body));
    apiReq.end();
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