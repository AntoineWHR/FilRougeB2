# YOps Portal - Application DEV locale

Application web locale pour YOps Cybersecurity.

Elle contient deux parties :

- une landing page publique pour presenter les services cyber et permettre a un prospect de demander un audit ;
- un espace connecte pour suivre les clients, audits, vulnerabilites, tickets de remediation et rapports.

Le projet est volontairement local : pas de Proxmox, pas de Tailscale, pas de service externe. Il tourne sur le PC avec Python et SQLite.

## Lancer le projet

Prerequis : Python 3.

```bash
cd app-yops-portal
python3 run.py
```

Ouvrir ensuite :

```text
http://127.0.0.1:8000
```

Comptes de demonstration :

| Role | Email | Mot de passe |
| --- | --- | --- |
| Administrateur | `admin@yops.local` | `YOps-Admin-2026!` |
| Analyste SOC | `sarah.diallo@yops.local` | `YOps-User-2026!` |
| Commercial | `hugo.bernard@yops.local` | `YOps-User-2026!` |
| Client | `client@alphatech.local` | `YOps-Client-2026!` |

## Fonctionnalites

- Connexion avec sessions locales.
- Landing page commerciale : services, methode, offres et appel a l'action.
- Inscription client / demande d'audit.
- Tableau de bord avec KPI, criticites et score de risque client.
- Gestion des clients.
- Consultation des audits.
- Registre des vulnerabilites avec filtres et ajout de nouvelles failles.
- Suivi des tickets de remediation.
- Rapports executifs.
- Page d'administration des utilisateurs.
- Module d'analyse Python exportant des fichiers CSV/JSON.

## Interfaces et droits

L'application separe volontairement deux espaces.

| Espace | Utilisateurs | Acces |
| --- | --- | --- |
| Site public | visiteurs | presentation des services, offres, demande d'audit |
| Espace client | clients | uniquement les audits, tickets, vulnerabilites et rapports de leur entreprise |
| Back-office | admin, analyste, commercial | gestion globale clients, audits, vulnerabilites, tickets et rapports |

Un compte client ne voit pas la liste des autres clients et ne peut pas acceder au registre global des vulnerabilites.

## Choix techniques

- Backend : Python standard library (`http.server`, `sqlite3`).
- Base de donnees : SQLite locale.
- Frontend : HTML/CSS/JS sans framework.
- Architecture : separation entre modeles, repositories SQL, services metier et vues.
- Securite applicative : mots de passe hashes avec PBKDF2, sessions avec token aleatoire, requetes SQL parametrees.

## Analyse de donnees

```bash
cd app-yops-portal
python3 analytics/analyze_yops.py
```

Les rapports sont crees dans `storage/reports/`.

## Correspondance avec la grille DEV

| Critere | Reponse dans le projet |
| --- | --- |
| Concevoir une solution logicielle | Parcours prospect vers demande d'audit, puis espace client/back-office. |
| Developper une application fonctionnelle | Landing page, inscription, espace client separe, back-office, formulaires, base locale et rapports. |
| Bonnes pratiques | Code separe en couches, fonctions courtes, requetes parametrees, pas de duplication inutile. |
| POO | Entites en dataclasses, repositories, services metier, gestionnaire d'application. |
| Base relationnelle | Schema SQLite avec relations clients, utilisateurs, audits, vulnerabilites, tickets, rapports. |
| SQL avance | Jointures, agregations, filtres, index, indicateurs et exports. |
| UI responsive et accessible | Interface responsive, navigation claire, contrastes propres, formulaires labels, HTML semantique. |
| Analyse Python | Script d'analyse produisant CSV/JSON depuis la base locale. |

## Structure

```text
app-yops-portal/
├── run.py
├── analytics/
├── public/assets/
├── storage/reports/
└── yops_portal/
    ├── core/
    ├── models/
    ├── repositories/
    ├── services/
    └── views/
```

La base SQLite est creee automatiquement dans `data/yops_portal.sqlite` au premier lancement.
