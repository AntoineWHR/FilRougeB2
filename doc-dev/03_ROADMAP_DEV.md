# Roadmap DEV - YOps Portal

## Phase 1 - Socle applicatif

Objectif : avoir une application qui demarre en local et se connecte a sa base locale.

Taches :

1. creer le dossier `app-yops-portal` ;
2. configurer SQLite local ;
3. creer le schema relationnel ;
4. ajouter les donnees de demonstration ;
5. ajouter l'authentification locale ;
6. lancer le serveur Python.

Validation :

```text
L'application affiche une page de login et le dashboard charge depuis la base.
```

## Phase 2 - Modules metier

Objectif : gerer les donnees cyber.

Taches :

1. gestion clients ;
2. consultation audits ;
3. registre vulnerabilites avec ajout ;
4. tickets de remediation ;
5. rapports executifs.

Validation :

```text
Un analyste peut creer un client, un audit, une vulnerabilite et un ticket.
```

## Phase 3 - Roles et droits

Objectif : eviter que tout le monde ait acces a tout.

Taches :

1. role admin ;
2. role analyste SOC ;
3. role commercial ;
4. role client ;
5. controle d'acces simple dans les routes.

Validation :

```text
Un client ne voit que son espace client. Il ne voit pas la liste globale des clients ni les donnees des autres entreprises.
```

## Phase 4 - Dashboard et rapport

Objectif : rendre la demo claire.

Taches :

1. cartes statistiques ;
2. repartition par criticite ;
3. page detail audit ;
4. synthese executive ;
5. analyse Python en CSV/JSON.

Validation :

```text
Le dashboard donne une vision rapide de l'etat cyber des clients.
```

## Phase 5 - Lancement local

Objectif : lancer l'application sur le PC pour la demonstration.

Taches :

1. verifier Python 3 ;
2. lancer `python3 run.py` ;
3. ouvrir `http://127.0.0.1:8000` ;
4. tester la connexion ;
5. lancer `python3 analytics/analyze_yops.py`.

Validation :

```text
L'application est accessible en local sur le PC et utilise SQLite.
```

## Ce qui est prioritaire

Pour l'oral, priorite a :

1. landing page ;
2. inscription client ;
3. login ;
4. separation espace client / back-office ;
5. dashboard ;
6. clients ;
7. audits ;
8. vulnerabilites ;
9. donnees de demo ;
10. roles simples.

Le reste est un bonus.
