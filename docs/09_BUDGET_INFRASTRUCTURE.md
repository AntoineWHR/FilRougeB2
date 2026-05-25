# Budget infrastructure YOps

Ce budget n'est pas un devis officiel. L'idee est de montrer ce qu'il faudrait prevoir pour passer du lab Proxmox actuel a une petite infrastructure d'entreprise.

## Contexte

Dans le projet, tout tourne sur un Proxmox deja disponible. Pour le lab, le cout est donc volontairement bas.  
En production, il faudrait par contre prevoir du materiel dedie, un minimum de redondance et un vrai stockage de sauvegarde.

## Budget du lab

| Element | Role | Cout estime |
|---|---|---:|
| Machine Proxmox existante | Hebergement des VMs | 0 EUR |
| pfSense CE | Pare-feu virtuel | 0 EUR |
| Debian | Serveurs web, DB, supervision | 0 EUR |
| Windows Server Evaluation | AD, DNS, fichiers | 0 EUR |
| Windows 11 Evaluation | Poste client de test | 0 EUR |
| Tailscale | Acces distant au lab | 0 EUR |

Ce budget correspond a un environnement de demonstration. Il permet de prouver l'architecture sans acheter de materiel supplementaire.

## Budget cible pour une petite entreprise

| Element | Exemple | Role | Budget |
|---|---|---|---:|
| Serveur de virtualisation | CPU 8/12 coeurs, 64 Go RAM, SSD/NVMe | Heberger AD, web, DB, supervision | 900 a 1800 EUR |
| Stockage de sauvegarde | NAS 2 baies ou disque dedie | Garder les backups hors de l'hyperviseur | 250 a 600 EUR |
| Firewall dedie | Appliance compatible pfSense | Filtrage, NAT, VPN/Tailscale | 180 a 500 EUR |
| Switch manageable | 8 ou 16 ports VLAN | Separation des reseaux | 80 a 250 EUR |
| Onduleur | 900 a 1500 VA | Eviter les coupures brutales | 120 a 300 EUR |
| Disques de spare | SSD/HDD de remplacement | Maintenance rapide | 100 a 250 EUR |

Estimation raisonnable :

```text
Budget minimum : environ 1 600 EUR
Budget confortable : environ 3 500 EUR
```

## Choix retenu

Pour le projet, j'ai garde l'infrastructure sur Proxmox car c'est le plus simple et le plus fiable pour un lab.  
Si l'entreprise YOps devait vraiment exister, je proposerais :

- un serveur Proxmox dedie ;
- un firewall physique ou une VM pfSense bien isolee ;
- un switch manageable pour les VLAN ;
- un NAS ou disque separe pour les sauvegardes ;
- un onduleur pour proteger l'hyperviseur et le stockage.

## Pourquoi ce choix est coherent

Le but n'est pas d'acheter du materiel tres cher. Le besoin principal est d'avoir :

- assez de RAM pour plusieurs VMs ;
- du stockage rapide pour Windows Server et Linux ;
- un stockage separe pour les sauvegardes ;
- un switch capable de gerer les VLAN ;
- une alimentation protegee.

Ce budget est donc adapte a une petite structure cyber ou a un lab interne de formation.

