# Playbook securite, supervision, sauvegarde, cloud et budget

## Politique de securite

Principes :

- acces distant uniquement par Tailscale ;
- aucun service interne expose publiquement sur le WAN ;
- segmentation LAN par pfSense ;
- droits utilisateurs bases sur des groupes AD ;
- principe du moindre privilege ;
- comptes administrateurs separes des comptes utilisateurs ;
- sauvegardes regulieres et testees ;
- supervision des services critiques.

## Regles d'acces

### Administration

| Source | Destination | Ports | Justification |
|---|---|---|---|
| Poste admin Tailscale | pfSense | 22, 443 | Administration firewall |
| Poste admin Tailscale | Proxmox | 22, 8006 | Administration hyperviseur |
| Poste admin Tailscale | Serveurs Linux | 22 | Maintenance |
| Poste admin Tailscale | Windows Server | RDP | Maintenance AD |

### Utilisateurs

| Source | Destination | Ports | Justification |
|---|---|---|---|
| Employes Tailscale | YOPS-WEB01 | 80/443 | Application YOps |
| Employes LAN | YOPS-WEB01 | 80/443 | Application YOps |
| Postes domaine | YOPS-DC01 | DNS/Kerberos/LDAP/SMB | Authentification et fichiers |

## Durcissement pfSense

A faire :

- changer le mot de passe admin ;
- limiter l'administration a Tailscale et au LAN ;
- supprimer les regles WAN temporaires non necessaires ;
- garder les logs firewall actifs ;
- documenter les regles utiles ;
- eviter d'exposer SSH/HTTPS sur WAN.

## Durcissement Windows

A faire :

- GPO mot de passe fort ;
- verrouillage session ;
- pare-feu Windows actif ;
- Windows Defender actif ;
- comptes admin separes ;
- droits NTFS par groupe ;
- desactiver les services inutiles ;
- activer les journaux d'evenements.

## Durcissement Linux

A faire :

- mises a jour systeme ;
- UFW ;
- Fail2ban ;
- SSH limite au LAN/Tailscale ;
- comptes non-root pour l'administration ;
- sauvegarde de `/etc`, application et base ;
- droits stricts sur `.env`.

## Supervision

Solution simple : Uptime Kuma sur `YOPS-MON01`.

Services supervises :

| Service | Test |
|---|---|
| pfSense | Ping `10.10.10.1` |
| Proxmox | Ping/HTTPS `192.168.1.253:8006` ou Tailscale |
| AD/DNS | Ping `10.10.10.10` |
| Web | HTTP `http://10.10.10.20` |
| DB | TCP `10.10.10.21:3306` |
| Monitoring | HTTP `http://10.10.10.30:3001` |

Alerting possible :

- email ;
- Discord/Teams webhook ;
- notification locale pendant la demo.

## Plan de sauvegarde

| Cible | Frequence | Methode | Conservation |
|---|---|---|---|
| VMs Proxmox | Hebdomadaire | Backup Proxmox | 2 a 4 versions |
| Base YOps | Quotidienne | `mysqldump` | 7 a 14 jours |
| Application YOps | Quotidienne | archive `/var/www/yops` | 7 jours |
| Partages Windows | Quotidienne | copie vers disque backup | 7 a 14 jours |
| Configuration pfSense | Apres chaque changement | export XML | 3 versions |
| Documentation | A chaque modification | Git | historique complet |

Test de restauration :

- restaurer une sauvegarde DB sur une base de test ;
- restaurer un fichier partage ;
- verifier qu'un snapshot Proxmox demarre.

## Proposition cloud

Pour une version professionnelle :

### Option Azure

- Azure Virtual Network ;
- Azure Firewall ou NSG ;
- Azure VM pour application web ;
- Azure Database for MySQL/PostgreSQL ;
- Azure Backup ;
- Azure Monitor ;
- Tailscale installe sur les serveurs ou subnet router.

### Option AWS

- VPC ;
- Security Groups ;
- EC2 pour application ;
- RDS pour base ;
- AWS Backup ;
- CloudWatch ;
- Tailscale subnet router.

Choix recommande pour le rapport :

```text
Cloud hybride : infrastructure locale Proxmox pour le lab, extension possible vers Azure/AWS avec Tailscale pour conserver le modele Zero Trust.
```

## Budget indicatif

### Lab et demonstration

| Element | Quantite | Cout |
|---|---:|---:|
| Proxmox existant | 1 | 0 EUR |
| pfSense CE | 1 | 0 EUR |
| Tailscale Free/Starter | 1 | 0 EUR pour lab |
| Debian/Ubuntu | 3 | 0 EUR |
| Windows Server evaluation | 1 | 0 EUR pour test |
| Windows client evaluation | 1 | 0 EUR pour test |

### Production indicative

| Element | Quantite | Cout indicatif |
|---|---:|---:|
| Serveur physique virtualisation | 1 | 1200 - 2500 EUR |
| NAS sauvegarde | 1 | 400 - 900 EUR |
| Firewall appliance | 1 | 300 - 900 EUR |
| Switch manageable | 1 | 150 - 400 EUR |
| Onduleur | 1 | 150 - 400 EUR |
| Licences Windows Server | selon besoin | variable |
| Nom de domaine + certificat | 1 | 20 - 150 EUR/an |

