# Demo orale - Partie DEV

## Objectif de la demo

Montrer que l'application n'est pas un site statique, mais une application metier locale connectee a une base de donnees.

## Scenario court

### 1. Ouvrir l'application

URL cible :

```text
http://127.0.0.1:8000
```

Phrase :

```text
La partie DEV tourne localement sur mon PC. Elle est separee de l'infrastructure pour que la demonstration reste stable et ne depende pas du reseau.
```

### 2. Connexion

Se connecter d'abord avec un compte client, puis avec un compte admin.

Phrase :

```text
L'application possede une authentification avec deux espaces differents : un espace client limite et un back-office pour l'equipe YOps.
```

### 3. Espace client

Compte client :

```text
client@alphatech.local
YOps-Client-2026!
```

Montrer :

- le client ne voit que son espace ;
- il ne voit pas la liste globale des clients ;
- il voit seulement ses audits, tickets et rapports.

Phrase :

```text
Un client ne doit jamais voir les autres clients. Son interface est volontairement limitee a son entreprise.
```

### 4. Back-office admin

Compte admin :

```text
admin@yops.local
YOps-Admin-2026!
```

Montrer :

- clients actifs ;
- audits en cours ;
- vulnerabilites critiques ;
- tickets ouverts.

Phrase :

```text
Le dashboard donne une vision rapide de l'activite cyber de l'entreprise.
```

### 5. Creer un client

Exemple :

```text
Client : DemoCorp
Secteur : SaaS
Contact : demo@democorp.local
```

Phrase :

```text
Les clients sont centralises dans l'application. Chaque audit est rattache a un client.
```

### 6. Creer un audit

Exemple :

```text
Audit : Audit web DemoCorp
Type : web
Statut : en cours
```

Phrase :

```text
Un audit represente une mission cyber realisee pour un client.
```

### 7. Ajouter une vulnerabilite

Exemple :

```text
Titre : MFA absent sur compte administrateur
Criticite : critique
Actif : portail.democorp.local
Recommandation : activer MFA pour les comptes privilegies
```

Phrase :

```text
Les vulnerabilites sont classees par criticite pour aider a prioriser les corrections.
```

### 8. Creer un ticket de remediation

Phrase :

```text
Le ticket permet de suivre la correction d'une vulnerabilite jusqu'a sa resolution.
```

### 9. Montrer la base de donnees

Depuis le dossier du projet sur mon PC :

```bash
cd app-yops-portal
python3 analytics/analyze_yops.py
ls storage/reports
```

Phrase :

```text
Cette commande montre que l'application exploite une vraie base locale et produit des rapports CSV/JSON a partir des donnees.
```

## Ce qu'il faut eviter pendant la demo

- ne pas montrer trop de code ;
- ne pas passer trop de temps sur les formulaires ;
- ne pas improviser une fonctionnalite non testee ;
- garder une demo courte et fluide.

## Phrase de conclusion DEV

```text
La partie DEV est locale sur mon PC. Elle montre la logique applicative : site public, inscription client, authentification, separation client/back-office, base relationnelle, audits, vulnerabilites et tickets de remediation.
```
