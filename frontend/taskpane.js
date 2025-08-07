(function () {
    "use strict";

    let isSelectingReponseCol = false;
    let isSelectingCommentaireCol = false;

    Office.onReady((info) => {
        if (info.host === Office.HostType.Excel) {
            console.log("Module initialisé dans Excel");

            document.getElementById("searchButton").onclick = searchQuestion;
            document.getElementById("selectReponseCell").onclick = startSelectReponseCol;
            document.getElementById("selectCommentaireCell").onclick = startSelectCommentaireCol;

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

        try {
            console.log("Tentative d'appel à l'API via http://localhost:8000/search");
            const response = await fetch("http://localhost:8000/search", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({ question: question, top_k: 5 })
            });

            console.log("Statut de la réponse:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Données reçues:", data);

            if (data.error) {
                showResults("<p style='color: red;'>Erreur: " + data.error + "</p>");
                return null;
            } else {
                displayResults(data.results);
                return data.results && data.results.length > 0 ? data.results[0] : null;
            }
        } catch (err) {
            console.error("Erreur détaillée:", err);
            let errorMessage = err.message || err;
            if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
                errorMessage = "Impossible de contacter le serveur. Vérifiez que le serveur est en cours d'exécution et accessible.";
            }
            showResults(`<p style='color: red;'>
                Erreur de communication avec le serveur:<br>
                ${errorMessage}<br><br>
                URL appelée: http://localhost:8000/search<br>
                Type d'erreur: ${err.name}<br>
                Message: ${err.message}
            </p>`);
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

    function showResults(content) {
        document.getElementById("results").innerHTML = content;
    }
})();
