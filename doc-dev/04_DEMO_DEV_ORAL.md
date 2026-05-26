# Demo orale - Partie DEV

## Objectif de la demo

Montrer que l'application n'est pas un site statique, mais une vraie application metier locale connectee a une base SQLite, avec un site public, un espace client, un back-office, un flow de demande d'audit client vers admin, des notes client, et un dashboard organise.

## Comptes de demo

```text
Admin       : admin@yops.local         / YOps-Admin-2026!
Analyste    : sarah.diallo@yops.local  / YOps-User-2026!
Commercial  : hugo.bernard@yops.local  / YOps-User-2026!
Client      : client@alphatech.local   / YOps-Client-2026!
```

## Scenario de demonstration

### 1. Lancer l'application

```bash
cd app-yops-portal
python3 run.py
```

URL :

```text
http://127.0.0.1:8000
```

Phrase :

```text
La partie DEV tourne en local. Elle est volontairement separee de l'infrastructure pour que la demo reste stable.
```

### 2. Page d'accueil publique

Montrer :

- le hero avec le visuel cyber, un widget "Synthese client" qui affiche un score de risque et des barres animees, et un badge "SOC actif" qui pulse en haut a droite ;
- le bandeau defilant en dessous avec les standards utilises (OWASP, ISO 27001, ANSSI, Wazuh, NIST CSF) ;
- les trois services : audit web, audit infrastructure, supervision SOC ;
- la methode en 4 etapes : cadrage, evaluation, remediation, restitution ;
- les trois offres tarifaires (Starter, Business, Managed) ;
- le bouton "Demander un audit" qui mene au formulaire d'inscription.

Phrase :

```text
La page publique sert a presenter YOps et a convertir un visiteur en client. Le hero n'est pas statique : il affiche des donnees vivantes qui ressemblent a la realite d'un suivi de risque.
```

### 3. Inscription client

URL :

```text
http://127.0.0.1:8000/register
```

Remplir le formulaire (entreprise, secteur, contact, email, telephone, mot de passe).

Phrase :

```text
Le formulaire cree une fiche client et un compte utilisateur lie. Le mot de passe est hashe PBKDF2 et l'email doit etre unique.
```

### 4. Espace client - demande d'audit

Se connecter en client :

```text
client@alphatech.local / YOps-Client-2026!
```

Sur le tableau de bord client, montrer :

- les KPI propres au client : audits, vulnerabilites ouvertes, tickets, critiques ;
- les rapports recus de YOps ;
- la section "Demandes d'audit" en bas de page.

Faire une demande :

```text
Type      : Infrastructure
Scope     : Audit DMZ et reverse-proxy nginx
Regles    : Lecture seule, pas d'arret de service, fenetre 22h-06h
Urgence   : Haute
Date cible: 2026-06-30
```

Apres envoi, la demande apparait dans "Mes demandes" avec le statut **En attente**.

Phrase :

```text
Le client peut declencher une demande d'audit avec son perimetre, ses regles d'engagement, son urgence et sa date cible. C'est le point d'entree d'une nouvelle mission.
```

### 5. Back-office admin - traiter la demande

Se deconnecter, se reconnecter en admin :

```text
admin@yops.local / YOps-Admin-2026!
```

Sur le dashboard admin, montrer :

- la section "Vue d'ensemble" : 4 KPI animes (clients actifs, audits en cours, critiques ouvertes, taux de remediation), 4 quick actions ;
- la quick action "Demandes clients" en surbrillance ambre avec le compteur ;
- la section "Demandes clients en attente" avec les cartes interactives.

Cliquer "Accepter" sur la demande creee a l'etape 4 :

```text
Titre        : Audit infra DMZ Alphatech
Date debut   : 2026-06-30
Message      : Demande validee, Sarah prend contact pour le kick-off.
```

Phrase :

```text
Acceptee, la demande genere automatiquement un audit en statut planifie, rattache au client et au responsable. Refusee, elle stocke la decision et le message renvoye au client.
```

