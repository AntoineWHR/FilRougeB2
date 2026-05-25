# Politique de securite YOps

Ce document resume les choix de securite du lab YOps.  
Il est volontairement simple : l'objectif est de pouvoir l'expliquer clairement a l'oral et de montrer une logique coherente.

## Objectif

L'infrastructure doit rester administrable a distance, mais sans exposer inutilement les services internes.  
La securite repose donc sur trois idees :

- limiter les acces ;
- donner les droits par role ;
- garder une capacite de restauration ;
- surveiller les machines importantes.

## Acces distant

L'administration distante passe par Tailscale.

Cela evite d'ouvrir directement sur Internet :

- Proxmox ;
- pfSense ;
- Windows Server ;
- les serveurs Linux.

Dans une vraie entreprise, je garderais cette logique car elle reduit fortement l'exposition publique. Les employes et administrateurs se connectent via un appareil autorise au lieu d'ouvrir des ports sur la box ou sur le WAN.

## Pare-feu

pfSense est le point de passage du reseau interne YOps.

Son role :

- router le LAN interne vers Internet ;
- filtrer les flux entrants ;
- garder les logs reseau ;
- separer le reseau maison du reseau de lab ;
- autoriser l'administration depuis Tailscale.

Dans le lab actuel, le reseau interne est `10.10.10.0/24`.  
L'evolution prevue est d'ajouter des VLAN pour separer les serveurs, les clients, l'administration et une DMZ.

## Identite et droits

L'identite est geree par Active Directory.

Les droits ne sont pas donnes directement aux utilisateurs. Ils passent par des groupes :

- `GG_Direction`
- `GG_Commercial`
- `GG_SOC`
- `GG_Admin_RH_Juridique`
- `GG_IT_Support`
- `GG_Clients_Portal`

Cette methode est plus propre, car quand une personne change de service, il suffit de modifier son groupe.

## Partages fichiers

Les partages sont centralises sur `YOPS-DC01`.

Principe retenu :

- chaque service a son espace ;
- les droits d'ecriture sont limites au bon groupe ;
- la Direction peut lire plusieurs espaces ;
- le dossier `Public` sert aux documents communs.

Ce fonctionnement respecte le principe du moindre privilege.

## Postes Windows

Les postes du domaine sont controles avec des GPO.

Mesures retenues :

- politique de mot de passe ;
- verrouillage de session ;
- pare-feu Windows actif ;
- droits utilisateurs separes des droits admin ;
- configuration centralisee depuis le controleur de domaine.

## Serveurs Linux

Les serveurs Linux sont utilises pour le web, la base de donnees et la supervision.

Mesures retenues :

- services limites au strict necessaire ;
- UFW active lorsque c'est possible ;
- Fail2ban installe pour reduire les tentatives brutales ;
- base MariaDB accessible uniquement depuis les machines prevues ;
- supervision via Uptime Kuma.

## SOC et detection

Wazuh a ete ajoute comme brique SOC.

Adresse :

```text
https://10.10.10.25
```

Agents actifs :

- `YOPS-WEB01`
- `YOPS-DB01`
- `YOPS-MON01`
- `YOPS-DC01`
- `YOPS-WIN01`

Le but est de ne pas seulement verifier que les services repondent, mais aussi de suivre les evenements de securite des machines.

Wazuh permet notamment de montrer :

- une vue des endpoints ;
- des alertes classees par criticite ;
- la surveillance de serveurs Linux et Windows ;
- une base pour ajouter ensuite un honeypot.

## Sauvegardes

Les VMs principales ont ete sauvegardees avec Proxmox.

Machines concernees :

- `YOPS-DC01`
- `YOPS-WEB01`
- `YOPS-DB01`
- `YOPS-MON01`
- `YOPS-WIN01`

L'objectif n'est pas seulement d'avoir une sauvegarde, mais de pouvoir repartir rapidement si une VM est cassee pendant les tests.

## Supervision

Uptime Kuma surveille les services importants :

- pfSense ;
- controleur de domaine ;
- portail intranet ;
- base de donnees ;
- supervision elle-meme.

Pendant l'oral, c'est une preuve visuelle simple : on voit tout de suite si un service est disponible.

Wazuh complete cette supervision avec une vision securite.  
Uptime Kuma repond a la question "est-ce que le service est joignable ?", alors que Wazuh repond plutot a "qu'est-ce qui se passe sur la machine ?".

## Limites actuelles

Je n'ai pas modifie toute l'architecture en VLAN pour ne pas casser le lab juste avant la presentation.  
C'est un choix volontaire : le LAN actuel fonctionne, AD/DNS fonctionne, les partages fonctionnent et les serveurs Linux repondent.

L'evolution propre serait de faire la segmentation dans une deuxieme phase, avec tests service par service.
