# Cahier des charges - YOps Portal

## Objectif

YOps Portal est une application web interne pour suivre les missions cyber d'une entreprise.

Elle doit permettre de centraliser :

- les demandes entrantes de clients ;
- les clients ;
- les audits ;
- les vulnerabilites ;
- les tickets de correction ;
- les rapports.

## Utilisateurs cibles

| Role | Besoin |
|---|---|
| Administrateur | Gerer l'application et les utilisateurs |
| Analyste SOC | Creer les audits, vulnerabilites et tickets |
| Commercial | Suivre les clients et l'avancement des audits |
| Client | Consulter seulement ses audits, rapports et corrections |

## Fonctionnalites principales

### Site public

- presenter YOps et ses services ;
- expliquer la methode de travail ;
- afficher des offres lisibles ;
- proposer un appel a l'action vers une demande d'audit.

### Inscription client

- creation d'une demande client ;
- creation d'un compte client lie a l'entreprise ;
- validation des champs obligatoires ;
- refus d'un email deja utilise.

### Authentification

- connexion avec email et mot de passe ;
- mot de passe hashe ;
- deconnexion ;
- sessions locales ;
- requetes SQL parametrees.

### Separation des interfaces

- un visiteur voit le site public ;
- un client connecte voit uniquement son espace client ;
- un administrateur ou analyste voit le back-office ;
- un client ne peut pas ouvrir la liste globale des clients ;
- un client ne peut pas consulter les donnees d'une autre entreprise.

### Tableau de bord

Indicateurs a afficher :

- nombre de clients actifs ;
- audits en cours ;
- vulnerabilites critiques ouvertes ;
- tickets en retard ;
- repartition par criticite.

### Clients

Champs :

- nom ;
- secteur ;
- contact principal ;
- email ;
- telephone ;
- statut.

Actions :

- lister ;
- creer ;
- afficher le detail client.

### Audits

Champs :

- client ;
- titre ;
- type : web, infra, AD, cloud, code ;
- date de debut ;
- date de fin ;
- statut ;
- responsable.

Actions :

- associer un audit a un client ;
- suivre son avancement.

### Vulnerabilites

Champs :

- audit ;
- titre ;
- description ;
- criticite ;
- score CVSS simplifie ;
- actif concerne ;
- preuve ;
- recommandation ;
- statut.

Criticites :

- faible ;
- moyenne ;
- haute ;
- critique.

### Tickets de remediation

Champs :

- vulnerabilite liee ;
- responsable ;
- priorite ;
- date limite ;
- statut ;
- commentaire.

### Rapports

Fonctions :

- afficher une synthese d'audit ;
- filtrer les vulnerabilites par criticite ;
- afficher une synthese executive.

### Analyse de donnees

Fonctions :

- calculer la repartition des vulnerabilites par criticite ;
- calculer le risque par client ;
- identifier les tickets en retard ;
- sortir des fichiers CSV et JSON exploitables.

## Regles de securite applicative

- validation cote serveur ;
- acces par role ;
- un client ne voit que ses propres audits, rapports, tickets et vulnerabilites ;
- un commercial ne modifie pas les vulnerabilites techniques ;
- un analyste SOC ne gere pas les comptes administrateurs ;
- pas de mot de passe ou secret dans Git.

## Donnees de demonstration

Clients exemples :

- Alphatech ;
- MedSecure ;
- RetailOne ;
- CityCloud.

Vulnerabilites exemples :

- MFA absent sur compte administrateur ;
- partage SMB trop permissif ;
- version Nginx obsolete ;
- injection SQL sur endpoint de recherche ;
- mot de passe faible sur compte de service ;
- sauvegarde non testee.
