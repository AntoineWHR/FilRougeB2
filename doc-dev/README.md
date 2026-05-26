# Partie DEV - Application YOps

Ce dossier regroupe le plan de la partie developpement du projet fil rouge.

L'objectif est de construire une application web metier pour **YOps Cybersecurity**.

La partie DEV est volontairement **locale sur mon PC**.  
Elle ne depend pas de Proxmox, Tailscale, `YOPS-WEB01` ou `YOPS-DB01`.

## Idee de l'application

L'application s'appelle :

```text
YOps Portal
```

Elle sert a presenter et gerer l'activite d'une petite entreprise de cybersecurite :

- landing page publique ;
- demande d'audit / inscription client ;
- clients ;
- audits ;
- vulnerabilites ;
- tickets de remediation ;
- rapports ;
- tableau de bord.

Ce n'est pas un simple site vitrine.  
C'est une application metier qui montre une logique d'entreprise cyber.

## Stack retenue

| Couche | Choix |
|---|---|
| Backend | Python standard library |
| Frontend | HTML/CSS/JS sans framework |
| Base de donnees | SQLite local |
| Serveur web | Serveur HTTP local Python |
| Authentification | Sessions locales + mots de passe hashes |
| Versioning | GitHub |

Pourquoi ce choix :

- l'application reste simple a lancer pendant l'oral ;
- aucune dependance reseau ne peut casser la demonstration DEV ;
- SQLite suffit pour montrer les tables, les relations et les donnees ;
- Python permet aussi de couvrir l'analyse de donnees demandee dans la grille DEV.

## Architecture DEV cible

```text
Utilisateur
   |
   v
PC local
http://127.0.0.1:8000
   |
   v
Python YOps Portal
SQLite local
```

La partie DEV reste separee de la partie INFRA.  
L'infra montre le SI d'entreprise ; l'application locale montre la partie developpement metier.

## Documents

| Fichier | Role |
|---|---|
| [01_CAHIER_DES_CHARGES.md](01_CAHIER_DES_CHARGES.md) | Fonctionnalites attendues |
| [02_MODELE_DONNEES.md](02_MODELE_DONNEES.md) | Tables et relations |
| [03_ROADMAP_DEV.md](03_ROADMAP_DEV.md) | Ordre de realisation |
| [04_DEMO_DEV_ORAL.md](04_DEMO_DEV_ORAL.md) | Scenario de demonstration |
| [05_ORAL_DEV_HUMAIN.md](05_ORAL_DEV_HUMAIN.md) | Script oral simple et humain |

## Minimum viable pour l'oral DEV

Pour avoir une partie DEV defendable, il faut au minimum :

- une landing page ;
- un formulaire d'inscription client ;
- une page de connexion ;
- un tableau de bord ;
- une liste de clients ;
- une liste d'audits ;
- une liste de vulnerabilites ;
- des badges de criticite ;
- une base SQLite avec des donnees de demonstration ;
- au moins deux roles : admin et analyste.
- un module Python d'analyse de donnees.

## Version ideale

Si le temps le permet :

- gestion complete CRUD clients/audits/vulnerabilites ;
- tickets de remediation ;
- filtrage par criticite ;
- restriction d'acces par role ;
- export rapport simple ;
- page client limitee a ses propres rapports.

## Phrase pour l'oral

```text
La partie DEV est une application metier cyber lancee en local sur mon PC. Je l'ai separee de l'infrastructure pour garder une demonstration stable et eviter qu'un probleme reseau bloque la partie developpement.
```
