@echo off
title 🔐 Installation certificat localhost pour Add-In Excel
color 0B

set CERT_PATH=%USERPROFILE%\.office-addin-dev-certs\localhost.crt

echo 📌 Vérification de l'existence du certificat : %CERT_PATH%
if not exist "%CERT_PATH%" (
    echo ❌ Le certificat n'existe pas.
    echo 🛠️ Lance : npx office-addin-dev-certs install
    pause
    exit /b
)

echo 🔎 Nettoyage des anciens certificats "localhost" dans le magasin racine...
powershell -Command ^
    "$store = New-Object System.Security.Cryptography.X509Certificates.X509Store('Root','LocalMachine');" ^
    "$store.Open('ReadWrite');" ^
    "$toRemove = $store.Certificates | Where-Object { $_.Subject -like '*CN=localhost*' };" ^
    "if ($toRemove.Count -gt 0) { $toRemove | ForEach-Object { Write-Host '🗑️ Suppression :' $_.Subject; $store.Remove($_) } }" ^
    "else { Write-Host '✅ Aucun ancien certificat localhost trouvé.' }" ^
    "$store.Close();"

echo 🚀 Installation du certificat localhost.crt...
powershell -Command ^
    "$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2('%CERT_PATH%');" ^
    "if (-not $cert.Subject -like '*CN=localhost*') { Write-Error '❌ Le certificat ne correspond pas à CN=localhost'; exit 1 }" ^
    "Write-Host '📥 Import du certificat dans le magasin racine machine...';" ^
    "Import-Certificate -FilePath '%CERT_PATH%' -CertStoreLocation 'Cert:\LocalMachine\Root' -Verbose"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Échec de l'installation. Assure-toi de lancer ce script en tant qu'administrateur.
    pause
    exit /b
)

echo 🟢 Certificat installé avec succès !
echo 🔁 Redémarre Excel (et/ou ton navigateur) si nécessaire.
pause
