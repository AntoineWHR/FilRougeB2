# Oral - Projet YOps Cybersecurity

Ce document sert de fil conducteur pour l'oral.  
L'objectif n'est pas de tout lire mot pour mot, mais d'avoir une presentation qui coule naturellement.

## Plan simple de l'oral

1. Presenter YOps et le besoin.
2. Expliquer l'architecture generale.
3. Montrer le reseau et l'acces distant.
4. Presenter Windows Server : AD, DNS, utilisateurs, groupes, droits.
5. Presenter les serveurs Linux : web, base de donnees et supervision.
6. Presenter la partie SOC avec Wazuh.
7. Expliquer la securite, les sauvegardes et le cloud hybride.
8. Parler des limites actuelles et des evolutions prevues.
9. Faire une courte demonstration.
10. Conclure.

## Introduction

Bonjour, je vais presenter mon projet fil rouge : **YOps Cybersecurity**.

YOps est une entreprise fictive de cybersecurite.  
L'objectif du projet est de construire une base d'infrastructure d'entreprise : un reseau interne, un pare-feu, un domaine Windows, des utilisateurs, des droits, des serveurs Linux, de la supervision et des sauvegardes.

J'ai volontairement adapte le sujet a une entreprise cyber, parce que cela permet d'avoir une infrastructure plus coherente avec la securite, l'administration distante et la supervision.

Phrase simple :

```text
L'idee du projet, c'est de partir d'un lab Proxmox et de construire une petite infrastructure d'entreprise exploitable, securisee et documentee.
```

## Vue d'ensemble

L'infrastructure repose sur plusieurs briques :

- **Proxmox** pour heberger les machines virtuelles ;
- **pfSense** pour le pare-feu, le routage et le NAT ;
- **Tailscale** pour l'acces distant securise ;
- **Windows Server** pour Active Directory, DNS, GPO et fichiers ;
- **Linux** pour le portail web, la base de donnees et la supervision ;
- **Wazuh** pour la partie SOC et detection securite.

Le reseau interne YOps est :

```text
10.10.10.0/24
```

La passerelle du reseau interne est pfSense :

```text
10.10.10.1
```

Les machines principales sont :

| Machine | Role | IP |
|---|---|---|
| pfSense | Pare-feu / passerelle | `10.10.10.1` |
| YOPS-DC01 | AD, DNS, fichiers | `10.10.10.10` |
| YOPS-WEB01 | Portail intranet | `10.10.10.20` |
| YOPS-DB01 | Base MariaDB | `10.10.10.21` |
| Wazuh | SOC / SIEM / agents | `10.10.10.25` |
| YOPS-MON01 | Supervision Uptime Kuma | `10.10.10.30` |
| YOPS-WIN01 | Poste client domaine | `10.10.10.50` |

Phrase simple :

```text
pfSense se place entre le reseau interne YOps et le reseau maison. Les serveurs et le poste client sont dans le LAN interne, et sortent vers Internet en passant par pfSense.
```

Ce que je montre :

- le schema reseau dans le README GitHub ;
- les IPs principales ;
- le fait que tout le LAN YOps passe par `10.10.10.1`.

## Reseau et pfSense

pfSense a trois roles principaux dans mon projet :

- faire passerelle pour le LAN YOps ;
- faire du NAT vers Internet ;
- filtrer les acces avec des regles de pare-feu.

Il a aussi une interface Tailscale pour l'administration distante.

L'architecture reseau actuelle est simple :

- `vmbr0` correspond au reseau maison / WAN ;
- `vmbr1` correspond au reseau interne YOps ;
- pfSense relie les deux.

Phrase simple :

```text
J'ai separe le reseau maison du reseau de lab. Les VMs internes ne sont pas directement dans le reseau de ma box, elles passent par pfSense.
```

Commande possible depuis mon PC ou Proxmox :

