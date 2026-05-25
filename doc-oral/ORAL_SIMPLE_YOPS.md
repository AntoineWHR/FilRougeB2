# Oral simple - Projet YOps

## Introduction

Bonjour, je vais presenter mon projet fil rouge : **YOps Cybersecurity**.

YOps est une entreprise fictive de cybersecurite. Elle a besoin d'une infrastructure interne securisee pour gerer ses employes, ses acces, ses fichiers et plus tard une application web metier.

L'objectif etait de mettre en place une base d'entreprise avec du reseau, de la securite, du Windows Server et du Linux.

## Idee generale

J'ai choisi une architecture avec :

- Proxmox pour heberger les machines virtuelles ;
- pfSense pour faire routeur et pare-feu ;
- Tailscale pour l'acces distant securise ;
- Windows Server pour l'Active Directory ;
- Linux pour le serveur web, la base de donnees et la supervision.

Le reseau interne de l'entreprise est :

```text
10.10.10.0/24
```

pfSense est la passerelle du reseau :

```text
10.10.10.1
```

## Pourquoi Tailscale ?

Dans le sujet initial, il etait question de VPN/IPSec.

Dans mon projet, j'ai choisi Tailscale car c'est plus moderne et plus simple pour une entreprise cyber.

Ca permet :

- de se connecter a distance sans ouvrir les services sur Internet ;
- de limiter l'acces aux machines autorisees ;
- d'avoir une approche plus proche du Zero Trust.

## Ce qui est deja en place

J'ai mis en place Proxmox avec pfSense.

pfSense a :

- une interface WAN ;
- une interface LAN ;
- une interface Tailscale ;
- du NAT pour que les machines internes sortent sur Internet ;
- des regles de pare-feu pour filtrer les acces.

Ensuite, j'ai installe un Windows Server nomme :

```text
YOPS-DC01
```

Il a l'adresse :

```text
10.10.10.10
```

Et il gere le domaine :

```text
yops.local
```

J'ai aussi ajoute :

- un poste Windows client : `YOPS-WIN01` ;
- un serveur web Linux : `YOPS-WEB01` ;
- un serveur base de donnees : `YOPS-DB01` ;
- un serveur de supervision : `YOPS-MON01`.

## Active Directory

Sur Windows Server, j'ai installe :

- Active Directory ;
- DNS ;
- la gestion des fichiers ;
- les GPO.

J'ai cree plusieurs groupes pour representer les services de l'entreprise :

- Direction ;
- Commercial ;
- SOC ;
- Admin/RH/Juridique ;
- IT Support ;
- Clients.

J'ai aussi cree des utilisateurs de test, par exemple :

- Alice Martin pour la Direction ;
- Sarah Diallo pour le SOC ;
- Nabil Moreau pour l'IT Support.

Le poste client `YOPS-WIN01` est joint au domaine. J'ai teste une connexion avec :

```text
YOPS\sarah.diallo
```

Cela prouve qu'un utilisateur du domaine peut se connecter sur un poste de l'entreprise.

## Droits fichiers

J'ai cree des dossiers partages pour chaque service :

- Direction ;
- Commercial ;
- SOC ;
- Admin-RH-Juridique ;
- IT-Support ;
- Public.

Les droits sont geres avec les groupes Active Directory.

Par exemple :

- le SOC peut ecrire dans son dossier ;
- le Commercial peut ecrire dans son dossier ;
- la Direction peut lire plusieurs dossiers ;
- les utilisateurs n'ont pas tous acces a tout.

Le but est de respecter le principe du moindre privilege.

J'ai teste avec Sarah Diallo, qui appartient au groupe SOC. Elle peut acceder au partage `SOC` et y creer un fichier.

## GPO

J'ai aussi commence a mettre en place des GPO.

Elles servent a appliquer des regles automatiquement aux postes du domaine.

Par exemple :

- politique de mot de passe ;
- verrouillage de session ;
- restrictions utilisateur ;
- configuration de securite des postes.

## Validation

Pour verifier que le domaine fonctionne, j'ai teste le DNS.

Les noms importants repondent bien :

```text
yops.local
YOPS-DC01.yops.local
```

Et les enregistrements Active Directory sont presents.

