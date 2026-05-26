# Oral DEV - version simple a dire

## 1. Introduction

Pour la partie developpement, j'ai cree une application web locale pour YOps, une entreprise de cybersecurite.

L'objectif est double.

D'abord, le site presente les services de YOps a des clients potentiels : audit web, audit infrastructure et suivi SOC.

Ensuite, quand un client fait une demande ou se connecte, l'application permet de suivre les clients, les audits, les vulnerabilites, les tickets de correction et les rapports.

Je suis parti sur une application locale en Python avec une base SQLite. Elle ne depend pas de Proxmox ni de Tailscale. Elle peut tourner directement sur mon PC.

Commande a montrer :

```bash
cd app-yops-portal
python3 run.py
```

Puis ouvrir :

```text
http://127.0.0.1:8000
```

## 2. Besoin metier

Dans une entreprise cyber, il faut d'abord convertir un prospect en client.

Le site public explique donc clairement ce que vend YOps et propose de demander un audit.

Ensuite, cote back-office, on doit pouvoir suivre plusieurs clients en meme temps.

Pour chaque client, on peut avoir des audits, des vulnerabilites trouvees, des actions de remediation, puis des rapports pour expliquer la situation.

L'application repond donc a un besoin concret : avoir une vision claire du risque client et de l'avancement des corrections.

## 3. Demonstration rapide

Je commence par montrer la page d'accueil publique.

Je montre :

- les services proposes ;
- la methode de travail ;
- les offres ;
- le bouton pour demander un audit.

Ensuite, je montre le formulaire d'inscription client.

URL :

```text
http://127.0.0.1:8000/register
```

Je peux expliquer que ce formulaire cree un client prospect et un compte client dans la base.

Apres ca, je montre la difference entre l'espace client et le back-office.

Je me connecte d'abord comme client :

```text
client@alphatech.local
YOps-Client-2026!
```

La, je montre que le client ne voit pas tous les clients de YOps. Il voit seulement son espace : ses audits, ses vulnerabilites, ses tickets et ses rapports.

Ensuite, je me connecte avec un compte administrateur pour montrer la partie back-office.

Compte de demo :

```text
admin@yops.local
YOps-Admin-2026!
```

Sur le tableau de bord, je montre :

- le nombre de clients actifs ;
- les audits en cours ;
- les vulnerabilites critiques ouvertes ;
- le taux de remediation ;
- le score de risque par client.

Ensuite je peux montrer la page Clients, ouvrir un client, puis montrer ses audits et ses vulnerabilites.

Je peux aussi montrer le registre des vulnerabilites et filtrer par criticite.

Point important a dire :

```text
Il y a volontairement deux interfaces. Le client a une vue limitee a son entreprise. L'equipe YOps a une vue back-office pour gerer tous les clients.
```

## 4. Architecture du code

Le code est separe en plusieurs parties.

Les `models` representent les objets metier : client, audit, vulnerabilite, ticket, utilisateur.

Les `repositories` gerent les requetes SQL vers SQLite.

Les `services` contiennent la logique metier, par exemple le calcul du risque client ou les indicateurs du dashboard.

Les `views` generent les pages HTML.

Cette separation evite d'avoir tout le code au meme endroit. C'est plus simple a maintenir et plus propre.

Commande a montrer :

```bash
find app-yops-portal/yops_portal -maxdepth 2 -type f | sort
```

## 5. Base de donnees

La base est relationnelle et stockee en SQLite.

Elle contient des tables pour :

- les roles ;
- les utilisateurs ;
- les clients ;
- les audits ;
- les vulnerabilites ;
- les tickets ;
- les rapports.

Les donnees sont reliees entre elles. Par exemple, une vulnerabilite appartient a un audit, et un audit appartient a un client.

Commande a montrer :

```bash
sqlite3 app-yops-portal/data/yops_portal.sqlite ".tables"
```

Si `sqlite3` n'est pas installe, je peux simplement montrer le fichier `yops_portal/core/database.py`.

## 6. Securite applicative

J'ai evite les mots de passe en clair.

Les mots de passe sont hashes avec PBKDF2. Les sessions utilisent des tokens aleatoires. Les requetes SQL utilisent des parametres pour eviter les injections SQL.

Ce n'est pas une application de production complete, mais les bases de securite sont presentes.

Fichier a montrer :

```text
app-yops-portal/yops_portal/core/security.py
```

## 7. Interface web

L'interface est responsive et utilisable sur desktop ou petit ecran.

J'ai fait une interface sobre, type outil SaaS interne, parce que l'application sert a travailler et pas a faire une page marketing.

Les formulaires ont des labels, la navigation est stable, les tableaux sont lisibles, et les couleurs indiquent les niveaux de risque.

## 8. Analyse de donnees Python

J'ai aussi ajoute un module d'analyse en Python.

Il lit la base SQLite et genere des rapports CSV et JSON :

- repartition par criticite ;
- risque par client ;
- tickets en retard ;
- evolution mensuelle ;
- actifs les plus touches.

Commande a montrer :

```bash
cd app-yops-portal
python3 analytics/analyze_yops.py
ls storage/reports
```

Ca montre que je ne fais pas seulement une interface, mais aussi de l'exploitation de donnees.

## 9. Conclusion

Pour resumer, cette application couvre le besoin metier de YOps : suivre les audits cyber et les corrections.

Elle utilise une base relationnelle, une architecture separee en couches, une interface responsive et un module d'analyse Python.

Elle est volontairement locale pour rester simple a lancer pendant la demonstration.

## Questions possibles

### Pourquoi Python ?

Parce que la grille autorise Python, et que c'est rapide a lancer en local. Je peux montrer le backend, la base SQL et l'analyse de donnees sans installer un gros framework.

### Pourquoi SQLite ?

SQLite suffit pour une application locale de demonstration. C'est une vraie base relationnelle, avec tables, jointures et requetes SQL, mais sans serveur a installer.

### C'est quoi une architecture en couches ?

C'est le fait de separer les responsabilites : les models representent les donnees, les repositories parlent a la base, les services gerent la logique metier, et les views affichent les pages.

### Comment le risque client est calcule ?

Chaque vulnerabilite ajoute du poids selon sa criticite. Une critique pese plus qu'une haute, une haute pese plus qu'une moyenne. Le score donne une vue rapide du client le plus risque.

### Pourquoi avoir deux interfaces ?

Parce qu'un client ne doit jamais voir les donnees des autres clients. C'est une regle de base de cloisonnement. Le back-office est reserve a l'equipe YOps, tandis que l'espace client affiche seulement les informations de l'entreprise connectee.

### Est-ce que c'est securise ?

Pour une demo locale, oui sur les bases : mots de passe hashes, sessions, requetes SQL parametrees et separation des vues selon le role. Pour de la production, il faudrait ajouter HTTPS, journalisation complete, tests automatises et controle d'acces encore plus fin.

### Pourquoi ne pas avoir fait une application cloud ?

Parce que cette partie DEV est locale. L'objectif ici est de montrer le developpement applicatif, la base de donnees, le SQL, l'interface et l'analyse Python.