```bash
ping -c 3 10.10.10.1
ping -c 3 10.10.10.10
```

Ce que je dis :

```text
Ces tests montrent que la passerelle pfSense et le controleur de domaine sont joignables depuis mon environnement d'administration.
```

## Pourquoi Tailscale

J'ai choisi Tailscale pour l'acces distant.

Tailscale permet de se connecter aux machines autorisees sans ouvrir directement les services sur Internet.  
Dans mon cas, je peux administrer Proxmox et pfSense a distance, tout en gardant les interfaces sensibles non exposees publiquement.

Phrase simple :

```text
Tailscale remplace un VPN classique dans mon lab. C'est plus simple a mettre en place, et ca correspond bien a une approche Zero Trust.
```

Points importants :

- chaque machine Tailscale a une IP en `100.x.x.x` ;
- seuls les appareils autorises peuvent rejoindre le tailnet ;
- l'administration reste possible meme a distance ;
- on evite d'exposer Proxmox ou pfSense directement sur Internet.

Commande possible depuis mon PC :

```bash
tailscale status
tailscale ping 100.94.68.82
```

Ce que je dis :

```text
Ici, je montre que pfSense est joignable via Tailscale. L'administration ne depend donc pas d'une exposition directe sur Internet.
```

## Windows Server et Active Directory

Le serveur Windows principal s'appelle :

```text
YOPS-DC01
```

Il gere le domaine :

```text
yops.local
```

Sur ce serveur, j'ai installe :

- Active Directory ;
- DNS ;
- le service de fichiers ;
- la gestion des GPO.

Phrase simple :

```text
Windows Server sert de base pour l'identite de l'entreprise. C'est lui qui gere les comptes, les groupes, les droits et les postes du domaine.
```

Commande a montrer sur `YOPS-DC01` :

```powershell
Get-ADDomain
Get-ADDomainController
```

Ce que je dis :

```text
Ces commandes prouvent que le domaine yops.local existe et que YOPS-DC01 est bien controleur de domaine.
```

## Organisation Active Directory

J'ai cree une organisation simple :

- une OU pour les utilisateurs ;
- une OU pour les ordinateurs ;
- une OU pour les serveurs ;
- une OU pour les groupes ;
- une OU pour les comptes de service.

Groupes principaux :

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

Phrase simple :

```text
Je n'attribue pas les droits directement aux utilisateurs. Je les attribue aux groupes. C'est plus propre et plus facile a maintenir.
```

Commandes a montrer :

```powershell
Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,DC=yops,DC=local" | Select Name,SamAccountName,Enabled
```

```powershell
Get-ADGroup -Filter * -SearchBase "OU=Groups,OU=YOps,DC=yops,DC=local" | Select Name
```

Ce que je dis :

```text
On voit les utilisateurs et les groupes metiers. Les droits sont ensuite rattaches aux groupes, pas aux personnes une par une.
```

## Poste client Windows

J'ai ajoute un poste client Windows :

```text
YOPS-WIN01
```

Ce poste est joint au domaine `yops.local`.

J'ai teste une connexion avec :

```text
YOPS\sarah.diallo
```

Phrase simple :

```text
Ce test prouve qu'un utilisateur du domaine peut se connecter sur un poste de l'entreprise et acceder aux ressources autorisees.
```

Ce que je montre :

- ouvrir une session sur `YOPS-WIN01` avec `YOPS\sarah.diallo` ;
- ouvrir l'explorateur ;
- acceder a `\\YOPS-DC01`.

Commande possible sur le poste client :

```powershell
whoami
gpresult /r
```

Ce que je dis :

```text
La commande whoami montre que je suis connecte avec un compte du domaine, et gpresult permet de verifier que les politiques de groupe s'appliquent.
```

## Partages et droits

J'ai cree plusieurs partages sur le serveur :

- `Direction`
- `Commercial`
- `SOC`
- `Admin-RH-Juridique`
- `IT-Support`
- `Public`

