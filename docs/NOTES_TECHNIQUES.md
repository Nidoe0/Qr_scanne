# Notes techniques

## Suppressions par rapport à l'archive initiale

- Suppression du frontend web `frontend/` (HTML/CSS/JavaScript).
- Suppression des environnements virtuels embarqués dans l'archive.
- Suppression des bases SQLite et fichiers stockés issus de l'ancien prototype.
- Suppression de l'authentification par compte, non demandée pour le partage invité.
- Suppression des écrans Kivy redondants et non reliés.
- Suppression de Tkinter du démarrage mobile : il n'est importé que dans le chemin de sélection desktop.
- Suppression de CORS, inutile pour le client Kivy natif.

## À implémenter avant une version complète

- Scan QR via caméra Android et validation de l'URI `qrconnect://`.
- Sélecteur de dossiers Android (Storage Access Framework) et ZIP.
- Progression réelle, annulation et reprise par blocs.
- Contrôle SHA-256 côté client après téléchargement.
- Demande d'acceptation avant réception.
- Expiration et purge automatique des fichiers.
- Google Drive OAuth si cette option est toujours souhaitée.
