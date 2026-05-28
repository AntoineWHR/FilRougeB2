# Oral DEV - version simple a dire

## 1. Introduction

Pour la partie developpement, j'ai cree une application web locale pour YOps, une entreprise de cybersecurite.

L'objectif est triple.

D'abord, le site presente les services de YOps a des clients potentiels : audit web, audit infrastructure et suivi SOC.

Ensuite, un visiteur peut s'inscrire et passer par un formulaire qui cree son espace client. Une fois connecte, ce client peut **declencher une demande d'audit en ligne** avec son perimetre, ses regles d'engagement, son urgence et sa date cible. L'admin YOps recoit la demande, l'accepte ou la refuse, et si elle est acceptee, l'audit est cree automatiquement.

Enfin, le back-office permet a l'equipe YOps de suivre tous les clients, les audits, les vulnerabilites, les tickets de remediation, les rapports, et de prendre des notes de suivi par client (echanges, alertes, reunions).

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

Le site public explique donc clairement ce que vend YOps et propose de demander un audit. Le hero ne se contente pas d'une image : il affiche un widget "Synthese client" avec un score de risque et des barres animees, un badge "SOC actif" qui pulse, et une carte "Remediation - 12 tickets traites cette semaine". Cela donne l'impression d'une application vivante, pas d'une brochure.

Ensuite, cote back-office, on doit pouvoir suivre plusieurs clients en meme temps.

Pour chaque client, on a :

- ses audits en cours et passes ;
- ses vulnerabilites trouvees, classees par criticite ;
- ses tickets de remediation ;
- ses rapports ;
- une timeline de notes pour tracer les echanges, les alertes et les decisions.

Et on a une nouvelle entree : les **demandes d'audit envoyees par les clients**, en attente de validation par l'admin.

L'application repond donc a un besoin concret : avoir une vision claire du risque client, de l'avancement des corrections, et un canal direct client-admin pour les nouvelles missions.

## 3. Demonstration rapide

### 3.1 Site public

Je commence par la page d'accueil. Je pointe :

- les services proposes ;
- la methode en 4 etapes ;
- les offres tarifaires ;
- le bouton "Demander un audit".

### 3.2 Espace client - demande d'audit

Je me connecte comme client Alphatech :

```text
client@alphatech.local
YOps-Client-2026!
```

Je montre que le client ne voit que son espace, pas la liste globale des clients.

Puis je vais sur la section "Demandes d'audit" et je remplis le formulaire. Je choisis le type d'audit, j'ecris le perimetre, je definis mes regles d'engagement (fenetres horaires, comptes de test, exclusions), je mets une urgence et une date cible. J'envoie.

La demande apparait dans "Mes demandes" avec le statut "En attente".

Je peux dire :

```text
C'est plus realiste qu'un email : la demande est tracee, dans la base, avec un statut et un historique.
```

### 3.3 Back-office admin - traitement

Je me reconnecte en admin :

```text
admin@yops.local
YOps-Admin-2026!
```

Sur le dashboard, la quick action "Demandes clients" est en surbrillance ambre, avec le nombre en attente. En dessous, le bloc "Demandes clients en attente" affiche les cartes interactives.

Je clique "Accepter" sur ma demande. Je peux donner un titre d'audit, une date de debut et un message au client. Validation.

Coulisses : l'application **cree automatiquement un audit** rattache au client, en statut "planifie", et marque la demande comme acceptee. Le client le voit instantanement dans son espace.

### 3.4 Notes client

Je vais sur une fiche client, par exemple Alphatech :

```text
http://127.0.0.1:8000/clients/1
```

Je montre la timeline "Suivi & notes". Il y a deja des notes seedees : une alerte sur le MFA, un compte-rendu d'appel, une note de preparation de demo.

J'ajoute une note de type "Alerte" avec un contenu. Elle apparait en haut de la timeline, avec mon nom, la date, et l'icone correspondant au type.

Je peux dire :

```text
Quatre types : note interne, contact, alerte, reunion. Chaque type a son icone et sa couleur. C'est l'equivalent d'un mini-CRM dans la fiche client.
```

### 3.5 Registre des vulnerabilites

Je vais sur :

```text
http://127.0.0.1:8000/vulnerabilities
```

Je montre :

