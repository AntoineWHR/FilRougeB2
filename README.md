# YOps Cybersecurity - Projet Fil Rouge INFRA

YOps Cybersecurity est une entreprise fictive de cybersecurite construite dans le cadre du projet fil rouge INFRA.  
Le but du projet est de mettre en place une infrastructure d'entreprise complete avec reseau, pare-feu, acces distant, Active Directory, services Linux, supervision, sauvegardes et portail intranet.

> Projet realise en environnement lab sur Proxmox. Les adresses IP, noms de domaine et services sont internes au projet.

## Schema reseau

![Plan d'adressage YOps](doc-github/assets/plan-adressage-yops.png)

## Objectifs du projet

- Concevoir une architecture reseau securisee.
- Deployer un pare-feu central avec pfSense.
- Fournir un acces distant securise avec Tailscale.
- Mettre en place un domaine Windows Active Directory.
- Gerer les utilisateurs, groupes, GPO et partages.
- Deployer des services Linux : web, base de donnees, supervision.
- Documenter l'infrastructure pour une presentation orale et un rapport.

## Architecture generale

| Zone | Role | Reseau |
|---|---|---|
| Reseau maison / WAN | Acces Internet, Proxmox, WAN pfSense | `192.168.1.0/24` |
| LAN interne YOps | Serveurs et poste client du lab | `10.10.10.0/24` |
| Tailscale | Administration distante securisee | `100.64.0.0/10` |

L'architecture repose sur deux bridges Proxmox principaux :

- `vmbr0` : reseau maison / WAN ;
- `vmbr1` : reseau interne YOps.

pfSense possede une interface WAN sur le reseau maison et une interface LAN sur le reseau YOps.  
Toutes les VMs internes utilisent `10.10.10.1` comme passerelle.

## Plan d'adressage

| Equipement | Role | Adresse |
|---|---|---|
| PC Admin / CachyOS | Poste d'administration | `192.168.1.245` |
| PC Admin / CachyOS | Tailscale | `100.71.132.89` |
| Box Internet | Passerelle maison | `192.168.1.1` |
| Proxmox wheelroot | Hyperviseur, bridge `vmbr0` | `192.168.1.253` |
| Proxmox wheelroot | Tailscale | `100.88.50.5` |
| pfSense WAN | Interface cote reseau maison | `192.168.1.40/24` |
| pfSense LAN | Passerelle LAN YOps | `10.10.10.1/24` |
| pfSense Tailscale | Administration distante | `100.94.68.82` |
| YOPS-DC01 | AD, DNS, fichiers | `10.10.10.10` |
| YOPS-WEB01 | Nginx, PHP, portail intranet | `10.10.10.20` |
| YOPS-DB01 | MariaDB | `10.10.10.21` |
| YOPS-MON01 | Uptime Kuma | `10.10.10.30` |
| YOPS-WIN01 | Client Windows domaine | `10.10.10.50` |

## Machines virtuelles

| VMID | Nom | Systeme | Role | Etat |
|---:|---|---|---|---|
| 100 | pfSense | FreeBSD / pfSense | Pare-feu, NAT, routage | OK |
| 210 | YOPS-DC01 | Windows Server 2022 | AD, DNS, fichiers, GPO | OK |
| 220 | YOPS-WEB01 | Debian | Nginx, PHP, portail intranet | OK |
| 221 | YOPS-DB01 | Debian | MariaDB | OK |
| 230 | YOPS-MON01 | Debian | Docker, Uptime Kuma | OK |
| 250 | YOPS-WIN01 | Windows 11 | Poste client domaine | OK |

## Services Windows

### Active Directory

Domaine :

```text
yops.local
```

Organisation :

```text
OU=YOps
OU=Users
OU=Computers
OU=Servers
OU=Groups
OU=Service Accounts
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
| Alice Martin | `alice.martin` | Direction |
| Hugo Bernard | `hugo.bernard` | Commercial |
| Sarah Diallo | `sarah.diallo` | SOC |
| Lea Robert | `lea.robert` | Admin/RH/Juridique |
| Nabil Moreau | `nabil.moreau` | IT Support |
| Client Demo | `client.demo` | Portail client |

### DNS

Le DNS interne est porte par `YOPS-DC01`.

Enregistrements utiles :

| Nom | Destination |
|---|---|
| `yops.local` | `10.10.10.10` |
| `YOPS-DC01.yops.local` | `10.10.10.10` |
| `portal.yops.local` | `10.10.10.20` |

### Partages

Partages crees sur `YOPS-DC01` :

- `Direction`
- `Commercial`
- `SOC`
- `Admin-RH-Juridique`
- `IT-Support`
- `Public`

Les droits sont geres par groupes Active Directory et appliques au niveau NTFS.

## Services Linux

| Serveur | Service | Validation |
|---|---|---|
| `YOPS-WEB01` | Nginx + PHP + intranet | `http://portal.yops.local` |
| `YOPS-DB01` | MariaDB | Base `yops_app` disponible |
| `YOPS-MON01` | Uptime Kuma | `http://10.10.10.30:3001` |

Le portail intranet YOps est heberge sur `YOPS-WEB01`.

## Securite

Mesures mises en place :

- pfSense comme pare-feu central.
- NAT du LAN YOps vers Internet.
- Administration distante via Tailscale.
- Acces d'administration non exposes directement sur Internet.
- Utilisateurs et droits geres via Active Directory.
- Partages controles par groupes AD.
- GPO de securite Windows.
- UFW et services Linux limites aux ports necessaires.
- Supervision avec Uptime Kuma.
- Sauvegardes Proxmox des VMs principales.

## Sauvegardes

Une sauvegarde Proxmox des VMs principales a ete realisee dans :

```text
/var/lib/vz/dump/yops
```

VMs sauvegardees :

- `YOPS-DC01`
- `YOPS-WEB01`
- `YOPS-DB01`
- `YOPS-MON01`
- `YOPS-WIN01`

## Complements pour la grille INFRA

Pour couvrir les points qui ne sont pas uniquement techniques, j'ai ajoute des documents separes :

| Sujet | Document |
|---|---|
| Budget materiel | [docs/09_BUDGET_INFRASTRUCTURE.md](docs/09_BUDGET_INFRASTRUCTURE.md) |
| Politique de securite | [docs/10_POLITIQUE_SECURITE_YOPS.md](docs/10_POLITIQUE_SECURITE_YOPS.md) |
| Cloud hybride et sauvegardes | [docs/11_CLOUD_HYBRIDE_BACKUP.md](docs/11_CLOUD_HYBRIDE_BACKUP.md) |
| Segmentation VLAN cible | [docs/12_PLAN_SEGMENTATION_VLAN_CIBLE.md](docs/12_PLAN_SEGMENTATION_VLAN_CIBLE.md) |

Ces documents ne changent pas l'infrastructure existante. Ils expliquent les choix, les limites du lab et les evolutions prevues pour une version plus proche d'une production.

## Validation rapide

Exemples de verifications utilisees pendant le projet :

```bash
curl -I http://portal.yops.local
curl -I http://10.10.10.20
curl -I http://10.10.10.30:3001
```

```powershell
nslookup yops.local
nslookup portal.yops.local
Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,DC=yops,DC=local" | Select Name,SamAccountName,Enabled
Get-ADGroup -Filter * -SearchBase "OU=Groups,OU=YOps,DC=yops,DC=local" | Select Name
Get-GPO -All | Select DisplayName
```

## Limites actuelles et ameliorations prevues

L'infrastructure actuelle fonctionne avec un LAN interne unique `10.10.10.0/24`.  
Il n'y a pas encore de VLAN reel configure en production dans le lab.

Ce choix est volontaire : le LAN actuel est stable, l'AD fonctionne, les partages fonctionnent et les services Linux repondent. La segmentation VLAN est donc documentee comme evolution cible plutot que faite dans l'urgence juste avant le rendu.

Ameliorations prevues :

- Ajouter une segmentation VLAN :
  - VLAN serveurs ;
  - VLAN clients ;
  - VLAN administration ;
  - VLAN DMZ.
- Mettre en place HTTPS interne avec une autorite de certification locale.
- Ajouter un reverse proxy pour acceder aux services avec des noms DNS propres.
- Automatiser la planification des sauvegardes Proxmox.
- Ajouter une partie cloud/hybride documentee pour repondre au sujet.
- Developper l'application web metier YOps.

## Arborescence du depot

```text
.
|-- README.md
|-- doc-github/
|   |-- README_INFRA_YOPS_ETAT_AVANCEMENT.md
|   `-- assets/
|       `-- plan-adressage-yops.png
|-- doc-oral/
|   `-- ORAL_SIMPLE_YOPS.md
|-- docs/
|   |-- 00_PLAN_GLOBAL_YOPS.md
|   |-- 01_PLAYBOOK_INFRA_PROXMOX_PFSENSE_TAILSCALE.md
|   |-- 02_PLAYBOOK_WINDOWS_SERVER_AD.md
|   |-- 03_PLAYBOOK_LINUX_SERVERS.md
|   |-- 04_PLAYBOOK_DEV_APPLICATION_YOPS.md
|   |-- 05_PLAYBOOK_SECURITE_SUPERVISION_SAUVEGARDE_CLOUD_BUDGET.md
|   |-- 06_PLAYBOOK_DEMO_ORAL.md
|   |-- 07_GUIDE_RAPPORT_LIVRABLES.md
|   |-- 08_RUNBOOK_EXECUTION_INFRA_A_Z.md
|   |-- 09_BUDGET_INFRASTRUCTURE.md
|   |-- 10_POLITIQUE_SECURITE_YOPS.md
|   |-- 11_CLOUD_HYBRIDE_BACKUP.md
|   `-- 12_PLAN_SEGMENTATION_VLAN_CIBLE.md
`-- web-intranet/
    `-- index.html
```

## Documentation complementaire

- [Etat d'avancement infrastructure](doc-github/README_INFRA_YOPS_ETAT_AVANCEMENT.md)
- [Support oral simple](doc-oral/ORAL_SIMPLE_YOPS.md)
- [Runbook d'execution A a Z](docs/08_RUNBOOK_EXECUTION_INFRA_A_Z.md)
- [Playbook Windows Server AD](docs/02_PLAYBOOK_WINDOWS_SERVER_AD.md)
- [Playbook Linux](docs/03_PLAYBOOK_LINUX_SERVERS.md)
- [Playbook securite, supervision, sauvegarde](docs/05_PLAYBOOK_SECURITE_SUPERVISION_SAUVEGARDE_CLOUD_BUDGET.md)
- [Budget infrastructure](docs/09_BUDGET_INFRASTRUCTURE.md)
- [Politique de securite YOps](docs/10_POLITIQUE_SECURITE_YOPS.md)
- [Cloud hybride et sauvegardes](docs/11_CLOUD_HYBRIDE_BACKUP.md)
- [Plan VLAN cible](docs/12_PLAN_SEGMENTATION_VLAN_CIBLE.md)
