# Plan de segmentation VLAN cible

Le lab actuel fonctionne avec un seul LAN interne :

```text
10.10.10.0/24
```

Je n'ai pas migre les VMs en VLAN pour ne pas casser l'Active Directory, le DNS, les partages et la supervision avant l'oral.  
Par contre, l'architecture cible prevoit bien une segmentation reseau.

## Pourquoi ajouter des VLAN

Un seul LAN est simple pour un lab, mais ce n'est pas ideal pour une entreprise.

Avec des VLAN, on peut separer :

- les serveurs ;
- les postes utilisateurs ;
- l'administration ;
- les services exposes ou semi-exposes ;
- les tests ou machines moins fiables ;
- les honeypots.

Cela permet de limiter les mouvements lateraux si une machine est compromise.

## Plan cible

| VLAN | Nom | Reseau | Usage |
|---:|---|---|---|
| 10 | SERVERS | `10.10.10.0/24` | AD, DNS, DB, monitoring |
| 20 | CLIENTS | `10.10.20.0/24` | Postes Windows utilisateurs |
| 30 | ADMIN | `10.10.30.0/24` | Administration Proxmox, pfSense, serveurs |
| 40 | DMZ | `10.10.40.0/24` | Portail web et services accessibles aux employes |
| 50 | GUEST | `10.10.50.0/24` | Invites ou machines de test |
| 60 | HONEYPOT | `10.10.60.0/24` | Honeypot isole, collecte Wazuh |

## Placement des machines

| Machine | Reseau actuel | Reseau cible |
|---|---|---|
| YOPS-DC01 | `10.10.10.10` | VLAN 10 SERVERS |
| YOPS-DB01 | `10.10.10.21` | VLAN 10 SERVERS |
| YOPS-MON01 | `10.10.10.30` | VLAN 10 SERVERS |
| Wazuh | `10.10.10.25` | VLAN 10 SERVERS / SOC |
| YOPS-WEB01 | `10.10.10.20` | VLAN 40 DMZ |
| YOPS-WIN01 | `10.10.10.50` | VLAN 20 CLIENTS |
| YOPS-HONEY01 | futur `10.10.60.10` | VLAN 60 HONEYPOT |
| Poste admin | Tailscale / LAN maison | VLAN 30 ADMIN ou Tailscale |

## Regles firewall cible

| Source | Destination | Autorisation |
|---|---|---|
| CLIENTS | DC | DNS, Kerberos, LDAP, SMB necessaires au domaine |
| CLIENTS | WEB/DMZ | HTTP/HTTPS |
| CLIENTS | DB | Refuse |
| WEB/DMZ | DB | MariaDB `3306` uniquement |
| WEB/DMZ | DC | DNS uniquement si besoin |
| ADMIN | Tous les VLAN | Administration controlee |
| Tailscale admin | pfSense, Proxmox, serveurs | Administration distante |
| GUEST | LAN interne | Refuse par defaut |
| HONEYPOT | LAN interne | Refuse par defaut |
| HONEYPOT | Wazuh | Agents Wazuh `1514/1515` uniquement |
| HONEYPOT | Internet | Updates/DNS/NTP uniquement |

## Cas particulier du honeypot

Le honeypot ne doit pas etre place librement dans le LAN principal.

Techniquement, son role est d'attirer ou de simuler des comportements suspects.  
Il doit donc etre isole pour eviter qu'une compromission du honeypot permette ensuite de rebondir vers l'Active Directory, les partages ou la base de donnees.

La cible propre serait :

- un reseau dedie `10.10.60.0/24` ;
- une passerelle pfSense `10.10.60.1` ;
- un honeypot `YOPS-HONEY01` en `10.10.60.10` ;
- aucune communication vers le LAN interne sauf vers Wazuh ;
- collecte des logs dans Wazuh pour la demonstration SOC.

## Methode de migration sans casser

Je ne ferais pas la migration en une seule fois.

Ordre conseille :

1. creer les VLAN dans pfSense ;
2. creer les bridges ou tags VLAN dans Proxmox ;
3. tester un VLAN vide avec une VM de test ;
4. migrer le poste client Windows ;
5. verifier AD, DNS et ouverture de session ;
6. migrer le serveur web en DMZ ;
7. autoriser uniquement les flux necessaires ;
8. ajouter le reseau honeypot separe ;
9. verifier que le honeypot ne joint pas le LAN interne ;
10. mettre a jour Uptime Kuma et Wazuh ;
11. mettre a jour la documentation.

## Choix pour le rendu actuel

Pour le rendu actuel, je garde le LAN unique car il est stable et tout fonctionne.  
Le plan VLAN est documente comme evolution cible. C'est le choix le plus raisonnable pour ne pas casser l'infrastructure avant la presentation.

Phrase simple pour l'oral :

```text
Dans le lab, j'ai garde un LAN unique pour stabiliser la demonstration. En production, je separerais les serveurs, les clients, l'administration, la DMZ et le honeypot avec des VLAN et des regles pfSense dediees.
```