Le principe est simple :

- chaque service a son dossier ;
- les droits sont bases sur les groupes AD ;
- un utilisateur n'a pas acces a tout ;
- le dossier `Public` sert aux documents communs.

Exemple :

```text
Sarah Diallo appartient au groupe SOC. Elle peut donc ecrire dans le partage SOC, mais elle n'est pas administratrice de tout le serveur.
```

Phrase simple :

```text
Le but est de respecter le principe du moindre privilege : chaque personne a les acces necessaires pour son travail, mais pas plus.
```

Commandes a montrer sur `YOPS-DC01` :

```powershell
Get-SmbShare | Where-Object {$_.Name -in "Direction","Commercial","SOC","Admin-RH-Juridique","IT-Support","Public"} | Select Name,Path
```

```powershell
icacls C:\Shares\SOC
```

Ce que je dis :

```text
Get-SmbShare montre les partages crees. Icacls permet de montrer que les droits NTFS sont bases sur les groupes Active Directory.
```

## GPO

Les GPO servent a appliquer des regles automatiquement aux postes du domaine.

Dans le projet, elles servent notamment a montrer :

- une politique de mot de passe ;
- le verrouillage de session ;
- le pare-feu Windows ;
- des regles de securite appliquees de maniere centralisee.

GPO supplementaires retenues pour rendre la partie Windows plus professionnelle :

- **YOPS - Verrouillage session** : verrouillage automatique apres inactivite ;
- **YOPS - Audit securite** : journalisation des connexions, echecs et changements de comptes ;
- **YOPS - Defender baseline** : activation et durcissement de Microsoft Defender ;
- **YOPS - Restrictions USB** : blocage des supports amovibles pour reduire les risques d'exfiltration ;
- **YOPS - Bannier connexion** : message legal avant ouverture de session.

Phrase simple :

```text
Les GPO evitent de configurer chaque poste a la main. On definit une regle une fois, puis elle s'applique aux machines du domaine.
```

Phrase a dire au jury :

```text
J'ai separe les GPO par theme. C'est plus lisible qu'une seule grosse GPO, et en entreprise c'est plus simple a maintenir ou a desactiver si une regle pose probleme.
```

Commandes a montrer :

```powershell
Get-GPO -All | Select DisplayName
```

```powershell
gpupdate /force
```

Ce que je dis :

```text
Je montre les GPO presentes, puis gpupdate permet de forcer l'application des politiques sur une machine.
```

## DNS

Le DNS interne est porte par `YOPS-DC01`.

Il permet de resoudre :

```text
yops.local
YOPS-DC01.yops.local
portal.yops.local
```

Phrase simple :

```text
Dans un domaine Active Directory, le DNS est essentiel. Les postes doivent pouvoir trouver le controleur de domaine pour ouvrir une session et acceder aux services.
```

Commandes a montrer :

```powershell
nslookup yops.local
nslookup YOPS-DC01.yops.local
nslookup portal.yops.local
```

Ce que je dis :

```text
Ces tests montrent que le DNS interne resout le domaine, le controleur de domaine et le portail intranet.
```

## Partie Linux

J'ai ajoute une partie Linux pour ne pas avoir une infrastructure uniquement Windows.

Il y a trois serveurs :

| Serveur | Role | IP |
|---|---|---|
| YOPS-WEB01 | Nginx / PHP / portail intranet | `10.10.10.20` |
| YOPS-DB01 | MariaDB | `10.10.10.21` |
| YOPS-MON01 | Uptime Kuma | `10.10.10.30` |

Phrase simple :

```text
Windows gere l'identite et les fichiers. Linux gere les services applicatifs : web, base de donnees et supervision.
```

Commandes possibles depuis mon PC :

```bash
curl -I http://10.10.10.20
curl -I http://10.10.10.30:3001
```

Ce que je dis :

