# Guide rapport et livrables - YOps

## Structure conseillee du rapport

### 1. Introduction

Presenter :

- le contexte YOps ;
- le besoin metier ;
- les objectifs DEV et INFRA ;
- l'adaptation Tailscale au lieu du VPN/IPSec.

### 2. Architecture generale

Inclure :

- schema reseau ;
- explication Proxmox ;
- explication pfSense ;
- explication Tailscale ;
- role de chaque VM.

### 3. Plan d'adressage IP

Reprendre le tableau :

| IP | Nom | Role |
|---|---|---|
| 10.10.10.1 | pfSense | Gateway LAN |
| 10.10.10.10 | YOPS-DC01 | AD/DNS/Fichiers |
| 10.10.10.20 | YOPS-WEB01 | Application |
| 10.10.10.21 | YOPS-DB01 | Base |
| 10.10.10.30 | YOPS-MON01 | Supervision |
| 10.10.10.50 | YOPS-WIN01 | Client Windows |
| 10.10.10.60 | YOPS-LNX01 | Client Linux |

### 4. Services reseau

Expliquer :

- DNS ;
- DHCP ;
- NAT ;
- filtrage ;
- acces distant Tailscale.

### 5. Active Directory

Inclure :

- nom du domaine ;
- OU ;
- groupes ;
- utilisateurs ;
- GPO ;
- serveur de fichiers ;
- matrice de droits.

### 6. Linux

Inclure :

- serveur web ;
- serveur DB ;
- serveur supervision ;
- durcissement minimal ;
- commandes importantes.

### 7. Application web

Inclure :

- fonctionnalites ;
- roles ;
- modele de donnees ;
- captures ;
- installation ;
- tests.

### 8. Securite

Inclure :

- politique de securite ;
- segmentation ;
- principe du moindre privilege ;
- Tailscale ;
- firewall ;
- sauvegardes ;
- supervision.

### 9. Cloud et budget

Inclure :

- proposition cloud hybride ;
- cout lab ;
- cout production indicatif.

### 10. Conclusion

Dire :

- ce qui fonctionne ;
- les competences mobilisees ;
- les ameliorations possibles.

## Documents a produire

| Document | Source conseillee |
|---|---|
| Plan global | `00_PLAN_GLOBAL_YOPS.md` |
| Guide infra | `01_PLAYBOOK_INFRA_PROXMOX_PFSENSE_TAILSCALE.md` |
| Guide Windows Server | `02_PLAYBOOK_WINDOWS_SERVER_AD.md` |
| Guide Linux | `03_PLAYBOOK_LINUX_SERVERS.md` |
| Guide DEV | `04_PLAYBOOK_DEV_APPLICATION_YOPS.md` |
| Securite/supervision/sauvegarde | `05_PLAYBOOK_SECURITE_SUPERVISION_SAUVEGARDE_CLOUD_BUDGET.md` |
| Demo orale | `06_PLAYBOOK_DEMO_ORAL.md` |
| Execution A-Z | `08_RUNBOOK_EXECUTION_INFRA_A_Z.md` |

## Schema reseau a dessiner

Elements obligatoires :

- Internet ;
- box/routeur maison `192.168.1.1` ;
- Proxmox `192.168.1.253` / `100.88.50.5` ;
- pfSense WAN `192.168.1.40` ;
- pfSense LAN `10.10.10.1` ;
- pfSense Tailscale `100.94.68.82` ;
- LAN `10.10.10.0/24` ;
- VMs YOps ;
- employes distants via Tailscale.

Schema textuel :

```text
Internet
   |
Box 192.168.1.1
   |
Reseau maison 192.168.1.0/24
   |
Proxmox 192.168.1.253 / Tailscale 100.88.50.5
   |
pfSense WAN 192.168.1.40
pfSense LAN 10.10.10.1
pfSense Tailscale 100.94.68.82
   |
LAN YOps 10.10.10.0/24
   |
YOPS-DC01 / YOPS-WEB01 / YOPS-DB01 / YOPS-MON01 / Clients
```

## Ameliorations possibles

Si temps disponible :

- HTTPS interne avec certificat ;
- integration LDAP/AD dans Laravel ;
- sauvegarde Proxmox Backup Server ;
- monitoring Zabbix plus avance ;
- VLAN separes pour serveurs, clients et admin ;
- MFA Tailscale ;
- ACL Tailscale plus fines ;
- export PDF des rapports.