Montrer la page complete des demandes :

```text
http://127.0.0.1:8000/audit-requests
```

Avec la section "A traiter" et "Historique" (decisions passees).

### 6. Fiche client et notes de suivi

Aller sur :

```text
http://127.0.0.1:8000/clients/1
```

Montrer :

- les 4 KPI risque du client (score, critiques, hautes, niveau) ;
- la liste des audits et la fiche contact ;
- les vulnerabilites principales ;
- la section "Suivi & notes" avec la timeline.

Ajouter une note :

```text
Type    : Alerte
Contenu : MFA toujours pas active, relance prevue cette semaine.
```

Phrase :

```text
La timeline regroupe les interactions avec le client : notes internes, comptes-rendus de contact, alertes ouvertes et reunions. Chaque entree porte son auteur, son type avec une couleur dediee, et sa date.
```

### 7. Registre des vulnerabilites

```text
http://127.0.0.1:8000/vulnerabilities
```

Montrer :

- la barre de chips de filtre : criticite, statut, puis filtre par client ;
- le champ de recherche live qui filtre instantanement la table ;
- la colonne action avec le bouton "Demarrer / Marquer corrigee / Reouvrir" pour faire avancer le statut sans quitter la page ;
- le formulaire d'ajout avec **regroupement par client** (optgroup) pour choisir l'audit.

Ajouter une vulnerabilite de demo :

```text
Audit         : Alphatech > Audit web portail client
Titre         : XSS reflechie sur recherche
Criticite     : Haute
CVSS          : 7.2
Actif         : /search
Recommandation: Encoder la sortie et activer CSP strict.
```

Phrase :

```text
Le registre permet de filtrer par criticite, statut ou client, de chercher en temps reel, et d'avancer le statut sans ouvrir une nouvelle page. Le formulaire d'ajout regroupe les audits par client pour choisir vite.
```

### 8. Pilotage et activite

Revenir au dashboard admin et derouler les sections :

- **Pilotage des audits** : progression des audits actifs sous forme de barre en pourcentage de vulns corrigees, et top 5 des actifs les plus exposes ;
- **Risque & vulnerabilites** : dernieres vulns trouvees, repartition par criticite, score risque par client ;
- **Activite recente** : feed unifie qui melange vulnerabilites, notes client et rapports tries par date.

Phrase :

```text
Le dashboard est structure en sections nommees : on sait toujours ce qu'on regarde. Les chiffres apparaissent avec une animation de compteur, les barres se remplissent au scroll. Tout est lu depuis la base, rien n'est statique.
```

### 9. Base de donnees et analyse Python

```bash
sqlite3 app-yops-portal/data/yops_portal.sqlite ".tables"
python3 app-yops-portal/analytics/analyze_yops.py
ls app-yops-portal/storage/reports
```

Phrase :

```text
La base contient roles, users, clients, audits, vulnerabilites, tickets, rapports, ainsi que les notes de suivi et les demandes d'audit. Le module Python exploite cette base pour produire CSV et JSON : repartition criticite, risque par client, tickets en retard.
```

## Ce qu'il faut eviter pendant la demo

- ne pas montrer trop de code ;
- ne pas passer trop de temps sur les formulaires : Ctrl+A puis taper vite ;
- ne pas improviser un type d'audit non gere par le seed ;
- garder une demo courte et fluide, max 7 minutes pour la partie DEV.

## Phrase de conclusion DEV

```text
La partie DEV est locale sur mon PC. Elle couvre l'integralite d'un cycle metier YOps : un prospect arrive par la landing publique, devient client, fait une demande d'audit, l'admin accepte, l'audit est cree, les vulnerabilites sont enregistrees, les tickets de remediation suivis, les notes client tracees, et un dashboard donne la vision d'ensemble. Le tout en Python, SQLite, HTML et CSS, sans framework.
```