```text
Ces deux tests montrent que le serveur web et la supervision repondent depuis le reseau.
```

## Portail intranet

Le portail intranet est disponible ici :

```text
http://portal.yops.local
```

Il sert de page interne pour l'entreprise.

Il affiche :

- les acces rapides ;
- les actualites internes ;
- les espaces d'equipe ;
- les operations ;
- les services importants.

Phrase simple :

```text
Ce portail montre que le serveur web fonctionne et donne un point d'entree plus realiste pour une entreprise.
```

Ce que je montre :

- ouvrir `http://portal.yops.local` ;
- montrer que la page ressemble a un intranet ;
- montrer les liens utiles et les blocs de statut.

## Base de donnees

La base MariaDB est sur :

```text
YOPS-DB01 - 10.10.10.21
```

Une base de demonstration existe :

```text
yops_app
```

Phrase simple :

```text
La base de donnees est separee du serveur web. C'est plus propre qu'une architecture ou tout est installe sur la meme machine.
```

Commande possible depuis Proxmox :

```bash
qm guest exec 220 -- bash -lc 'mysql -h 10.10.10.21 -u yops_app -pYOps_DB_2026! -e "SHOW DATABASES;"'
```

Ce que je dis :

```text
La commande est lancee depuis le serveur web et interroge le serveur de base de donnees. Cela montre que les deux machines communiquent correctement.
```

## Supervision

La supervision de disponibilite est faite avec Uptime Kuma :

```text
http://10.10.10.30:3001
```

Elle permet de surveiller :

- pfSense ;
- le controleur de domaine ;
- le portail web ;
- la base de donnees ;
- le serveur de supervision.

Phrase simple :

```text
Uptime Kuma me permet de voir rapidement si un service important est disponible ou non.
```

Ce que je montre :

- ouvrir `http://10.10.10.30:3001` ;
- montrer les sondes vertes ;
- expliquer que c'est de la supervision de disponibilite.

## SOC et Wazuh

J'ai aussi ajoute une brique SOC avec Wazuh :

```text
https://10.10.10.25
```

Wazuh ne fait pas la meme chose qu'Uptime Kuma.

- Uptime Kuma verifie si un service repond.
- Wazuh surveille les machines, les evenements de securite, les fichiers, la configuration et les alertes.

Agents actifs dans Wazuh :

| Agent | IP | Role |
|---|---|---|
| YOPS-WEB01 | `10.10.10.20` | Serveur web Linux |
| YOPS-DB01 | `10.10.10.21` | Serveur base de donnees |
| YOPS-MON01 | `10.10.10.30` | Serveur supervision |
| YOPS-DC01 | `10.10.10.10` | Controleur de domaine Windows |
| YOPS-WIN01 | `10.10.10.50` | Poste client Windows |

Phrase simple :

```text
Uptime Kuma me dit si les services sont disponibles. Wazuh me donne une vision securite sur les serveurs et les postes.
```

Phrase a dire si le jury demande pourquoi c'est utile :

```text
Pour une entreprise cyber, ce n'est pas suffisant de savoir qu'un serveur repond. Il faut aussi surveiller ce qui se passe dessus : connexions, changements de fichiers, vulnerabilites, evenements Windows et alertes de securite.
```

Ce que je montre :

- ouvrir `https://10.10.10.25` ;
- aller dans `Endpoints` ;
- montrer les cinq agents actifs.

Phrase a dire :

```text
Ici, on voit que les serveurs Linux, le controleur de domaine et le poste Windows remontent bien dans Wazuh.
```

## Sauvegardes

J'ai realise une sauvegarde Proxmox des VMs importantes :

- `YOPS-DC01`
- `YOPS-WEB01`
- `YOPS-DB01`
- `YOPS-MON01`
- `YOPS-WIN01`

Emplacement :

```text
/var/lib/vz/dump/yops
```

Phrase simple :

