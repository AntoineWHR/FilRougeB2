# Roadmap DEV - YOps Portal

## Phase 1 - Socle applicatif

Objectif : avoir une application qui demarre en local et se connecte a sa base locale.

Taches :

1. creer le projet Laravel ;
2. configurer `.env` avec SQLite ;
3. creer le fichier local `database/database.sqlite` ;
4. creer les migrations principales ;
5. creer les seeders de demonstration ;
6. ajouter l'authentification.

Validation :

```text
L'application affiche une page de login et le dashboard charge depuis la base.
```

## Phase 2 - Modules metier

Objectif : gerer les donnees cyber.

Taches :

1. CRUD clients ;
2. CRUD audits ;
3. CRUD vulnerabilites ;
4. tickets de remediation ;
5. commentaires simples.

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
5. restrictions dans les controleurs ou policies.

Validation :

```text
Un client ne voit que ses rapports. Un commercial ne modifie pas les vulnerabilites techniques.
```

## Phase 4 - Dashboard et rapport

Objectif : rendre la demo claire.

Taches :

1. cartes statistiques ;
2. graphiques simples par criticite ;
3. page detail audit ;
4. synthese executive ;
5. export PDF si le temps le permet.

Validation :

```text
Le dashboard donne une vision rapide de l'etat cyber des clients.
```

## Phase 5 - Lancement local

Objectif : lancer l'application sur le PC pour la demonstration.

Taches :

1. installer les dependances PHP ;
2. configurer `.env` en local ;
3. lancer les migrations et seeders ;
4. demarrer le serveur local Laravel ;
5. tester depuis `http://127.0.0.1:8000`.

Validation :

```text
L'application est accessible en local sur le PC et utilise SQLite.
```

## Ce qui est prioritaire

Pour l'oral, priorite a :

1. login ;
2. dashboard ;
3. clients ;
4. audits ;
5. vulnerabilites ;
6. donnees de demo ;
7. roles simples.

Le reste est un bonus.
