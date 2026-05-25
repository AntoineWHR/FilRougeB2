# Playbook Windows Server - Active Directory YOps

## Objectif

Installer et configurer `YOPS-DC01`, le serveur Windows principal de YOps, avec :

- Active Directory Domain Services ;
- DNS ;
- structure OU/groupes/utilisateurs ;
- GPO ;
- serveur de fichiers ;
- droits NTFS selon les poles.

Pour les commandes PowerShell completes a executer dans l'ordre, suivre :

```text
docs/08_RUNBOOK_EXECUTION_INFRA_A_Z.md
```

## Choix d'installation

Utiliser Windows Server 2022 ou 2025 avec l'option :

```text
Desktop Experience / Experience utilisateur
```

Justification :

- plus simple pour la demonstration orale ;
- administration graphique claire ;
- compatible avec Server Manager, ADUC, DNS Manager et GPMC ;
- PowerShell reste disponible pour montrer la maitrise technique.

## Configuration IP

Sur `YOPS-DC01` :

| Parametre | Valeur |
|---|---|
| IP | 10.10.10.10 |
| Masque | 255.255.255.0 |
| Gateway | 10.10.10.1 |
| DNS avant promotion | 10.10.10.1 ou 127.0.0.1 temporaire |
| DNS apres promotion | 127.0.0.1 |
| Nom machine | YOPS-DC01 |

## Installation des roles

Dans Server Manager :

1. `Manage > Add Roles and Features`.
2. Selectionner `Active Directory Domain Services`.
3. Ajouter aussi `DNS Server`.
4. Installer.
5. Cliquer sur la notification puis `Promote this server to a domain controller`.

Parametres du domaine :

| Parametre | Valeur |
|---|---|
| New forest | yops.local |
| NetBIOS | YOPS |
| Niveau fonctionnel | Windows Server 2016 ou plus |
| DNS | Oui |
| Global Catalog | Oui |

## Structure Active Directory

Creer les OU :

```text
YOps
YOps/Users
YOps/Computers
YOps/Servers
YOps/Groups
YOps/Service Accounts
```

Creer les groupes globaux :

```text
GG_Direction
GG_Commercial
GG_SOC
GG_Admin_RH_Juridique
GG_IT_Support
GG_Clients_Portal
```

Exemple d'utilisateurs :

| Utilisateur | Login | Groupe |
|---|---|---|
| Alice Martin | alice.martin | GG_Direction |
| Hugo Bernard | hugo.bernard | GG_Commercial |
| Sarah Diallo | sarah.diallo | GG_SOC |
| Lea Robert | lea.robert | GG_Admin_RH_Juridique |
| Nabil Moreau | nabil.moreau | GG_IT_Support |

## Commandes PowerShell utiles

Lister les utilisateurs :

```powershell
Get-ADUser -Filter * | Select-Object Name,SamAccountName
```

Lister les groupes :

```powershell
Get-ADGroup -Filter * | Select-Object Name
```

Forcer l'application des GPO :

```powershell
gpupdate /force
```

Voir les GPO appliquees :

```powershell
gpresult /r
```

## GPO a creer

### GPO - Politique mots de passe

Parametres :

- longueur minimale : 12 caracteres ;
- complexite activee ;
- historique : 5 mots de passe ;
- verrouillage compte apres 5 echecs ;
- duree verrouillage : 15 minutes.

### GPO - Securite postes utilisateurs

Parametres :

- verrouillage automatique apres 10 minutes ;
- Windows Defender actif ;
- pare-feu Windows actif ;
- interdiction panneau de configuration pour les utilisateurs standards ;
- desactivation execution automatique USB.

### GPO - Lecteurs reseau

Mapper automatiquement :

| Lecteur | Chemin |
|---|---|
| `S:` | `\\YOPS-DC01\Shared` |
| `P:` | `\\YOPS-DC01\Public` |

### GPO - Fond d'ecran YOps

Configurer un fond d'ecran commun pour montrer visuellement que le poste est dans le domaine.

## Serveur de fichiers

Creer le dossier :

```text
D:\Shares
```

Partages :

```text
\\YOPS-DC01\Direction
\\YOPS-DC01\Commercial
\\YOPS-DC01\SOC
\\YOPS-DC01\Admin-RH-Juridique
\\YOPS-DC01\IT-Support
\\YOPS-DC01\Public
```

## Matrice des droits adaptee YOps

| Groupe \ Dossier | Direction | Commercial | SOC | Admin-RH-Juridique | IT-Support |
|---|---|---|---|---|---|
| Direction | Lecture/Ecriture | Lecture | Lecture | Lecture | Lecture |
| Commercial | Interdit | Lecture/Ecriture | Lecture | Interdit | Interdit |
| SOC | Interdit | Lecture | Lecture/Ecriture | Interdit | Interdit |
| Admin-RH-Juridique | Interdit | Lecture | Lecture | Lecture/Ecriture | Interdit |
| IT-Support | Interdit | Lecture | Lecture | Interdit | Lecture/Ecriture |

Bonnes pratiques :

- appliquer les droits sur groupes, jamais directement sur utilisateurs ;
- utiliser NTFS pour les droits reels ;
- utiliser les permissions de partage en `Authenticated Users: Change` ou `Everyone: Full Control` puis filtrer par NTFS ;
- retirer les droits herites si necessaire.

## Jonction du poste Windows

Sur `YOPS-WIN01` :

1. IP dans `10.10.10.0/24`.
2. DNS : `10.10.10.10`.
3. Renommer le poste `YOPS-WIN01`.
4. Joindre le domaine `yops.local`.
5. Redemarrer.
6. Se connecter avec un compte domaine.
7. Verifier les lecteurs reseau et les droits.

## Tests de validation

Depuis `YOPS-WIN01` :

```powershell
ipconfig /all
ping yops.local
nslookup yops.local
gpupdate /force
gpresult /r
```

Tests metier :

- un utilisateur SOC peut ecrire dans `SOC` ;
- un utilisateur Commercial ne peut pas ouvrir `Direction` ;
- un utilisateur Direction lit les dossiers des poles ;
- les lecteurs reseau apparaissent automatiquement ;
- la GPO de securite est appliquee.