```text
L'objectif est de pouvoir restaurer rapidement une machine si une erreur ou une panne arrive pendant le projet.
```

Commande a montrer sur Proxmox :

```bash
ls -lh /var/lib/vz/dump/yops
```

Ce que je dis :

```text
On voit les sauvegardes des VMs principales. Ce n'est pas juste theorique : les fichiers de backup existent vraiment.
```

## Cloud hybride

Le projet tourne localement sur Proxmox.  
Pour la partie cloud/hybride, j'ai documente une strategie simple : garder les services en local, mais envoyer une copie chiffree des sauvegardes vers un stockage cloud.

Exemples possibles :

- Azure Blob Storage ;
- bucket S3 ;
- Backblaze B2 ;
- autre stockage externe.

Phrase simple :

```text
Je ne migre pas toute l'infrastructure dans le cloud. Je garde les services localement, et j'utilise le cloud comme securite supplementaire pour les sauvegardes.
```

## Budget infrastructure

Pour le lab, le cout est faible car j'utilise du materiel deja disponible.

Pour une petite entreprise, j'ai prevu un budget cible avec :

- un serveur de virtualisation ;
- un firewall ;
- un switch manageable ;
- un stockage de sauvegarde ;
- un onduleur.

Budget estime :

```text
Budget minimum : environ 1 600 EUR
Budget confortable : environ 3 500 EUR
```

Phrase simple :

```text
Le budget montre ce qu'il faudrait prevoir pour passer du lab a une petite infrastructure reelle.
```

## VLAN et segmentation

Point important : dans le lab actuel, je n'ai pas mis en place de vrais VLAN.

Le reseau interne actuel est :

```text
10.10.10.0/24
```

Pourquoi ?

```text
J'ai garde un LAN unique pour stabiliser la demonstration. L'Active Directory, le DNS, les partages, le portail et la supervision fonctionnent. Changer les VLAN juste avant l'oral aurait ajoute un risque inutile.
```

Par contre, j'ai prevu une architecture cible :

| VLAN | Nom | Reseau | Usage |
|---:|---|---|---|
| 10 | SERVERS | `10.10.10.0/24` | AD, DNS, DB, monitoring |
| 20 | CLIENTS | `10.10.20.0/24` | Postes utilisateurs |
| 30 | ADMIN | `10.10.30.0/24` | Administration |
| 40 | DMZ | `10.10.40.0/24` | Portail web |
| 50 | GUEST | `10.10.50.0/24` | Invites / tests |

Phrase simple :

```text
Dans le lab, le reseau est simple et stable. En production, je separerais les serveurs, les clients, l'administration et la DMZ avec des VLAN et des regles pfSense.
```

## Securite globale

Les mesures de securite principales sont :

- pfSense comme pare-feu central ;
- Tailscale pour l'acces distant ;
- aucun service sensible expose directement sur Internet ;
- Active Directory pour gerer les comptes ;
- groupes AD pour gerer les droits ;
- GPO pour les postes Windows ;
- UFW et Fail2ban sur Linux ;
- sauvegardes Proxmox ;
- supervision de disponibilite avec Uptime Kuma ;
- supervision securite avec Wazuh.

Phrase simple :

```text
La securite du projet repose sur plusieurs couches : pare-feu, acces distant controle, gestion des identites, droits par groupes, supervision et sauvegardes.
```

## Ce que je montre pendant la demo

Je ne suis pas oblige de tout montrer. Le plus important est de montrer rapidement que l'infrastructure fonctionne.

### 1. Le schema reseau

Montrer le schema GitHub.

Phrase :

```text
Ici, on voit le reseau maison, pfSense, le LAN YOps, les serveurs internes et Tailscale pour l'administration distante.
```

### 2. Le domaine Windows

Sur `YOPS-DC01` :

```powershell
ipconfig /all
```

Puis :

```powershell
nslookup yops.local
nslookup portal.yops.local
```

Phrase :