Cela montre que le controleur de domaine est bien operationnel.

## Partie Linux

J'ai aussi mis en place une partie Linux pour ne pas avoir une infrastructure uniquement Windows.

Il y a trois serveurs :

```text
YOPS-WEB01 : serveur web Nginx/PHP
YOPS-DB01  : serveur base de donnees MariaDB
YOPS-MON01 : serveur de supervision Uptime Kuma
```

Le serveur web repond sur :

```text
http://10.10.10.20
```

J'ai aussi ajoute un portail intranet plus propre :

```text
http://portal.yops.local
```

Il affiche l'etat des services, les IPs importantes, les liens utiles, les espaces equipes et un espace cyber interne.

Le serveur de supervision repond sur :

```text
http://10.10.10.30:3001
```

La base MariaDB contient une base de demonstration :

```text
yops_app
```

L'objectif est de montrer une architecture mixte : Windows pour l'identite et Linux pour les services applicatifs.

## Sauvegardes

J'ai aussi mis en place une premiere sauvegarde des machines importantes dans Proxmox.

Les VMs sauvegardees sont :

- le controleur de domaine ;
- le serveur web ;
- le serveur de base de donnees ;
- le serveur de supervision ;
- le poste client Windows.

Phrase simple :

```text
L'objectif est de pouvoir restaurer l'infrastructure en cas d'erreur ou de panne. Pour le projet, j'ai donc prevu une strategie de sauvegarde avec Proxmox, la base de donnees et la configuration pfSense.
```

## Petite demo a montrer

Pendant l'oral, je peux montrer rapidement que l'infrastructure fonctionne avec quelques commandes simples.

### 1. Montrer la configuration reseau du serveur

Sur `YOPS-DC01`, dans PowerShell :

```powershell
ipconfig /all
```

Ce que je montre :

- le nom du serveur ;
- l'adresse IP `10.10.10.10` ;
- le DNS configure sur le serveur ;
- le domaine `yops.local`.

Je peux expliquer :

```text
Ici, on voit que le serveur est bien dans le reseau interne YOps et qu'il utilise le DNS du domaine.
```

### 2. Montrer que le DNS du domaine fonctionne

Dans PowerShell :

```powershell
nslookup yops.local
nslookup YOPS-DC01.yops.local
nslookup -type=SRV _ldap._tcp.dc._msdcs.yops.local
```

Ce que je montre :

- `yops.local` repond ;
- `YOPS-DC01.yops.local` pointe vers `10.10.10.10` ;
- l'enregistrement LDAP prouve que le controleur de domaine est trouve.

Phrase simple :

```text
Ces tests montrent que le DNS Active Directory fonctionne et que les machines pourront trouver le controleur de domaine.
```

### 3. Montrer les utilisateurs crees

Dans PowerShell :

```powershell
Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,DC=yops,DC=local" | Select Name,SamAccountName,Enabled
```

Ce que je montre :

- les utilisateurs de demonstration ;
- leurs identifiants ;
- le fait que les comptes sont actifs.

Exemple :

```text
Alice Martin est dans la Direction, Sarah Diallo dans le SOC, Nabil Moreau dans l'IT Support.
```

### 4. Montrer les groupes

Dans PowerShell :

```powershell
Get-ADGroup -Filter * -SearchBase "OU=Groups,OU=YOps,DC=yops,DC=local" | Select Name
```

Ce que je montre :

- les groupes de securite ;
- chaque groupe correspond a un service de l'entreprise.

Phrase simple :

```text
Les droits ne sont pas donnes directement aux utilisateurs. Ils passent par des groupes, ce qui est plus propre et plus facile a administrer.
```

### 5. Montrer les membres d'un groupe

Dans PowerShell :

```powershell
Get-ADGroupMember "GG_SOC" | Select Name,SamAccountName
```

Ce que je montre :

- les utilisateurs du groupe SOC ;
- cela permet d'expliquer la gestion par role.

### 6. Montrer les partages fichiers

Le plus simple est de le montrer dans l'explorateur Windows.

Dans la barre d'adresse de l'explorateur :

```text
\\YOPS-DC01
```

Ou directement :

```text
\\YOPS-DC01\Public
\\YOPS-DC01\SOC
\\YOPS-DC01\Direction
```

