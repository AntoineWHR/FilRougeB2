# Projet Fil Rouge - YOps Cybersecurity

## 1. Presentation

YOps est une entreprise fictive de cybersecurite. Le projet consiste a construire une infrastructure d'entreprise securisee avec :

- un pare-feu central ;
- un acces distant securise ;
- un domaine Active Directory ;
- une gestion des utilisateurs, groupes, droits et GPO ;
- une base Linux prevue pour les services web, base de donnees et supervision ;
- une future application web metier cyber.

Le sujet initial demandait une infrastructure d'entreprise avec du Windows Server, du reseau, de la securite et une partie developpement. Dans notre adaptation, l'entreprise n'est pas immobiliere mais orientee cybersecurite.

## 2. Choix d'architecture

L'infrastructure repose sur :

- **Proxmox** pour heberger les machines virtuelles ;
- **pfSense** pour le routage, le pare-feu et le NAT ;
- **Tailscale** pour l'acces distant securise ;
- **Windows Server 2022** pour Active Directory, DNS, GPO et fichiers ;
- **Linux** pour les futurs serveurs web, base de donnees et supervision.

Tailscale remplace le VPN/IPSec classique. Ce choix est coherent pour une entreprise cyber moderne car il permet un acces distant de type Zero Trust sans exposer directement les services internes sur Internet.

## 3. Adressage IP