```text
Le serveur est bien dans le reseau YOps et le DNS interne resout les noms du domaine.
```

### 3. Les utilisateurs et groupes

```powershell
Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,DC=yops,DC=local" | Select Name,SamAccountName,Enabled
```

```powershell
Get-ADGroup -Filter * -SearchBase "OU=Groups,OU=YOps,DC=yops,DC=local" | Select Name
```

Phrase :

```text
On voit les utilisateurs de l'entreprise et les groupes qui servent a gerer les droits.
```

### 4. Les partages

Dans l'explorateur Windows :

```text
\\YOPS-DC01
```

Phrase :

```text
Les dossiers sont centralises sur le serveur et les droits dependent des groupes Active Directory.
```

### 5. Le portail intranet

Dans un navigateur :

```text
http://portal.yops.local
```

Phrase :

```text
Le portail intranet est heberge sur Linux et sert de point d'entree interne.
```

### 6. La supervision

Dans un navigateur :

```text
http://10.10.10.30:3001
```

Phrase :

```text
Ici, je peux verifier rapidement l'etat des services principaux.
```

### 7. Le SOC Wazuh

Dans un navigateur :

```text
https://10.10.10.25
```

Montrer `Endpoints`.

Phrase :

```text
Ici, on voit les agents Wazuh actifs sur les serveurs Linux, le controleur de domaine et le poste Windows. Cela montre que les machines remontent leurs informations de securite au SOC.
```

### 8. Les sauvegardes

Sur Proxmox :

```bash
ls -lh /var/lib/vz/dump/yops
```

Phrase :

```text
On voit les sauvegardes des VMs importantes. C'est ce qui permet de restaurer en cas de probleme.
```

## Conclusion

Pour resumer, j'ai mis en place une infrastructure complete de lab :

- un hyperviseur Proxmox ;
- un pare-feu pfSense ;
- un acces distant Tailscale ;
- un domaine Active Directory ;
- des utilisateurs, groupes, droits et GPO ;
- un poste Windows joint au domaine ;
- des serveurs Linux pour le web, la base de donnees et la supervision ;
- une brique SOC avec Wazuh et cinq agents actifs ;
- un portail intranet ;
- des sauvegardes ;
- une documentation GitHub avec schema, budget, securite, cloud hybride et plan VLAN cible.

Phrase de conclusion :

```text
L'infrastructure actuelle est stable et presente les bases d'un SI d'entreprise : identite, reseau, services, supervision et securite. La prochaine etape serait de pousser la segmentation VLAN, d'ajouter du HTTPS interne et de developper l'application metier YOps.
```

# Questions / Reponses possibles

## Qu'est-ce que Tailscale ?

Tailscale est une solution d'acces distant basee sur WireGuard.  
Elle permet de creer un reseau prive entre des machines autorisees.

Dans mon projet, je l'utilise pour administrer Proxmox et pfSense sans ouvrir leurs interfaces directement sur Internet.

Reponse courte :

```text
Tailscale me permet d'acceder a mon lab a distance de maniere securisee, sans exposer les services d'administration sur le WAN.
```

## Pourquoi ne pas avoir utilise un VPN classique ?

Un VPN classique fonctionne aussi, mais il demande souvent plus de configuration : ports ouverts, certificats, routage, clients VPN.

Tailscale est plus simple pour un lab et plus moderne dans l'approche.  
Il se rapproche d'une logique Zero Trust : seuls les appareils autorises peuvent se connecter.

## Qu'est-ce que pfSense ?

pfSense est un pare-feu/routeur open source base sur FreeBSD.

Dans mon projet, il sert a :

- faire passerelle du LAN YOps ;
- faire du NAT vers Internet ;
- filtrer les flux ;
- administrer le reseau interne.

## Quelle est la difference entre WAN et LAN ?

Le WAN est le cote externe, ici le reseau maison `192.168.1.0/24`.  
Le LAN est le reseau interne YOps `10.10.10.0/24`.