Ce que je montre :

- les dossiers partages de l'entreprise ;
- chaque service a son espace ;
- les partages sont centralises sur le serveur Windows.

Phrase simple :

```text
Ici, on voit les partages crees sur le serveur. Chaque service a son dossier, et les droits sont geres par les groupes Active Directory.
```

Si je veux aussi le montrer en PowerShell :

```powershell
Get-SmbShare | Where-Object {$_.Name -in "Direction","Commercial","SOC","Admin-RH-Juridique","IT-Support","Public"} | Select Name,Path
```

### 7. Montrer les GPO

Dans PowerShell :

```powershell
Get-GPO -All | Select DisplayName
```

Ce que je montre :

- les GPO par defaut ;
- les GPO YOps ajoutees.

Phrase simple :

```text
Les GPO permettent d'appliquer automatiquement des regles aux postes du domaine, par exemple la politique de mot de passe ou des restrictions de securite.
```

### 8. Montrer Tailscale depuis mon poste

Sur mon PC Linux :

```bash
tailscale status
tailscale ping 100.94.68.82
```

Ce que je montre :

- pfSense est joignable via Tailscale ;
- l'administration passe par un acces securise ;
- les services ne sont pas exposes directement sur Internet.

Phrase simple :

```text
Tailscale me permet d'administrer l'infrastructure a distance sans ouvrir pfSense ou Proxmox publiquement sur Internet.
```

### 9. Montrer le portail intranet YOps

Sur mon PC ou dans un navigateur :

```bash
curl -I http://portal.yops.local
```

Ou ouvrir :

```text
http://portal.yops.local
```

Ce que je montre :

- le serveur Linux repond ;
- Nginx et PHP fonctionnent ;
- le portail intranet YOps est accessible depuis le reseau interne ;
- on voit les services, les IPs, la supervision et les liens utiles.

Phrase simple :

```text
Ce portail sert de point d'entree interne pour YOps. Il montre que le serveur web Linux fonctionne et centralise les informations utiles de l'infrastructure.
```

### 10. Montrer la base de donnees

Depuis Proxmox, via l'agent QEMU :

```bash
qm guest exec 220 -- bash -lc 'mysql -h 10.10.10.21 -u yops_app -pYOps_DB_2026! -e "SHOW DATABASES;"'
```

Ce que je montre :

- le serveur web peut joindre le serveur de base de donnees ;
- la base `yops_app` existe.

Phrase simple :

```text
Le serveur web communique avec la base de donnees MariaDB. C'est le socle qui servira pour l'application web.
```

### 11. Montrer la supervision

Dans un navigateur :

```text
http://10.10.10.30:3001
```

Ce que je montre :

- Uptime Kuma est lance ;
- il permettra de surveiller pfSense, le serveur web, le serveur DB et le controleur de domaine.

Phrase simple :

```text
La supervision permet de voir rapidement si un service important est disponible ou non.
```

### 12. Montrer les sauvegardes

Sur Proxmox :

```bash
ls -lh /var/lib/vz/dump/yops
```

Ce que je montre :

- les fichiers de sauvegarde des VMs ;
- les logs de sauvegarde ;
- la sauvegarde du controleur de domaine, du web, de la base, de la supervision et du client.

Phrase simple :

```text
Ici, on voit les sauvegardes Proxmox des machines importantes. Cela permet de restaurer rapidement un serveur si un probleme arrive.
```

## Prochaines etapes

L'infrastructure de base est maintenant en place.

La prochaine grosse etape est la partie developpement web :

- creation de l'application YOps ;
- gestion des clients ;
- gestion des audits ;
- gestion des vulnerabilites ;
- tableaux de bord et statistiques.

## Conclusion

Pour resumer, j'ai deja mis en place la base de l'infrastructure YOps :

- le routage et le pare-feu avec pfSense ;
- l'acces distant avec Tailscale ;
- le domaine Windows `yops.local` ;
- les groupes, utilisateurs, partages et GPO ;
- un client Windows joint au domaine ;
- un serveur web Linux ;
- un serveur base de donnees ;
- un serveur de supervision ;
- une premiere sauvegarde des VMs.

L'infrastructure est prete pour accueillir l'application web.