![Plan d'adressage YOps](assets/plan-adressage-yops.png)

| Equipement | Role | IP |
|---|---|---|
| Proxmox | Hyperviseur | 192.168.1.253 |
| Proxmox | Acces Tailscale | 100.88.50.5 |
| pfSense WAN | Acces reseau maison | 192.168.1.40/24 |
| pfSense LAN | Gateway interne | 10.10.10.1/24 |
| pfSense Tailscale | Acces distant | 100.94.68.82 |
| YOPS-DC01 | AD, DNS, fichiers | 10.10.10.10 |
| YOPS-WIN01 | Client Windows domaine | 10.10.10.50 |
| YOPS-WEB01 | Serveur web Linux | 10.10.10.20 |
| YOPS-DB01 | Serveur base de donnees Linux | 10.10.10.21 |
| YOPS-MON01 | Serveur supervision Linux | 10.10.10.30 |

Reseau interne YOps :

```text
10.10.10.0/24
```

Remarque importante : l'infrastructure actuelle utilise un LAN interne unique. Il n'y a pas encore de VLAN reel configure dans le lab. Une evolution prevue consiste a segmenter le reseau en VLAN serveurs, clients, administration et DMZ.

## 4. Etat realise

### Proxmox

Proxmox est operationnel et accessible via Tailscale.

VMs presentes :

| VMID | Nom | Etat | Role |
|---:|---|---|---|
| 100 | pfSense | Running | Pare-feu |
| 210 | YOPS-DC01 | Running | Controleur de domaine |
| 220 | YOPS-WEB01 | Running | Web Linux |
| 221 | YOPS-DB01 | Running | Base MariaDB |
| 230 | YOPS-MON01 | Running | Supervision |
| 250 | YOPS-WIN01 | Running | Client Windows domaine |

### pfSense

pfSense est configure avec :

- WAN en `192.168.1.40/24` ;
- LAN en `10.10.10.1/24` ;
- interface Tailscale en `100.94.68.82/32` ;
- NAT du LAN vers Internet ;
- acces d'administration via Tailscale ;
- regles permettant au tailnet d'atteindre le LAN interne.

### Tailscale

Tailscale permet l'acces distant aux elements d'administration :

- Proxmox ;
- pfSense ;
- les services internes publies dans le LAN YOps.

L'objectif est d'eviter l'exposition directe de l'administration sur Internet.

### Windows Server - YOPS-DC01

Le serveur `YOPS-DC01` est installe avec Windows Server 2022 Standard Evaluation.

Configuration :

| Parametre | Valeur |
|---|---|
| Nom serveur | YOPS-DC01 |
| Domaine | yops.local |
| IP | 10.10.10.10 |
| Gateway | 10.10.10.1 |
| DNS | 127.0.0.1 et 10.10.10.1 |

Roles installes :

- Active Directory Domain Services ;
- DNS ;
- File Server ;
- Group Policy Management.

### Active Directory

Domaine cree :

```text
yops.local
```

Organisation :

```text
YOps
YOps/Users
YOps/Computers
YOps/Servers
YOps/Groups
YOps/Service Accounts
```

Groupes crees :

- `GG_Direction`
- `GG_Commercial`
- `GG_SOC`
- `GG_Admin_RH_Juridique`
- `GG_IT_Support`
- `GG_Clients_Portal`

Utilisateurs de demonstration :

| Utilisateur | Login | Groupe |
|---|---|---|
| Alice Martin | alice.martin | Direction |
| Hugo Bernard | hugo.bernard | Commercial |
| Sarah Diallo | sarah.diallo | SOC |
| Lea Robert | lea.robert | Admin/RH/Juridique |
| Nabil Moreau | nabil.moreau | IT Support |
| Client Demo | client.demo | Portail client |

### DNS

Le DNS interne repond correctement :

```text
yops.local -> 10.10.10.10
YOPS-DC01.yops.local -> 10.10.10.10
_ldap._tcp.dc._msdcs.yops.local -> yops-dc01.yops.local:389
```

Cela valide que le domaine est resolvable et que les enregistrements Active Directory principaux sont presents.

### Partages et droits

Des partages ont ete crees sur `YOPS-DC01` :

- Direction ;
- Commercial ;
- SOC ;
- Admin-RH-Juridique ;
- IT-Support ;
- Public.

Les droits sont bases sur les groupes AD. Le principe retenu est :

- les droits sont donnes aux groupes, pas directement aux utilisateurs ;
- chaque pole a un dossier principal ;
- la Direction a une visibilite de lecture sur plusieurs espaces ;
- chaque service a l'ecriture sur son propre dossier.

Test realise :

- connexion avec `YOPS\sarah.diallo` sur `YOPS-WIN01` ;
- acces au partage `\\YOPS-DC01\SOC` ;
- ecriture possible dans le dossier SOC car Sarah appartient au groupe `GG_SOC` ;
- restrictions gerees au niveau NTFS par groupes AD.

### GPO

GPO creees :

- `YOPS - Securite postes`
- `YOPS - Pare-feu Windows`

Politique de mot de passe configuree :

- longueur minimale : 12 caracteres ;
- complexite activee ;
- verrouillage apres plusieurs echecs ;
- historique de mots de passe.

### Client Windows - YOPS-WIN01

Le poste `YOPS-WIN01` a ete installe avec Windows 11.

Configuration :

| Parametre | Valeur |
|---|---|
| Nom machine | YOPS-WIN01 |
| IP | 10.10.10.50 |
| DNS | 10.10.10.10 |
| Domaine | yops.local |

Validation :

- poste joint au domaine ;
- connexion avec un utilisateur domaine ;
- acces aux partages du serveur ;
- test d'ecriture dans le partage SOC.

### Serveurs Linux

Trois serveurs Linux ont ete mis en place.

| Serveur | IP | Role | Etat |
|---|---|---|---|
| YOPS-WEB01 | 10.10.10.20 | Nginx, PHP, portail intranet YOps | OK |
| YOPS-DB01 | 10.10.10.21 | MariaDB, base `yops_app` | OK |
| YOPS-MON01 | 10.10.10.30 | Docker, Uptime Kuma | OK |

Validation realisee :

```text
http://10.10.10.20 -> HTTP 200
http://portal.yops.local -> portail intranet YOps
MariaDB 10.10.10.21:3306 -> actif
Base yops_app -> accessible depuis YOPS-WEB01
Uptime Kuma -> conteneur Docker actif sur 10.10.10.30:3001
```

### Portail intranet YOps

Un portail intranet a ete ajoute sur le serveur `YOPS-WEB01`.

URL :

```text
http://portal.yops.local
```

Le portail presente :

- l'etat des principaux services ;
- le plan d'adressage IP ;
- les liens utiles vers le portail, Uptime Kuma et pfSense ;
- des espaces equipes proches d'un vrai intranet d'entreprise ;
- un centre cyber avec supervision, incidents, audits et documentation.

### Supervision

Uptime Kuma est installe sur `YOPS-MON01`.

URL :

```text
http://10.10.10.30:3001
```

Moniteurs conseilles :

- pfSense LAN : `10.10.10.1` ;
- YOPS-DC01 : `10.10.10.10` ;
- YOPS-WEB01 : `http://10.10.10.20` ;
- YOPS-DB01 : port TCP `10.10.10.21:3306` ;
- YOPS-MON01 : `http://10.10.10.30:3001`.

### Sauvegardes

Une premiere sauvegarde Proxmox des VMs principales a ete realisee.

Emplacement :

```text
/var/lib/vz/dump/yops
```

VMs sauvegardees :

| VMID | Nom | Role |
|---:|---|---|
| 210 | YOPS-DC01 | Controleur de domaine |
| 220 | YOPS-WEB01 | Serveur web |
| 221 | YOPS-DB01 | Serveur base de donnees |
| 230 | YOPS-MON01 | Supervision |
| 250 | YOPS-WIN01 | Client Windows |

La strategie de sauvegarde retenue est :

- sauvegarde Proxmox des VMs importantes ;
- export de configuration pfSense apres changement majeur ;
- sauvegarde de la base MariaDB ;
- conservation de plusieurs versions selon l'espace disponible.

## 5. Prochaines etapes

Les prochaines etapes prevues sont :

1. Faire des captures pour le rapport.
2. Planifier automatiquement les sauvegardes Proxmox.
3. Developper ensuite l'application web YOps.

## 6. Validation actuelle

Etat actuel :

```text
pfSense : OK
Tailscale : OK
Windows Server : OK
Active Directory : OK
DNS principal : OK
OU/groupes/users : OK
Partages : OK
GPO : OK
YOPS-WIN01 joint au domaine : OK
Connexion Sarah : OK
Serveur web Linux : OK
Portail intranet YOps : OK
Serveur MariaDB : OK
Serveur supervision : OK
Sauvegardes Proxmox : OK
```

Le socle infrastructure Windows + Linux est donc operationnel. La suite principale est la partie developpement de l'application web YOps.
