# Playbook demo orale - YOps

## Objectif

Preparer une demonstration fluide de 10 minutes DEV et 10 minutes INFRA.

Le but n'est pas de tout montrer, mais de prouver que l'architecture fonctionne, que les choix sont coherents et que les livrables sont maitrises.

## Pitch court

```text
YOps est une entreprise de cybersecurite. Nous avons concu une infrastructure securisee et une plateforme web interne permettant de gerer les clients, les audits, les vulnerabilites, les tickets de remediation et les rapports.

L'infrastructure repose sur Proxmox, pfSense, Windows Server, Linux et Tailscale. Tailscale remplace le VPN/IPSec traditionnel par un acces Zero Trust plus simple a administrer et plus adapte a des employes distants.
```

## Demo INFRA - 10 minutes

### 1. Vue generale

Montrer le schema reseau :

- Proxmox ;
- pfSense ;
- Tailscale ;
- LAN `10.10.10.0/24` ;
- Windows Server ;
- serveurs Linux ;
- poste client.

Message a dire :

```text
pfSense isole le lab du reseau maison, gere le NAT et filtre les flux. Tailscale sert d'acces distant securise aux administrateurs et employes.
```

### 2. Acces distant Tailscale

Depuis le PC admin :

```bash
tailscale status
tailscale ping 100.94.68.82
ssh admin@100.94.68.82
```

Montrer :

- pfSense joignable ;
- Proxmox joignable ;
- pas d'exposition publique necessaire.

### 3. pfSense

Montrer :

- WAN `192.168.1.40/24` ;
- LAN `10.10.10.1/24` ;
- OPT1 Tailscale `100.94.68.82/32` ;
- regles Tailscale vers LAN ;
- NAT LAN vers WAN.

Message a dire :

```text
Les flux entrants depuis Internet sont bloques. Les acces d'administration passent par le tailnet.
```

### 4. Windows Server / AD

Montrer :

- domaine `yops.local` ;
- OU ;
- utilisateurs ;
- groupes ;
- GPO ;
- partages.

Test :

- connexion `YOPS-WIN01` avec un utilisateur domaine ;
- `gpupdate /force` ;
- lecteur reseau visible ;
- acces autorise/refuse selon groupe.

### 5. Linux

Montrer :

- `YOPS-WEB01` repond en HTTP ;
- `YOPS-DB01` repond sur le port DB depuis le web ;
- `YOPS-MON01` supervise les services.

Commandes utiles :

```bash
curl -I http://10.10.10.20
nc -vz 10.10.10.21 3306
curl -I http://10.10.10.30:3001
```

## Demo DEV - 10 minutes

### 1. Presentation rapide

Message :

```text
La plateforme YOps centralise la gestion des clients, audits, vulnerabilites, tickets de remediation et rapports. Elle donne une vision operationnelle de l'activite cyber.
```

### 2. Connexion

Montrer :

- page login ;
- connexion admin ;
- dashboard.

### 3. Scenario metier

Enchainer :

1. creer ou ouvrir un client ;
2. creer un audit ;
3. ajouter une vulnerabilite critique ;
4. creer un ticket de remediation ;
5. montrer le dashboard mis a jour ;
6. ouvrir un rapport ;
7. se connecter comme client et montrer les restrictions.

### 4. Qualite technique

Montrer rapidement :

- migrations ;
- seeders ;
- modeles ;
- controleurs ;
- validations ;
- roles.

Message :

```text
Le code suit une architecture MVC Laravel, avec separation des responsabilites, validations serveur et gestion des droits par role.
```

## Checklist avant l'oral

### Infra

- [ ] pfSense demarre.
- [ ] Tailscale actif sur pfSense.
- [ ] Proxmox accessible.
- [ ] `YOPS-DC01` demarre.
- [ ] `YOPS-WEB01` demarre.
- [ ] `YOPS-DB01` demarre.
- [ ] `YOPS-MON01` demarre.
- [ ] `YOPS-WIN01` joint au domaine.
- [ ] DNS fonctionne.
- [ ] GPO appliquee.
- [ ] Partages accessibles.
- [ ] Supervision visible.

### DEV

- [ ] application accessible.
- [ ] compte admin fonctionne.
- [ ] compte analyste fonctionne.
- [ ] compte client fonctionne.
- [ ] seeders charges.
- [ ] dashboard rempli.
- [ ] demo scenario testee.

### Documents

- [ ] schema reseau pret.
- [ ] plan IP pret.
- [ ] politique securite prete.
- [ ] plan droits pret.
- [ ] guide Windows pret.
- [ ] guide Linux pret.
- [ ] plan sauvegarde/supervision pret.
- [ ] proposition cloud prete.
- [ ] budget pret.

## Risques et reponses

Question : pourquoi pas VPN/IPSec ?

Reponse :

```text
Le VPN/IPSec est une solution classique, mais YOps etant une entreprise cyber avec des employes distants, Tailscale apporte une approche Zero Trust plus simple a exploiter : authentification forte, acces par identite, pas d'ouverture de ports publics et administration centralisee.
```

Question : pourquoi Windows Server GUI ?

Reponse :

```text
La version GUI facilite la demonstration pedagogique de l'AD, des GPO et des droits. En production, une administration hybride GUI/PowerShell ou Server Core pourrait etre retenue.
```

Question : pourquoi Linux ?

Reponse :

```text
Linux est utilise pour les services applicatifs, la base de donnees et la supervision. Cela montre une infrastructure mixte realiste, avec Windows pour l'identite et Linux pour les services web.
```

