# SuiviUsagerPro - Guide de l'utilisateur

## Introduction
**SuiviUsagerPro** est une application portable de bureau, conçue pour aider les conseillers numériques à gérer efficacement les usagers et les ateliers.

## Configuration requise
- **Système d'exploitation** : Windows 10 ou plus récent
- **Espace disque** : 100 Mo minimum
- **RAM** : 4 Go recommandés
- **Résolution d'écran** : 1280x720 minimum

## Installation
1. Téléchargez le fichier `SuiviUsagerPro.exe` depuis le [lien de téléchargement].
2. Placez le fichier `.exe` dans un dossier de votre choix.
3. Double-cliquez sur `SuiviUsagerPro.exe` pour lancer l'application.
4. Un dossier "data" sera créé dans le dossier de l'exécutable, contenant la base de données.
5. Un dossier "exports" sera créé dans "data", il contiendra les sauvegardes au format `.csv`.

## Fonctionnalités principales

### 1. Tableau de bord
- Récapitulatif mensuel des ateliers.
- Statistiques sur les types d'ateliers et leur statut (payant/gratuit).
- Nombre total d'usagers et d'ateliers.
- Historique des derniers usagers.

### 2. Gestion des usagers
- Ajout de nouveaux usagers.
- Liste paginée avec fonction de recherche.
- Édition et suppression d'usagers.
- Ajout rapide d'ateliers pour un usager.

### 3. Historique des ateliers
- Vue détaillée de tous les ateliers réalisés.

### 4. Gestion des données
- Exportation en CSV (usagers, ateliers, données complètes).
- Gestion RGPD (suppression des usagers inactifs).
- Importation de données.

### 5. Paramètres
- Gestion des conseillers numériques.
- Personnalisation de l'interface.
- Configuration RGPD.

### 6. Fonctionnalités globales
- Barre de recherche rapide.
- Sélection du conseiller actif.

## Sauvegarde et restauration
- Pour sauvegarder manuellement, copiez le dossier "data" dans un emplacement sûr.
- Pour restaurer, remplacez le dossier "data" dans le dossier où se trouve l'exécutable.

## Guide rapide

### Ajouter un nouvel usager
1. Cliquez sur "Ajouter un usager" dans le menu principal.
2. Remplissez les champs obligatoires (Nom, Prénom, Téléphone).
3. Ajoutez des informations supplémentaires si nécessaire.
4. Cliquez sur "Valider la création du nouvel utilisateur".

![Capture d'écran](https://github.com/user-attachments/assets/99ed41ff-6d43-4953-a992-cfc5182e81e4)

### Enregistrer un atelier
1. Trouvez l'usager concerné via la barre de recherche ou la liste des usagers.
2. Cliquez sur "Ajouter un atelier" pour cet usager.
3. Sélectionnez la date, le type d'atelier et le conseiller.
4. Ajoutez une description si nécessaire.
5. Indiquez si l'atelier a été payé.
6. Validez l'ajout de l'atelier.

![Capture d'écran](https://github.com/user-attachments/assets/d35dbaf6-a8dd-4c5c-8e57-23f2f79292e8)

### Exporter/Importer les données
1. Accédez à "Gestion des données" dans le menu.
2. Choisissez le type de données à exporter/importer (usagers, ateliers, ou toutes les données).
3. Cliquez sur "Exporter" pour générer le fichier.
4. L'export sera enregistré dans `../data/exports/`.

## Options

### Gérer les ateliers payants
1. Ouvrez les "Paramètres" via le menu.
2. Dans la section "Paramètres des ateliers", vous pouvez :
   - Choisir le nombre d'ateliers avant un paiement (valeur appliquée à tous les ateliers indiqués).
   - Déterminer quels ateliers sont payants.

### Gérer les conseillers
1. Ouvrez les "Paramètres" via le menu.
2. Dans la section "Gestion des conseillers", vous pouvez :
   - Ajouter un nouveau conseiller en entrant son nom.
   - Supprimer un conseiller existant.

### Confidentialité et RGPD
**SuiviUsagerPro** est conçu pour respecter le RGPD :
- Les données sont stockées localement sur votre machine.
- Vous pouvez exporter ou supprimer les données des usagers à leur demande.
- L'application ne collecte ni ne transmet aucune donnée personnelle.
- Vous pouvez configurer la durée avant la suppression des données personnelles.

![Capture d'écran](https://github.com/user-attachments/assets/cb34e0ba-dbb7-4637-8861-e7d7ff33cd28)

## Résolution des problèmes courants
- **L'application ne démarre pas** : Assurez-vous d'avoir les droits d'administrateur ou d'exécution dans le dossier.
- **Erreur de base de données** : Vérifiez que le dossier "data" est présent et non corrompu.
- **Interface graphique ne s'affiche pas correctement** : Mettez à jour vos pilotes graphiques.

## Support
Pour toute question ou assistance, un serveur Discord est disponible : [Discord](https://discord.gg/FD4DdWEQ). 
Conservez le fichier `app.log` dans un autre dossier pour aider à identifier les problèmes rencontrés.

## Captures d'écran
![Capture d'écran](https://github.com/user-attachments/assets/628ca66f-bc1a-40d5-b464-2425e9013da5)

--- 

J'ai corrigé la grammaire, l'orthographe et la ponctuation, et j'ai ajusté certaines formulations pour améliorer la clarté et la précision du guide. Si tu souhaites d'autres modifications, fais-le moi savoir.
