# Plan global du projet fil rouge - YOps Cybersecurity

## 1. Contexte

YOps est une entreprise de cybersecurite specialisee dans l'audit, la supervision, la gestion des vulnerabilites et l'accompagnement des clients dans la securisation de leur systeme d'information.

Le projet consiste a livrer :

- une infrastructure reseau securisee et scalable ;
- un domaine Windows Active Directory pour la gestion des utilisateurs, groupes, GPO et droits d'acces ;
- des serveurs Linux pour l'hebergement web, la base de donnees, la supervision et les sauvegardes ;
- une application web metier permettant de gerer clients, audits, vulnerabilites, tickets, remediations et rapports ;
- une documentation technique et fonctionnelle utilisable pendant la soutenance.

Le sujet initial demande un VPN/IPSec entre le siege et les agences. Dans l'adaptation YOps, l'acces distant des employes est assure par Tailscale, ce qui correspond a une approche Zero Trust moderne. pfSense reste le pare-feu central du lab.

## 2. Existant technique

### Proxmox

| Element | Valeur |
|---|---|
| Hostname | wheelroot |
| IP LAN | 192.168.1.253/24 |
| IP Tailscale | 100.88.50.5 |
| Bridge WAN | vmbr0 |
| Bridge LAN interne | vmbr1 |
| Passerelle | 192.168.1.1 |

### pfSense

| Interface | Role | IP |
|---|---|---|
| vtnet0 | WAN | 192.168.1.40/24 |
| vtnet1 | LAN | 10.10.10.1/24 |
| tailscale0 | Acces distant | 100.94.68.82/32 |

Regles deja presentes :

- NAT du LAN `10.10.10.0/24` vers le WAN ;
- acces Tailscale vers le LAN `10.10.10.0/24` ;
- acces Tailscale vers l'administration pfSense ;
- SSH actif sur pfSense.

## 3. Architecture cible

```text
Employes distants
       |
       | Tailscale
       |
100.94.68.82 - pfSense
       |
       | LAN 10.10.10.0/24
       |
+----------------------+----------------------+----------------------+
| Windows Server       | Linux servers        | Clients de test      |
| YOPS-DC01            | YOPS-WEB01           | YOPS-WIN01           |
| AD / DNS / fichiers  | YOPS-DB01            | YOPS-LNX01           |
|                      | YOPS-MON01           |                      |
+----------------------+----------------------+----------------------+
```

## 4. Plan d'adressage IP

| IP | Nom | Systeme | Role |
|---|---|---|---|
| 10.10.10.1 | pfsense-lab | pfSense | Routeur, pare-feu, NAT, Tailscale |
| 10.10.10.10 | YOPS-DC01 | Windows Server GUI | AD DS, DNS, fichiers |
| 10.10.10.20 | YOPS-WEB01 | Debian/Ubuntu Server | Nginx, PHP, Laravel |
| 10.10.10.21 | YOPS-DB01 | Debian/Ubuntu Server | MariaDB ou PostgreSQL |
| 10.10.10.30 | YOPS-MON01 | Debian/Ubuntu Server | Uptime Kuma/Zabbix, sauvegardes |
| 10.10.10.50 | YOPS-WIN01 | Windows 10/11 | Poste employe test |
| 10.10.10.60 | YOPS-LNX01 | Debian/Ubuntu Desktop | Poste Linux test |

Reservation DHCP conseillee :

- pfSense garde le DHCP pour le lab ;
- plage dynamique : `10.10.10.100 - 10.10.10.199` ;
- serveurs en IP fixe hors plage ;
- DNS distribue aux clients : `10.10.10.10` apres installation de l'AD.

## 5. Domaine et identite

| Element | Valeur |
|---|---|
| Domaine AD | yops.local |
| NetBIOS | YOPS |
| Serveur AD | YOPS-DC01 |
| Organisation | YOps Cybersecurity |

Unites d'organisation :

- `OU=YOps`
- `OU=Users`
- `OU=Computers`
- `OU=Servers`
- `OU=Groups`
- `OU=Service Accounts`

Groupes principaux :

- `GG_Direction`
- `GG_Commercial`
- `GG_SOC`
- `GG_Admin_RH_Juridique`
- `GG_IT_Support`
- `GG_Clients_Portal`

## 6. Plateforme web YOps

Stack retenue :

- Laravel/PHP ;
- Nginx ;
- MariaDB ou PostgreSQL ;
- Git pour le versioning ;
- application accessible depuis le LAN et depuis Tailscale.

Fonctionnalites principales :

- authentification ;
- roles : administrateur, analyste SOC, commercial, client ;
- gestion des clients ;
- gestion des audits ;
- gestion des vulnerabilites ;
- criticite type CVSS simplifiee ;
- tickets de remediation ;
- rapports ;
- dashboard statistiques.

## 7. Livrables attendus

### Infra

- schema d'architecture reseau ;
- plan d'adressage IP ;
- politique de securite ;
- plan de gestion des droits ;
- guide de configuration Windows Server ;
- guide de configuration Linux ;
- plan de sauvegarde et supervision ;
- proposition cloud ;
- guide de deploiement ;
- budget materiel et licences.

### DEV

- documentation fonctionnelle ;
- documentation technique ;
- schema de base de donnees ;
- application web ;
- guide d'installation ;
- jeu de donnees de demonstration.

## 8. Ordre de realisation

Le fichier a suivre pour l'execution complete est :

```text
docs/08_RUNBOOK_EXECUTION_INFRA_A_Z.md
```

1. Stabiliser Proxmox, pfSense et Tailscale.
2. Creer les VMs avec IP fixes.
3. Installer `YOPS-DC01` en Windows Server GUI.
4. Promouvoir `YOPS-DC01` en controleur de domaine `yops.local`.
5. Configurer DNS, OU, groupes, utilisateurs, GPO et partages.
6. Joindre `YOPS-WIN01` au domaine.
7. Installer `YOPS-WEB01` avec Nginx, PHP et Laravel.
8. Installer `YOPS-DB01` avec MariaDB/PostgreSQL.
9. Deployer l'application YOps.
10. Installer `YOPS-MON01` pour supervision et sauvegardes.
11. Rediger et finaliser les documents.
12. Preparer une demonstration courte et fluide.