pfSense est entre les deux.

## Pourquoi utiliser Proxmox ?

Proxmox permet de faire tourner plusieurs machines virtuelles sur une seule machine physique.

C'est pratique pour un projet comme celui-ci car je peux avoir :

- un pare-feu ;
- un serveur Windows ;
- plusieurs serveurs Linux ;
- un client Windows ;
- tout ca dans un seul lab.

## Qu'est-ce qu'Active Directory ?

Active Directory est le service Microsoft qui gere l'identite dans un domaine Windows.

Il sert a gerer :

- les utilisateurs ;
- les groupes ;
- les ordinateurs ;
- les droits ;
- les GPO.

## Pourquoi le DNS est important dans Active Directory ?

Les postes utilisent le DNS pour trouver le controleur de domaine.  
Sans DNS correct, l'ouverture de session, les GPO et certains services du domaine peuvent ne pas fonctionner.

## Qu'est-ce qu'une GPO ?

Une GPO est une strategie de groupe.  
Elle permet d'appliquer automatiquement des parametres aux postes ou aux utilisateurs du domaine.

Exemples :

- politique de mot de passe ;
- verrouillage de session ;
- pare-feu Windows ;
- restrictions utilisateur.

Dans mon projet, les GPO servent surtout a montrer un durcissement de base :

- verrouillage de session ;
- audit des evenements ;
- Microsoft Defender ;
- restrictions USB ;
- pare-feu Windows.

## Pourquoi creer plusieurs GPO au lieu d'une seule ?

C'est plus propre.

Si toutes les regles sont dans une seule GPO, c'est plus difficile a diagnostiquer.  
En separant par theme, je peux comprendre rapidement quelle GPO fait quoi.

Reponse courte :

```text
Je separe les GPO par role pour faciliter la lecture, le depannage et l'evolution.
```

## Pourquoi gerer les droits avec des groupes ?

Parce que c'est plus simple et plus propre.

Au lieu de donner les droits utilisateur par utilisateur, je donne les droits a un groupe.  
Ensuite, j'ajoute ou je retire les personnes du groupe.

## Qu'est-ce que le principe du moindre privilege ?

Cela veut dire qu'un utilisateur doit avoir uniquement les droits necessaires pour faire son travail.

Il ne doit pas avoir acces a tout par defaut.

## Pourquoi avoir mis du Linux ?

Le sujet ne devait pas etre uniquement Windows.  
Linux est tres utilise pour les services web, les bases de donnees et la supervision.

Dans mon projet :

- Linux heberge le portail intranet ;
- Linux heberge MariaDB ;
- Linux heberge Uptime Kuma.

## Pourquoi separer le web et la base de donnees ?

C'est plus propre et plus proche d'une vraie architecture.

Le serveur web affiche l'application ou le portail.  
Le serveur DB stocke les donnees.

Si un jour on veut securiser davantage, on peut autoriser seulement le serveur web a parler a la base.

## Qu'est-ce qu'Uptime Kuma ?

Uptime Kuma est un outil de supervision simple.

Il permet de verifier si des services sont disponibles :

- ping ;
- HTTP ;
- port TCP ;
- statut d'un service.

Dans mon projet, il sert a montrer rapidement l'etat de l'infrastructure.

## Qu'est-ce que Wazuh ?

Wazuh est une solution de securite de type SIEM/XDR.

Elle permet de centraliser des informations de securite venant des serveurs et des postes.

Dans mon projet, Wazuh surveille :

- les serveurs Linux ;
- le controleur de domaine Windows ;
- le poste client Windows.

Reponse courte :

```text
Wazuh me sert de mini-SOC. Il centralise les alertes de securite des machines importantes du lab.
```

## Quelle est la difference entre Uptime Kuma et Wazuh ?

Uptime Kuma surveille surtout la disponibilite.

