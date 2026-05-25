# Cahier des charges - YOps Portal

## Objectif

YOps Portal est une application web interne pour suivre les missions cyber d'une entreprise.

Elle doit permettre de centraliser :

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
| Client | Consulter ses rapports et corrections |

## Fonctionnalites principales

### Authentification

- connexion avec email et mot de passe ;
- mot de passe hashe ;
- deconnexion ;
- protection CSRF.

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
- modifier ;
- archiver.

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

- creer un audit ;
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
- afficher une synthese executive ;
- exporter en PDF si possible.

## Regles de securite applicative

- validation cote serveur ;
- acces par role ;
- un client ne voit que ses propres rapports ;
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
