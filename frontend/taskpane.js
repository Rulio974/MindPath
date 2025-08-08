(function () {
    "use strict";

    let isSelectingReponseCol = false;
    let isSelectingCommentaireCol = false;

    // Configuration par défaut
    let config = {
        serverUrl: '', // L'utilisateur configure son propre serveur
        apiToken: ''
    };

    // Gestion des onglets
    function initTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');

                // Désactiver tous les onglets
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Activer l'onglet sélectionné
                button.classList.add('active');
                document.getElementById(targetTab + '-tab').classList.add('active');
            });
        });
    }

    // Persistance des paramètres
    function loadSettings() {
        try {
            const savedConfig = localStorage.getItem('mindpathConfig');
            if (savedConfig) {
                config = { ...config, ...JSON.parse(savedConfig) };
                document.getElementById('serverUrl').value = config.serverUrl;
                document.getElementById('apiToken').value = config.apiToken;
                console.log('Paramètres chargés:', config);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des paramètres:', error);
        }
    }

    async function saveSettings() {
        const serverUrl = document.getElementById('serverUrl').value.trim();
        const apiToken = document.getElementById('apiToken').value.trim();

        if (!serverUrl || !apiToken) {
            showSaveStatus('Veuillez remplir tous les champs.', 'error');
            return;
        }

        // Sauvegarder dans localStorage
        config.serverUrl = serverUrl;
        config.apiToken = apiToken;
        localStorage.setItem('mindpathConfig', JSON.stringify(config));

        // Tester la connexion avec une route authentifiée
        try {
            showSaveStatus('Test de connexion en cours...', 'warning');

            // Créer un AbortController pour le timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 secondes

            const response = await fetch(`${serverUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiToken}`
                },
                body: JSON.stringify({ question: "test", top_k: 1 }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                showSaveStatus('Connexion réussie ! Paramètres sauvegardés.', 'success');
                console.log('Paramètres sauvegardés et connexion testée: ', config);
            } else if (response.status === 401 || response.status === 403) {
                showSaveStatus('Token invalide. Vérifiez votre token API.', 'error');
            } else {
                showSaveStatus(`Erreur de connexion (${response.status}). Vérifiez l'URL du serveur.`, 'error');
            }
        } catch (error) {
            console.error('Erreur de test de connexion:', error);
            if (error.name === 'AbortError') {
                showSaveStatus('Timeout : Le serveur ne répond pas. Vérifiez l\'URL.', 'error');
            } else {
                showSaveStatus('Impossible de contacter le serveur. Vérifiez l\'URL.', 'error');
            }
        }
    }

    function showSaveStatus(message, type) {
        const statusElement = document.getElementById('saveStatus');
        statusElement.textContent = message;
        statusElement.className = `status-indicator ${type}`;
        setTimeout(() => {
            statusElement.textContent = '';
            statusElement.className = 'status-indicator';
        }, 3000);
    }



    function toggleTokenVisibility() {
        const tokenInput = document.getElementById('apiToken');
        const toggleBtn = document.getElementById('toggleTokenVisibility');

        if (tokenInput.type === 'password') {
            tokenInput.type = 'text';
            toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
        } else {
            tokenInput.type = 'password';
            toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
        }
    }

    Office.onReady((info) => {
        if (info.host === Office.HostType.Excel) {
            console.log("Module initialisé dans Excel");

            // Initialiser les onglets
            initTabs();

            // Charger les paramètres sauvegardés
            loadSettings();

            // Vérifier si la configuration est complète
            if (!config.serverUrl || !config.apiToken) {
                console.log('Configuration incomplète, affichage de l\'onglet Paramètres');
                // Basculer vers l'onglet Paramètres si la configuration est incomplète
                setTimeout(() => {
                    document.querySelector('[data-tab="settings"]').click();
                }, 500);
            }

            // Événements de recherche
            document.getElementById("searchButton").onclick = searchQuestion;
            document.getElementById("selectReponseCell").onclick = startSelectReponseCol;
            document.getElementById("selectCommentaireCell").onclick = startSelectCommentaireCol;

            // Événements des paramètres
            document.getElementById("saveSettings").onclick = saveSettings;
            document.getElementById("toggleTokenVisibility").onclick = toggleTokenVisibility;

            const optionsToggle = document.getElementById("optionsToggle");
            const autoFillConfig = document.getElementById("autoFillConfig");
            const chevron = optionsToggle.querySelector(".chevron");

            optionsToggle.addEventListener("click", () => {
                const isVisible = autoFillConfig.style.display !== "none";
                autoFillConfig.style.display = isVisible ? "none" : "block";
                chevron.classList.toggle("up", !isVisible);
            });

            Excel.run(async (context) => {
                console.log("Configuration de l'événement de sélection");

                let sheet = context.workbook.worksheets.getActiveWorksheet();
                sheet.onSelectionChanged.add(handleSelectionChange);

                await context.sync();
                console.log("Événement de sélection configuré");
            }).catch(function (error) {
                console.error("Erreur lors de l'initialisation:", error);
            });
        }
    });

    function startSelectReponseCol() {
        console.log("Début sélection colonne réponse");
        isSelectingReponseCol = true;
        isSelectingCommentaireCol = false;
        document.getElementById("selectReponseCell").style.backgroundColor = "#ff9800";
    }

    function startSelectCommentaireCol() {
        console.log("Début sélection colonne commentaire");
        isSelectingReponseCol = false;
        isSelectingCommentaireCol = true;
        document.getElementById("selectCommentaireCell").style.backgroundColor = "#ff9800";
    }

    async function handleSelectionChange(event) {
        return Excel.run(async (context) => {
            console.log("Changement de sélection détecté");

            let range = context.workbook.getSelectedRange();
            range.load(["address", "text", "rowIndex"]);

            await context.sync();

            if (isSelectingReponseCol || isSelectingCommentaireCol) {
                console.log("Mode sélection colonne actif");
                const colLetter = range.address.split("!")[1].replace(/[0-9]/g, '');

                if (isSelectingReponseCol) {
                    document.getElementById("reponseCell").value = colLetter;
                    document.getElementById("selectReponseCell").style.backgroundColor = "#217346";
                    document.getElementById("reponseCellStatus").innerHTML = "✓";
                    isSelectingReponseCol = false;
                    console.log("Colonne réponse sélectionnée:", colLetter);
                } else {
                    document.getElementById("commentaireCell").value = colLetter;
                    document.getElementById("selectCommentaireCell").style.backgroundColor = "#217346";
                    document.getElementById("commentaireCellStatus").innerHTML = "✓";
                    isSelectingCommentaireCol = false;
                    console.log("Colonne commentaire sélectionnée:", colLetter);
                }
            } else if (range.text && range.text[0] && range.text[0][0]) {
                const question = range.text[0][0];
                const rowNumber = range.rowIndex;
                console.log("Question sélectionnée:", question, "à la ligne", rowNumber);

                document.getElementById("questionInput").value = question;
                const bestResult = await searchQuestion();

                if (document.getElementById("autoFillEnabled").checked && bestResult) {
                    await fillAnswerCells(bestResult, rowNumber);
                }
            }
        }).catch(function (error) {
            console.error("Erreur lors de la gestion de la sélection:", error);
        });
    }

    async function searchQuestion() {
        const question = document.getElementById("questionInput").value;
        console.log("Question posée:", question);

        if (!question) {
            showResults("Veuillez entrer une question.");
            return null;
        }

        // Vérifier la configuration
        if (!config.serverUrl || !config.apiToken) {
            showResults("Veuillez configurer le serveur et le token API dans l'onglet Paramètres.");
            return null;
        }

        try {
            console.log("Tentative d'appel à l'API via", config.serverUrl);

            // Créer un AbortController pour le timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 secondes

            const response = await fetch(`${config.serverUrl}/search`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": `Bearer ${config.apiToken}`
                },
                body: JSON.stringify({ question: question, top_k: 5 }),
                signal: controller.signal,
                // Ignorer les erreurs de certificat SSL auto-signé
                mode: 'cors'
            });

            clearTimeout(timeoutId);

            console.log("Statut de la réponse:", response.status);
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error("Token API invalide. Vérifiez votre token dans les paramètres.");
                } else if (response.status === 403) {
                    throw new Error("Accès refusé. Vérifiez vos permissions.");
                } else {
                    throw new Error(`Erreur HTTP ${response.status}: ${response.statusText}`);
                }
            }

            const data = await response.json();
            console.log("Données reçues:", data);

            if (data.error) {
                showError("Erreur serveur", data.error);
                return null;
            } else {
                displayResults(data.results);
                return data.results && data.results.length > 0 ? data.results[0] : null;
            }
        } catch (err) {
            console.error("Erreur détaillée:", err);
            let errorMessage = err.message || err;
            if (err.name === 'AbortError') {
                errorMessage = "Timeout : Le serveur ne répond pas. Vérifiez l'URL du serveur.";
            } else if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
                errorMessage = "Impossible de contacter le serveur. Vérifiez que le serveur est en cours d'exécution et accessible.";
            }
            showError("Erreur de communication", errorMessage, {
                url: `${config.serverUrl}/search`,
                type: err.name,
                message: err.message
            });
            return null;
        }
    }

    async function fillAnswerCells(result, rowNumber) {
        if (!result) {
            console.log("Pas de résultat à remplir");
            return;
        }

        const reponseCol = document.getElementById("reponseCell").value;
        const commentaireCol = document.getElementById("commentaireCell").value;

        if (!reponseCol && !commentaireCol) {
            console.log("Aucune colonne configurée pour le remplissage");
            return;
        }

        try {
            return Excel.run(async (context) => {
                console.log("Remplissage des cellules à la ligne", rowNumber);
                let sheet = context.workbook.worksheets.getActiveWorksheet();

                if (reponseCol && result.reponse) {
                    console.log("Remplissage réponse:", result.reponse, "dans", `${reponseCol}${rowNumber + 1}`);
                    let reponseRange = sheet.getRange(`${reponseCol}${rowNumber + 1}`);
                    reponseRange.values = [[result.reponse]];
                }

                if (commentaireCol && result.commentaire) {
                    console.log("Remplissage commentaire:", result.commentaire, "dans", `${commentaireCol}${rowNumber + 1}`);
                    let commentaireRange = sheet.getRange(`${commentaireCol}${rowNumber + 1}`);
                    commentaireRange.values = [[result.commentaire]];
                }

                await context.sync();
                console.log("Remplissage terminé");
            });
        } catch (error) {
            console.error("Erreur lors du remplissage des cellules:", error);
        }
    }

    function displayResults(results) {
        console.log("Affichage des résultats:", results);
        if (!results || results.length === 0) {
            showResults("Aucun résultat trouvé.");
            return;
        }

        let html = "<table>";
        html += "<tr><th>Entreprise</th><th>Question</th><th>Réponse</th><th>Commentaire</th><th>Date</th><th>Score</th></tr>";
        results.forEach(result => {
            html += "<tr>";
            html += `<td>${result.entreprise || ""}</td>`;
            html += `<td>${result.question || ""}</td>`;
            html += `<td>${result.reponse || ""}</td>`;
            html += `<td>${result.commentaire || ""}</td>`;
            html += `<td>${result.annee || ""}</td>`;
            html += `<td>${result.score.toFixed(2)}</td>`;
            html += "</tr>";
        });
        html += "</table>";
        showResults(html);
    }

    function showError(title, message, details = null) {
        let html = `
            <div class="error-card">
                <div class="error-header">
                    <i class="bi bi-exclamation-triangle"></i>
                    <span class="error-title">${title}</span>
                </div>
                <div class="error-message">${message}</div>
                ${details ? `
                    <div class="error-details">
                        <div class="error-detail">
                            <strong>URL :</strong> ${details.url || 'N/A'}
                        </div>
                        ${details.type ? `<div class="error-detail"><strong>Type :</strong> ${details.type}</div>` : ''}
                        ${details.message ? `<div class="error-detail"><strong>Message :</strong> ${details.message}</div>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
        document.getElementById("results").innerHTML = html;
    }

    function showResults(content) {
        document.getElementById("results").innerHTML = content;
    }
})();
