# Playbook infra - Proxmox, pfSense et Tailscale

## Objectif

Mettre en place l'infrastructure reseau YOps sur Proxmox avec pfSense comme pare-feu central et Tailscale comme solution d'acces distant securise.

Pour l'execution pas a pas avec toutes les commandes, suivre d'abord :

```text
docs/08_RUNBOOK_EXECUTION_INFRA_A_Z.md
```

## Etat de depart

| Element | Valeur |
|---|---|
| Proxmox LAN | 192.168.1.253/24 |
| Proxmox Tailscale | 100.88.50.5 |
| pfSense WAN | 192.168.1.40/24 |
| pfSense LAN | 10.10.10.1/24 |
| pfSense Tailscale | 100.94.68.82 |
| Gateway Internet | 192.168.1.1 |
| LAN interne lab | 10.10.10.0/24 |

## Topologie Proxmox

| Bridge | Role | Configuration |
|---|---|---|
| vmbr0 | WAN/lien maison | Bridge sur `nic0`, IP Proxmox `192.168.1.253/24` |
| vmbr1 | LAN interne YOps | Bridge prive sans IP sur l'hote |

Chaque VM interne doit avoir son interface reseau sur `vmbr1`, sauf pfSense qui doit avoir :

- une interface WAN sur `vmbr0` ;
- une interface LAN sur `vmbr1`.

## VMs a creer

| Nom | OS | CPU | RAM | Disque | Reseau |
|---|---|---:|---:|---:|---|
| YOPS-DC01 | Windows Server 2022/2025 GUI | 2 | 4 Go | 60 Go | vmbr1 |
| YOPS-WEB01 | Debian/Ubuntu Server | 2 | 2 Go | 30 Go | vmbr1 |
| YOPS-DB01 | Debian/Ubuntu Server | 2 | 2 Go | 40 Go | vmbr1 |
| YOPS-MON01 | Debian/Ubuntu Server | 2 | 2 Go | 30 Go | vmbr1 |
| YOPS-WIN01 | Windows 10/11 | 2 | 4 Go | 50 Go | vmbr1 |
| YOPS-LNX01 | Debian/Ubuntu Desktop | 2 | 2 Go | 25 Go | vmbr1 |

## Configuration pfSense

### Interfaces

| Interface | Role | IP |
|---|---|---|
| WAN | Internet | DHCP, actuellement `192.168.1.40/24` |
| LAN | Reseau interne | `10.10.10.1/24` |
| OPT1 | Tailscale | `100.94.68.82/32` |

### DHCP

Recommandation :

- pfSense conserve le DHCP ;
- plage DHCP : `10.10.10.100 - 10.10.10.199` ;
- gateway DHCP : `10.10.10.1` ;
- DNS DHCP : `10.10.10.10` apres installation de l'AD ;
- domaine DHCP : `yops.local`.

### NAT

Le NAT sortant existe deja :

```text
10.10.10.0/24 -> WAN 192.168.1.40
```

Le conserver pour permettre aux VMs internes d'acceder a Internet.

### Regles firewall recommandees

Interface LAN :

| Source | Destination | Port | Action | Justification |
|---|---|---|---|---|
| LAN net | Any | Any | Pass | Regle simple pour le lab |
| LAN net | pfSense | 80/443/22 | Pass | Admin locale |

Interface Tailscale :

| Source | Destination | Port | Action | Justification |
|---|---|---|---|---|
| 100.71.132.89 | pfSense | 22, 443, ICMP | Pass | Admin depuis poste cachywhr |
| 100.88.50.5 | pfSense | 22, 443, ICMP | Pass | Admin depuis Proxmox/tailnet |
| Tailnet | 10.10.10.0/24 | Ports utiles | Pass | Acces employes aux services internes |
| Tailnet | YOPS-WEB01 | 80, 443 | Pass | Acces application |
| Tailnet | YOPS-DC01 | DNS, Kerberos, LDAP, SMB | Pass limite | Tests AD et domaine |

Interface WAN :

- ne pas exposer l'application web ;
- ne pas exposer RDP/SSH des VMs ;
- conserver seulement les regles necessaires d'administration si besoin temporaire.

## Tailscale

Tailscale est utilise comme remplacement moderne du VPN site-a-site classique.

Commandes utiles sur pfSense :

```sh
tailscale status
tailscale ip -4
service tailscaled restart
```

Commandes utiles sur Proxmox/Linux :

```bash
tailscale status
tailscale ip -4
tailscale ping 100.94.68.82
```

## Tests de validation

Depuis le PC admin :

```bash
tailscale ping 100.94.68.82
ssh admin@100.94.68.82
ssh root@100.88.50.5
```

Depuis une VM du LAN :

```bash
ping 10.10.10.1
ping 192.168.1.1
ping 8.8.8.8
nslookup google.com
```

Depuis le PC admin via Tailscale :

```bash
ping 10.10.10.10
ping 10.10.10.20
curl -I http://10.10.10.20
```

## Points a documenter pour l'oral

- pfSense segmente le LAN interne du reseau maison ;
- Proxmox heberge les serveurs comme dans une petite infrastructure d'entreprise ;
- Tailscale remplace le VPN/IPSec et simplifie l'acces distant ;
- aucune exposition publique n'est necessaire ;
- l'administration se fait via Tailscale et non depuis Internet.
