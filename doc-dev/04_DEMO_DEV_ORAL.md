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

Se connecter avec un compte admin ou analyste SOC.

Phrase :

```text
L'application possede une authentification. Les utilisateurs n'ont pas tous les memes droits.
```

### 3. Tableau de bord

Montrer :

- clients actifs ;
- audits en cours ;
- vulnerabilites critiques ;
- tickets ouverts.

Phrase :

```text
Le dashboard donne une vision rapide de l'activite cyber de l'entreprise.
```

### 4. Creer un client

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

### 5. Creer un audit

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

### 6. Ajouter une vulnerabilite

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

### 7. Creer un ticket de remediation

Phrase :

```text
Le ticket permet de suivre la correction d'une vulnerabilite jusqu'a sa resolution.
```

### 8. Montrer la base de donnees

Depuis le dossier du projet sur mon PC :

```bash
php artisan migrate:status
```

Phrase :

```text
Cette commande montre que l'application utilise de vraies migrations et une base locale. Les donnees ne sont pas juste ecrites en dur dans les pages.
```

## Ce qu'il faut eviter pendant la demo

- ne pas montrer trop de code ;
- ne pas passer trop de temps sur les formulaires ;
- ne pas improviser une fonctionnalite non testee ;
- garder une demo courte et fluide.

## Phrase de conclusion DEV

```text
La partie DEV est locale sur mon PC. Elle montre la logique applicative : authentification, roles, clients, audits, vulnerabilites et tickets de remediation.
```
