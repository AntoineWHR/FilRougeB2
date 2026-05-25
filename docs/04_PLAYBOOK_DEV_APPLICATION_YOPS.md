# Playbook DEV - Application web YOps

## Objectif

Developper une application web YOps pour une entreprise de cybersecurite.

L'application doit permettre de gerer :

- clients ;
- audits ;
- vulnerabilites ;
- tickets de remediation ;
- rapports ;
- statistiques cyber.

## Stack

| Couche | Choix |
|---|---|
| Backend | Laravel/PHP |
| Frontend | Blade + CSS framework simple, ou Laravel Breeze |
| Base de donnees | SQLite local |
| Serveur web | Serveur local Laravel |
| Authentification | Laravel Breeze ou auth Laravel |
| Versioning | Git |

La partie DEV est prevue pour tourner **uniquement en local sur le PC**.  
Elle ne depend pas de Proxmox, Tailscale ou des serveurs Linux du lab.

## Roles applicatifs

| Role | Droits |
|---|---|
| Admin | Acces complet |
| Analyste SOC | Gestion audits, vulnerabilites, tickets, rapports |
| Commercial | Gestion clients, consultation et suivi des audits |
| Client | Consultation de ses rapports et tickets |

## Modules fonctionnels

### Tableau de bord

Indicateurs :

- nombre de clients actifs ;
- nombre d'audits en cours ;
- vulnerabilites critiques ouvertes ;
- tickets en retard ;
- taux de remediation ;
- repartition des vulnerabilites par criticite.

### Clients

Champs :

- nom ;
- secteur ;
- contact principal ;
- email ;
- telephone ;
- statut ;
- date de creation.

### Audits

Champs :

- client ;
- titre ;
- type d'audit : web, infra, AD, cloud, code ;
- date de debut ;
- date de fin ;
- statut : planifie, en cours, termine ;
- responsable SOC.

### Vulnerabilites

Champs :

- audit ;
- titre ;
- description ;
- criticite : faible, moyenne, haute, critique ;
- score CVSS simplifie ;
- actif concerne ;
- preuve ;
- recommandation ;
- statut : ouverte, en cours, corrigee, acceptee.

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

- voir les vulnerabilites d'un audit ;
- filtrer par criticite ;
- exporter une page rapport en PDF si possible ;
- afficher une synthese executive.

## Modele de donnees minimal

Tables :

```text
users
roles
clients
audits
vulnerabilities
remediation_tickets
reports
comments
```

Relations :

- un client a plusieurs audits ;
- un audit a plusieurs vulnerabilites ;
- une vulnerabilite peut avoir un ticket de remediation ;
- un rapport appartient a un audit ;
- un utilisateur peut etre responsable d'un audit ou d'un ticket.

## Pages a livrer

| Page | URL indicative |
|---|---|
| Login | `/login` |
| Dashboard | `/dashboard` |
| Clients | `/clients` |
| Detail client | `/clients/{id}` |
| Audits | `/audits` |
| Detail audit | `/audits/{id}` |
| Vulnerabilites | `/vulnerabilities` |
| Tickets | `/tickets` |
| Rapports | `/reports` |
| Administration utilisateurs | `/admin/users` |

## Jeu de donnees de demonstration

Creer au moins :

- 4 clients ;
- 6 audits ;
- 20 vulnerabilites ;
- 10 tickets ;
- 3 rapports.

Exemples de clients :

```text
Alphatech
MedSecure
RetailOne
CityCloud
```

Exemples de vulnerabilites :

```text
MFA absent sur compte administrateur
Partage SMB accessible a tous les utilisateurs
Version Nginx obsolete
Injection SQL sur endpoint de recherche
Mot de passe faible sur compte de service
Absence de sauvegarde testee
```

## Qualite attendue

Backend :

- code organise par modeles, controleurs, policies si possible ;
- validations de formulaire ;
- migrations propres ;
- seeders pour la demo ;
- separation des roles.

Frontend :

- responsive desktop/mobile ;
- navigation claire ;
- tableaux lisibles ;
- badges de criticite colores ;
- formulaires simples ;
- aucun texte debordant.

Securite :

- mots de passe hashes ;
- CSRF actif ;
- acces par role ;
- validation cote serveur ;
- pas d'informations sensibles dans Git.

## Installation type locale

Sur le PC :

```bash
git clone <repo> yops
cd yops
composer install
cp .env.example .env
php artisan key:generate
touch database/database.sqlite
php artisan migrate --seed
php artisan serve
```

Variables `.env` :

```env
APP_NAME=YOps
APP_ENV=local
APP_DEBUG=true
APP_URL=http://127.0.0.1:8000

DB_CONNECTION=sqlite
```

## Tests fonctionnels

- un admin peut creer un client ;
- un analyste SOC peut creer une vulnerabilite ;
- un commercial ne peut pas modifier une vulnerabilite critique ;
- un client ne voit que ses propres rapports ;
- le dashboard affiche les statistiques ;
- les formulaires refusent les champs obligatoires vides ;
- l'application fonctionne en local sur `http://127.0.0.1:8000`.

## Demonstration DEV

Scenario court :

1. Connexion en admin.
2. Creation d'un client.
3. Creation d'un audit.
4. Ajout d'une vulnerabilite critique.
5. Creation d'un ticket de remediation.
6. Consultation du dashboard.
7. Connexion avec un compte client et verification de la restriction d'acces.