Exemple :

```text
Est-ce que le portail web repond ? Est-ce que la base de donnees ecoute sur son port ?
```

Wazuh surveille la securite des machines.

Exemple :

```text
Est-ce qu'il y a des evenements suspects ? Des changements de fichiers ? Des problemes de configuration ? Des alertes sur un poste ?
```

Reponse courte :

```text
Uptime Kuma me dit si le service est joignable. Wazuh me dit ce qui se passe sur la machine.
```

## Pourquoi avoir mis un SOC dans le projet ?

Parce que l'entreprise fictive est une entreprise de cybersecurite.

Donc il est logique d'avoir une brique qui centralise les alertes et donne une vision securite de l'infrastructure.

Je ne dis pas que c'est un SOC complet comme dans une grande entreprise, mais c'est une base realiste :

- les agents sont installes ;
- les machines remontent dans Wazuh ;
- les alertes sont centralisees ;
- on peut ensuite ajouter des regles de detection plus avancees.

## C'est quoi un agent Wazuh ?

Un agent Wazuh est un petit programme installe sur une machine surveillee.

Il envoie les informations au serveur Wazuh.

Dans mon projet, les agents actifs sont :

```text
YOPS-WEB01
YOPS-DB01
YOPS-MON01
YOPS-DC01
YOPS-WIN01
```

## Pourquoi ne pas avoir mis de vrais VLAN ?

Je ne les ai pas mis techniquement pour ne pas casser le lab avant l'oral.

L'AD, le DNS, les partages, le portail et la supervision fonctionnent deja.  
Changer les VLAN aurait demande de modifier les IP, les regles pfSense, le DNS et les tests.

J'ai donc documente un plan VLAN cible, qui serait la prochaine etape propre.

## C'est quoi une DMZ ?

Une DMZ est une zone reseau separee pour les services plus exposes, par exemple un serveur web.

L'idee est d'eviter qu'un serveur web compromis donne directement acces au reseau interne complet.

## Pourquoi parler de cloud hybride ?

Parce que le sujet demande une reflexion cloud ou hybride.

Dans mon choix, les services restent locaux sur Proxmox, mais les sauvegardes peuvent etre copiees dans un stockage cloud.

C'est une approche simple et realiste pour une petite structure.

## Qu'est-ce que RPO et RTO ?

RPO : combien de donnees on accepte de perdre.  
RTO : combien de temps on accepte d'attendre avant que le service revienne.

Exemple :

```text
Si je sauvegarde une fois par jour, mon RPO est d'environ 24 heures.
```

## Pourquoi faire des sauvegardes Proxmox ?

Parce qu'en cas d'erreur, je peux restaurer une VM complete.

C'est utile pour :

- le controleur de domaine ;
- le serveur web ;
- la base de donnees ;
- la supervision ;
- le poste client.

## Qu'est-ce qui se passe si pfSense tombe ?

Le LAN interne perd sa passerelle vers Internet.  
Les machines internes peuvent encore exister, mais elles ne sortent plus correctement.

Par contre, comme Proxmox a aussi Tailscale, je peux toujours reprendre la main sur l'hyperviseur pour depanner.

## Pourquoi avoir un budget infrastructure ?

Le budget permet de montrer que le projet n'est pas seulement technique.  
Il faut aussi savoir estimer le materiel necessaire pour une vraie entreprise.

Dans mon cas, j'ai estime un budget minimum et un budget plus confortable.

## Quelles sont les limites du projet aujourd'hui ?

Les limites principales sont :

- pas encore de VLAN reel ;
- pas encore de reverse proxy HTTPS ;
- cloud hybride documente mais pas de compte cloud branche ;
- l'application metier YOps reste a developper.

Phrase simple :

```text
Le socle infrastructure est en place. Les prochaines etapes seraient la segmentation VLAN, HTTPS/reverse proxy et le developpement de l'application metier.
```