- la barre de filtres par criticite, statut, et par client ;
- le champ de recherche qui filtre la table en temps reel ;
- la colonne action avec le bouton qui fait avancer le statut sans recharger toute la page ;
- le formulaire d'ajout avec un select **regroupe par client** (optgroup), donc on choisit vite l'audit cible meme avec beaucoup de clients.

### 3.6 Dashboard admin restructure

Je reviens sur le dashboard et je deroule les sections :

```text
Vue d'ensemble  -> KPI animes + quick actions
Demandes        -> les demandes clients en attente
Pilotage        -> progression des audits + actifs les plus exposes
Risque & vulns  -> dernieres failles + criticites + score par client
Activite        -> feed unifie : vulns + notes + rapports tries par date
```

Point a dire :

```text
Tout est structure en sections nommees, avec un trait accent sous chaque titre. On sait toujours ce qu'on regarde. Les chiffres apparaissent avec une animation de compteur, les barres se remplissent au scroll. Rien n'est statique : tout vient de la base.
```

## 4. Architecture du code

Le code est separe en plusieurs parties.

Les `models` representent les objets metier : Client, Audit, Vulnerability, Ticket, Report, **ClientNote** (notes de suivi), **AuditRequest** (demandes d'audit).

Les `repositories` gerent les requetes SQL vers SQLite. Chaque entite a son repository. Les requetes sont parametrees pour eviter les injections.

Les `services` contiennent la logique metier :

- `AuthService` pour l'authentification ;
- `RegistrationService` pour l'inscription d'un nouveau client ;
- `ClientRiskService` pour calculer un score de risque par client ;
- `DashboardService` qui agrege les indicateurs : KPI, top assets, progression audits, feed d'activite unifie (UNION ALL entre vulnerabilites, notes et rapports).

Les `views` generent les pages HTML.

Cette separation evite d'avoir tout le code au meme endroit. Quand on ajoute une feature comme les notes ou les demandes d'audit, on touche une entite, un repository, un service au besoin, et une vue. Le reste ne bouge pas.

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
- les tickets de remediation ;
- les rapports ;
- les notes client (`client_notes`) avec auteur, type, contenu, date ;
- les demandes d'audit (`audit_requests`) avec scope, regles, urgence, date cible, statut, message admin, et lien vers l'audit cree si accepte.

Les donnees sont reliees entre elles. Par exemple, une vulnerabilite appartient a un audit, un audit appartient a un client, une note pointe sur un client et un auteur, une demande d'audit pointe sur un client demandeur et eventuellement sur l'audit qui en decoule.

Commande a montrer :

```bash
sqlite3 app-yops-portal/data/yops_portal.sqlite ".tables"
sqlite3 app-yops-portal/data/yops_portal.sqlite "SELECT COUNT(*) FROM audit_requests WHERE status = 'pending';"
```

Si `sqlite3` n'est pas installe, je peux simplement montrer le fichier `yops_portal/core/database.py`.

## 6. Securite applicative

J'ai evite les mots de passe en clair.

Les mots de passe sont hashes avec PBKDF2 sur 260 000 iterations. Les sessions utilisent des tokens aleatoires generes par `secrets.token_urlsafe`. Les cookies de session sont en `HttpOnly` et `SameSite=Lax`.

Les requetes SQL utilisent des parametres pour eviter les injections.

Cote acces, l'application controle le role a chaque route :

- un client ne peut pas ouvrir `/clients`, `/vulnerabilities`, `/tickets` ou `/audit-requests` ;
- un client qui essaye de lire `/clients/2` est redirige s'il n'est pas client 2 ;
- l'admin et l'analyste accedent au back-office, mais seul l'admin gere `/admin/users`.

Ce n'est pas une application de production complete, mais les bases de securite sont presentes.

Fichier a montrer :

```text
app-yops-portal/yops_portal/core/security.py
```

## 7. Interface web

L'interface est responsive et utilisable sur desktop ou petit ecran.

J'ai travaille le rendu pour ne pas avoir l'impression d'une demo : palette creme et teal, ombres teintees, animations de revele au scroll, compteurs animes sur les KPI, hover spotlight sur les cartes, marquee de standards de securite sur la landing.

Sur le dashboard, les sections sont separees par des titres avec accent typographique, ce qui evite l'effet "tout au meme endroit". J'ai aussi optimise les transitions pour que le scroll reste fluide sur le back-office.

Les formulaires ont des labels, les tableaux sont scrollables horizontalement quand ils debordent, les couleurs indiquent les niveaux de risque (rouge critique, ambre haute, olive moyen, bleu faible).

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

Pour resumer, cette application couvre un cycle metier YOps complet :

1. un prospect arrive par la landing publique ;
2. il s'inscrit et obtient un compte client ;
3. il declenche une demande d'audit en ligne avec son perimetre et ses regles ;
4. l'admin YOps recoit la demande, l'accepte, l'audit est cree ;
5. l'analyste enregistre les vulnerabilites trouvees, classees par criticite ;
6. les tickets de remediation sont suivis jusqu'a cloture ;
7. les echanges avec le client sont traces dans la timeline de notes ;
8. un dashboard structure donne la vision d'ensemble a l'equipe YOps ;
9. un module Python sort des rapports CSV/JSON.

Elle utilise une base relationnelle SQLite, une architecture separee en couches (models, repositories, services, views), une interface responsive sans framework JS, et un module d'analyse Python.

Elle est volontairement locale pour rester simple a lancer pendant la demonstration.

## Questions possibles

### Pourquoi Python ?

Parce que la grille autorise Python, et que c'est rapide a lancer en local. Je peux montrer le backend, la base SQL et l'analyse de donnees sans installer un gros framework.

### Pourquoi SQLite ?

SQLite suffit pour une application locale de demonstration. C'est une vraie base relationnelle, avec tables, jointures et requetes SQL, mais sans serveur a installer.

### Pourquoi pas de framework type Flask ou Django ?

J'ai voulu montrer que je sais ecrire le HTTP, le routing, les sessions et les vues moi-meme avec la lib standard Python (`http.server`). Ca prouve que je comprends ce qu'un framework fait dans mon dos. Et ca evite une dependance externe sur une demo locale.

### C'est quoi une architecture en couches ?

C'est le fait de separer les responsabilites : les models representent les donnees, les repositories parlent a la base, les services gerent la logique metier, et les views affichent les pages. Quand j'ai ajoute les notes et les demandes d'audit, j'ai cree un model, un repository, ajoute une methode dans un service, et une section dans une vue. Le reste du code n'a pas bouge.

### Comment le risque client est calcule ?

Chaque vulnerabilite ajoute du poids selon sa criticite. Une critique pese plus qu'une haute, une haute pese plus qu'une moyenne. Le score donne une vue rapide du client le plus risque, affiche dans la section "Risque par client" du dashboard.

### Pourquoi avoir deux interfaces ?

Parce qu'un client ne doit jamais voir les donnees des autres clients. C'est une regle de base de cloisonnement. Le back-office est reserve a l'equipe YOps, tandis que l'espace client affiche seulement les informations de l'entreprise connectee.

### Comment fonctionne le flow de demande d'audit ?

Le client poste un formulaire sur `/audit-requests`. L'application enregistre une ligne dans la table `audit_requests` avec le statut "pending". Sur le dashboard admin, cette demande apparait dans une carte interactive. Si l'admin clique "Accepter", on cree un nouvel `Audit` rattache au client, on stocke son ID dans la demande, on passe le statut a "accepted". Si "Refuser", on stocke juste la decision et le message. Le client voit le resultat dans son espace.

### Comment les notes sont stockees ?

Dans une table dediee `client_notes` avec quatre colonnes principales : `client_id`, `author_id`, `kind` (note, contact, alerte, reunion), `body`. Une note appartient toujours a un client et a un auteur. On les liste triees par date decroissante, et on les affiche en timeline avec une icone par type.

### Est-ce que c'est securise ?

Pour une demo locale, oui sur les bases : mots de passe hashes PBKDF2, sessions par token aleatoire, cookies HttpOnly, requetes SQL parametrees, separation des vues selon le role, et controles d'acces serveur sur chaque route sensible. Pour de la production, il faudrait ajouter HTTPS, journalisation complete, tests automatises, CSRF tokens sur les formulaires et un controle d'acces encore plus fin.

### Pourquoi ne pas avoir fait une application cloud ?

Parce que cette partie DEV est locale. L'objectif ici est de montrer le developpement applicatif, la base de donnees, le SQL, l'interface et l'analyse Python. La partie cloud / VM / reseau est couverte par la partie INFRA.
