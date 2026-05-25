# Runbook execution A-Z - Infrastructure YOps

## Objectif

Ce document est le guide principal a suivre pour construire l'infrastructure YOps de A a Z.

Il couvre :

- verification Proxmox, pfSense et Tailscale ;
- creation des VMs ;
- installation Windows Server AD/DNS/fichiers/GPO ;
- installation clients Windows ;
- installation serveurs Linux web, base de donnees et supervision ;
- sauvegardes ;
- tests finaux.

La partie application metier Laravel sera faite plus tard. Ici on prepare seulement l'infrastructure pour l'accueillir.

## Conventions

Executer les commandes dans le bon environnement :

| Prefixe | Ou lancer la commande |
|---|---|
| `[PC]` | Ton poste Linux local |
| `[PVE]` | Shell root du serveur Proxmox `wheelroot` |
| `[PFSENSE]` | Shell pfSense via SSH ou console |
| `[WIN-DC01]` | PowerShell administrateur sur Windows Server |
| `[WIN-CLIENT]` | PowerShell administrateur sur le client Windows |
| `[LINUX]` | Shell du serveur Linux concerne |

Valeurs retenues :

```text
Entreprise : YOps Cybersecurity
Domaine AD : yops.local
NetBIOS : YOPS
LAN interne : 10.10.10.0/24
pfSense LAN : 10.10.10.1
pfSense Tailscale : 100.94.68.82
Proxmox LAN : 192.168.1.253
Proxmox Tailscale : 100.88.50.5
```

Plan IP :

| IP | Nom | Role |
|---|---|---|
| 10.10.10.1 | pfsense-lab | Pare-feu/gateway |
| 10.10.10.10 | YOPS-DC01 | AD, DNS, fichiers |
| 10.10.10.20 | YOPS-WEB01 | Web, Nginx, PHP |
| 10.10.10.21 | YOPS-DB01 | MariaDB |
| 10.10.10.30 | YOPS-MON01 | Uptime Kuma, sauvegardes |
| 10.10.10.50 | YOPS-WIN01 | Client Windows domaine |
| 10.10.10.60 | YOPS-LNX01 | Client Linux test |

Mots de passe de lab proposes :

```text
Compte Linux cloud-init : yopsadmin / YOps-Lab-2026!
Compte AD utilisateurs : YOps-User-2026!
Compte DSRM AD : YOps-DSRM-2026!
Compte DB app : yops_app / YOps_DB_2026!
Compte DB backup : yops_backup / YOps_Backup_2026!
```

Pour un vrai rendu, change ces mots de passe avant la soutenance et ne les mets pas dans un depot public.

## 1. Verification de l'acces Tailscale

### 1.1 Depuis ton PC

```bash
tailscale status
tailscale ping 100.94.68.82
tailscale ping 100.88.50.5
ssh admin@100.94.68.82
ssh root@100.88.50.5
```

Resultat attendu :

- `pfsense-lab` repond ;
- `wheelroot` repond ;
- SSH fonctionne vers pfSense et Proxmox.

## 2. Verification pfSense

### 2.1 Commandes de controle

```sh
ifconfig
netstat -rn
tailscale status
tailscale ip -4
pfctl -sn
pfctl -sr
```

Resultat attendu :

```text
WAN : 192.168.1.40/24
LAN : 10.10.10.1/24
TAILSCALE : 100.94.68.82/32
Gateway : 192.168.1.1
NAT : 10.10.10.0/24 vers WAN
```

### 2.2 Regles pfSense a verifier dans le GUI

Depuis le navigateur :

```text
https://100.94.68.82
```

Verifier :

```text
Firewall > Rules > OPT1/Tailscale
```

Regles minimales :

```text
Pass IPv4 TCP/ICMP - Source Tailnet - Destination This firewall - Ports 22,443,ICMP
Pass IPv4 Any - Source Tailnet - Destination 10.10.10.0/24
```

Verifier :

```text
Firewall > NAT > Outbound
```

NAT attendu :

```text
10.10.10.0/24 -> WAN address
```

### 2.3 Annoncer le LAN YOps dans Tailscale

Cette etape est indispensable pour que ton PC et les employes joignent directement les serveurs `10.10.10.x` via Tailscale.

Sur pfSense :

```sh
tailscale set --advertise-routes=10.10.10.0/24 --accept-dns=false
tailscale status
```

Si la commande `tailscale set` ne modifie rien, utiliser :

```sh
tailscale up --advertise-routes=10.10.10.0/24 --accept-dns=false
tailscale status
```

Ensuite, dans l'interface d'administration Tailscale :

```text
Machines > pfsense-lab > Edit route settings > Enable 10.10.10.0/24
```

Validation depuis ton PC :

```bash
tailscale ping 100.94.68.82
ping -c 3 10.10.10.1
```

## 3. Verification Proxmox

### 3.1 Controle reseau

Sur Proxmox :

```bash
ip -br addr
ip route
cat /etc/network/interfaces
tailscale ip -4
pvesm status
qm list
```

Resultat attendu :

```text
vmbr0 : 192.168.1.253/24
vmbr1 : bridge prive sans IP IPv4
tailscale0 : 100.88.50.5/32
gateway : 192.168.1.1
```

### 3.2 Lister les ISO disponibles

```bash
pvesm list local --content iso
```

Il faut au minimum :

- ISO Windows Server 2022 ou 2025 ;
- ISO Windows 10/11 ;
- ISO VirtIO Windows ;
- ISO Debian/Ubuntu si tu installes Linux manuellement.

Si l'ISO VirtIO n'est pas present, telecharge-le depuis ton PC puis upload dans Proxmox, ou depuis Proxmox :

```bash
cd /var/lib/vz/template/iso
wget -O virtio-win.iso https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso
```

## 4. Creation des VMs Windows dans Proxmox

Ces commandes creent les VMs. L'installation de Windows se fait ensuite via la console Proxmox.

### 4.1 Definir les variables

Sur Proxmox, adapte uniquement les noms d'ISO et le stockage si besoin apres `pvesm status` et `pvesm list local --content iso`.

```bash
export VMSTORAGE="local-lvm"
export ISO_WIN_SERVER="local:iso/Windows_Server.iso"
export ISO_WIN_CLIENT="local:iso/Windows_Client.iso"
export ISO_VIRTIO="local:iso/virtio-win.iso"
```

Si ton stockage disque n'est pas `local-lvm`, remplace `VMSTORAGE` par le stockage affiche par :

```bash
pvesm status
```

### 4.2 Creer YOPS-DC01

```bash
qm create 110 \
  --name YOPS-DC01 \
  --memory 4096 \
  --cores 2 \
  --cpu host \
  --machine q35 \
  --ostype win11 \
  --agent enabled=1 \
  --net0 virtio,bridge=vmbr1 \
  --scsihw virtio-scsi-pci \
  --scsi0 ${VMSTORAGE}:60 \
  --ide2 ${ISO_WIN_SERVER},media=cdrom \
  --ide3 ${ISO_VIRTIO},media=cdrom \
  --boot order=ide2\;scsi0 \
  --tablet 1
qm start 110
```

Installation Windows Server :

1. Ouvrir la console Proxmox de la VM `YOPS-DC01`.
2. Installer Windows Server avec `Desktop Experience`.
3. Si le disque n'apparait pas, charger le driver VirtIO depuis l'ISO VirtIO :
   - `vioscsi > w11/2k22/amd64` ou dossier equivalent ;
   - installer aussi le driver reseau `NetKVM`.
4. Une fois Windows installe, installer `virtio-win-guest-tools.exe` depuis l'ISO VirtIO.
5. Redemarrer.

### 4.3 Creer YOPS-WIN01

```bash
qm create 150 \
  --name YOPS-WIN01 \
  --memory 4096 \
  --cores 2 \
  --cpu host \
  --machine q35 \
  --ostype win11 \
  --agent enabled=1 \
  --net0 virtio,bridge=vmbr1 \
  --scsihw virtio-scsi-pci \
  --scsi0 ${VMSTORAGE}:50 \
  --ide2 ${ISO_WIN_CLIENT},media=cdrom \
  --ide3 ${ISO_VIRTIO},media=cdrom \
  --boot order=ide2\;scsi0 \
  --tablet 1
qm start 150
```

Installation Windows client :

1. Installer Windows 10/11.
2. Charger les drivers VirtIO si necessaire.
3. Installer `virtio-win-guest-tools.exe`.
4. Redemarrer.

## 5. Creation des VMs Linux dans Proxmox avec cloud-init

Cette methode evite d'installer Linux a la main pour chaque serveur.

### 5.1 Installer les outils et telecharger l'image Debian 12

Sur Proxmox :

```bash
apt update
apt install -y libguestfs-tools curl wget
mkdir -p /var/lib/vz/template/qcow2
wget -O /var/lib/vz/template/qcow2/debian-12-generic-amd64.qcow2 https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2
virt-customize -a /var/lib/vz/template/qcow2/debian-12-generic-amd64.qcow2 \
  --install qemu-guest-agent,curl,wget,git,vim,htop,net-tools,ufw,ca-certificates,sudo \
  --run-command 'systemctl enable qemu-guest-agent'
```

### 5.2 Creer le template Debian

Adapte `VMSTORAGE` si necessaire.

```bash
export VMSTORAGE="local-lvm"
qm create 9000 \
  --name debian12-cloudinit-template \
  --memory 2048 \
  --cores 2 \
  --cpu host \
  --net0 virtio,bridge=vmbr1 \
  --scsihw virtio-scsi-pci \
  --ostype l26 \
  --agent enabled=1
qm importdisk 9000 /var/lib/vz/template/qcow2/debian-12-generic-amd64.qcow2 ${VMSTORAGE}
IMPORTED_DISK=$(qm config 9000 | awk -F': ' '/^unused0:/ {print $2}')
qm set 9000 --scsi0 "${IMPORTED_DISK}"
qm set 9000 --ide2 ${VMSTORAGE}:cloudinit
qm set 9000 --boot order=scsi0
qm set 9000 --serial0 socket --vga serial0
qm template 9000
```

Si `IMPORTED_DISK` est vide, recupere le nom exact du disque avec :

```bash
qm config 9000
```

Puis configure le disque affiche sur la ligne `unused0`.

### 5.3 Preparer la cle SSH cloud-init

```bash
mkdir -p /root/.ssh
test -f /root/.ssh/id_ed25519 || ssh-keygen -t ed25519 -N "" -f /root/.ssh/id_ed25519
cp /root/.ssh/id_ed25519.pub /tmp/yops_cloudinit_key.pub
```

### 5.4 Creer YOPS-WEB01

```bash
qm clone 9000 120 --name YOPS-WEB01 --full 1
qm set 120 --memory 2048 --cores 2
qm set 120 --ipconfig0 ip=10.10.10.20/24,gw=10.10.10.1
qm set 120 --nameserver 10.10.10.1
qm set 120 --searchdomain yops.local
qm set 120 --ciuser yopsadmin
qm set 120 --cipassword 'YOps-Lab-2026!'
qm set 120 --sshkeys /tmp/yops_cloudinit_key.pub
qm resize 120 scsi0 30G
qm start 120
```

### 5.5 Creer YOPS-DB01

```bash
qm clone 9000 121 --name YOPS-DB01 --full 1
qm set 121 --memory 2048 --cores 2
qm set 121 --ipconfig0 ip=10.10.10.21/24,gw=10.10.10.1
qm set 121 --nameserver 10.10.10.1
qm set 121 --searchdomain yops.local
qm set 121 --ciuser yopsadmin
qm set 121 --cipassword 'YOps-Lab-2026!'
qm set 121 --sshkeys /tmp/yops_cloudinit_key.pub
qm resize 121 scsi0 40G
qm start 121
```

### 5.6 Creer YOPS-MON01

```bash
qm clone 9000 130 --name YOPS-MON01 --full 1
qm set 130 --memory 2048 --cores 2
qm set 130 --ipconfig0 ip=10.10.10.30/24,gw=10.10.10.1
qm set 130 --nameserver 10.10.10.1
qm set 130 --searchdomain yops.local
qm set 130 --ciuser yopsadmin
qm set 130 --cipassword 'YOps-Lab-2026!'
qm set 130 --sshkeys /tmp/yops_cloudinit_key.pub
qm resize 130 scsi0 30G
qm start 130
```

### 5.7 Creer YOPS-LNX01

```bash
qm clone 9000 160 --name YOPS-LNX01 --full 1
qm set 160 --memory 2048 --cores 2
qm set 160 --ipconfig0 ip=10.10.10.60/24,gw=10.10.10.1
qm set 160 --nameserver 10.10.10.1
qm set 160 --searchdomain yops.local
qm set 160 --ciuser yopsadmin
qm set 160 --cipassword 'YOps-Lab-2026!'
qm set 160 --sshkeys /tmp/yops_cloudinit_key.pub
qm resize 160 scsi0 25G
qm start 160
```

### 5.8 Verifier les VMs Linux

Attendre 1 a 2 minutes, puis depuis Proxmox :

```bash
ping -c 3 10.10.10.20
ping -c 3 10.10.10.21
ping -c 3 10.10.10.30
ping -c 3 10.10.10.60
ssh yopsadmin@10.10.10.20 hostname
ssh yopsadmin@10.10.10.21 hostname
ssh yopsadmin@10.10.10.30 hostname
ssh yopsadmin@10.10.10.60 hostname
```

## 6. Configuration Windows Server AD - YOPS-DC01

Toutes les commandes de cette section se lancent dans PowerShell administrateur sur `YOPS-DC01`.

### 6.1 Renommer le serveur

```powershell
Rename-Computer -NewName "YOPS-DC01" -Restart
```

Apres redemarrage, rouvrir PowerShell administrateur.

### 6.2 Configurer l'IP fixe

```powershell
$if = (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).Name
New-NetIPAddress -InterfaceAlias $if -IPAddress 10.10.10.10 -PrefixLength 24 -DefaultGateway 10.10.10.1
Set-DnsClientServerAddress -InterfaceAlias $if -ServerAddresses 10.10.10.1
ipconfig /all
ping 10.10.10.1
```

Si `New-NetIPAddress` indique qu'une IP existe deja :

```powershell
$if = (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).Name
Get-NetIPAddress -InterfaceAlias $if -AddressFamily IPv4 | Remove-NetIPAddress -Confirm:$false
New-NetIPAddress -InterfaceAlias $if -IPAddress 10.10.10.10 -PrefixLength 24 -DefaultGateway 10.10.10.1
Set-DnsClientServerAddress -InterfaceAlias $if -ServerAddresses 10.10.10.1
```

### 6.3 Installer AD DS, DNS, fichiers et GPMC

```powershell
Install-WindowsFeature AD-Domain-Services,DNS,FS-FileServer,GPMC -IncludeManagementTools
```

### 6.4 Promouvoir le serveur en controleur de domaine

```powershell
$DSRMPassword = ConvertTo-SecureString "YOps-DSRM-2026!" -AsPlainText -Force
Install-ADDSForest `
  -DomainName "yops.local" `
  -DomainNetbiosName "YOPS" `
  -InstallDNS `
  -SafeModeAdministratorPassword $DSRMPassword `
  -Force
```

Le serveur redemarre automatiquement.

### 6.5 Configuration DNS apres promotion

Apres redemarrage, se connecter en administrateur du domaine puis lancer :

```powershell
$if = (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).Name
Set-DnsClientServerAddress -InterfaceAlias $if -ServerAddresses 127.0.0.1,10.10.10.1
Add-DnsServerForwarder -IPAddress 1.1.1.1,8.8.8.8 -PassThru
Add-DnsServerPrimaryZone -NetworkId "10.10.10.0/24" -ReplicationScope "Domain"
ipconfig /flushdns
nslookup yops.local
```

### 6.6 Creer OU, groupes et utilisateurs

```powershell
Import-Module ActiveDirectory

$base = "DC=yops,DC=local"
New-ADOrganizationalUnit -Name "YOps" -Path $base -ProtectedFromAccidentalDeletion $false
New-ADOrganizationalUnit -Name "Users" -Path "OU=YOps,$base" -ProtectedFromAccidentalDeletion $false
New-ADOrganizationalUnit -Name "Computers" -Path "OU=YOps,$base" -ProtectedFromAccidentalDeletion $false
New-ADOrganizationalUnit -Name "Servers" -Path "OU=YOps,$base" -ProtectedFromAccidentalDeletion $false
New-ADOrganizationalUnit -Name "Groups" -Path "OU=YOps,$base" -ProtectedFromAccidentalDeletion $false
New-ADOrganizationalUnit -Name "Service Accounts" -Path "OU=YOps,$base" -ProtectedFromAccidentalDeletion $false

$groups = @(
  "GG_Direction",
  "GG_Commercial",
  "GG_SOC",
  "GG_Admin_RH_Juridique",
  "GG_IT_Support",
  "GG_Clients_Portal"
)

foreach ($g in $groups) {
  New-ADGroup -Name $g -SamAccountName $g -GroupScope Global -GroupCategory Security -Path "OU=Groups,OU=YOps,$base"
}

$pwd = ConvertTo-SecureString "YOps-User-2026!" -AsPlainText -Force
$users = @(
  @{Name="Alice Martin"; GivenName="Alice"; Surname="Martin"; Sam="alice.martin"; Group="GG_Direction"},
  @{Name="Hugo Bernard"; GivenName="Hugo"; Surname="Bernard"; Sam="hugo.bernard"; Group="GG_Commercial"},
  @{Name="Sarah Diallo"; GivenName="Sarah"; Surname="Diallo"; Sam="sarah.diallo"; Group="GG_SOC"},
  @{Name="Lea Robert"; GivenName="Lea"; Surname="Robert"; Sam="lea.robert"; Group="GG_Admin_RH_Juridique"},
  @{Name="Nabil Moreau"; GivenName="Nabil"; Surname="Moreau"; Sam="nabil.moreau"; Group="GG_IT_Support"},
  @{Name="Client Demo"; GivenName="Client"; Surname="Demo"; Sam="client.demo"; Group="GG_Clients_Portal"}
)

foreach ($u in $users) {
  New-ADUser `
    -Name $u.Name `
    -GivenName $u.GivenName `
    -Surname $u.Surname `
    -SamAccountName $u.Sam `
    -UserPrincipalName "$($u.Sam)@yops.local" `
    -Path "OU=Users,OU=YOps,$base" `
    -AccountPassword $pwd `
    -Enabled $true `
    -ChangePasswordAtLogon $false
  Add-ADGroupMember -Identity $u.Group -Members $u.Sam
}

Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,$base" | Select-Object Name,SamAccountName
Get-ADGroup -Filter * -SearchBase "OU=Groups,OU=YOps,$base" | Select-Object Name
```

### 6.7 Politique de mot de passe domaine

```powershell
Set-ADDefaultDomainPasswordPolicy `
  -Identity "yops.local" `
  -MinPasswordLength 12 `
  -ComplexityEnabled $true `
  -PasswordHistoryCount 5 `
  -LockoutThreshold 5 `
  -LockoutDuration "00:15:00" `
  -LockoutObservationWindow "00:15:00"

Get-ADDefaultDomainPasswordPolicy
```

### 6.8 Creer les partages fichiers et droits NTFS

```powershell
$root = "C:\Shares"
New-Item -ItemType Directory -Path $root -Force

$folders = @("Direction","Commercial","SOC","Admin-RH-Juridique","IT-Support","Public")
foreach ($f in $folders) {
  New-Item -ItemType Directory -Path "$root\$f" -Force
}

foreach ($f in $folders) {
  if (-not (Get-SmbShare -Name $f -ErrorAction SilentlyContinue)) {
    New-SmbShare -Name $f -Path "$root\$f" -ChangeAccess "Authenticated Users"
  }
}

function Reset-YOpsAcl {
  param([string]$Path)
  icacls $Path /inheritance:r
  icacls $Path /grant "YOPS\Domain Admins:(OI)(CI)(F)"
  icacls $Path /grant "SYSTEM:(OI)(CI)(F)"
}

Reset-YOpsAcl "$root\Direction"
icacls "$root\Direction" /grant "YOPS\GG_Direction:(OI)(CI)(M)"

Reset-YOpsAcl "$root\Commercial"
icacls "$root\Commercial" /grant "YOPS\GG_Direction:(OI)(CI)(RX)"
icacls "$root\Commercial" /grant "YOPS\GG_Commercial:(OI)(CI)(M)"
icacls "$root\Commercial" /grant "YOPS\GG_SOC:(OI)(CI)(RX)"
icacls "$root\Commercial" /grant "YOPS\GG_Admin_RH_Juridique:(OI)(CI)(RX)"
icacls "$root\Commercial" /grant "YOPS\GG_IT_Support:(OI)(CI)(RX)"

Reset-YOpsAcl "$root\SOC"
icacls "$root\SOC" /grant "YOPS\GG_Direction:(OI)(CI)(RX)"
icacls "$root\SOC" /grant "YOPS\GG_Commercial:(OI)(CI)(RX)"
icacls "$root\SOC" /grant "YOPS\GG_SOC:(OI)(CI)(M)"
icacls "$root\SOC" /grant "YOPS\GG_Admin_RH_Juridique:(OI)(CI)(RX)"
icacls "$root\SOC" /grant "YOPS\GG_IT_Support:(OI)(CI)(RX)"

Reset-YOpsAcl "$root\Admin-RH-Juridique"
icacls "$root\Admin-RH-Juridique" /grant "YOPS\GG_Direction:(OI)(CI)(RX)"
icacls "$root\Admin-RH-Juridique" /grant "YOPS\GG_Admin_RH_Juridique:(OI)(CI)(M)"

Reset-YOpsAcl "$root\IT-Support"
icacls "$root\IT-Support" /grant "YOPS\GG_Direction:(OI)(CI)(RX)"
icacls "$root\IT-Support" /grant "YOPS\GG_IT_Support:(OI)(CI)(M)"

Reset-YOpsAcl "$root\Public"
icacls "$root\Public" /grant "YOPS\Domain Users:(OI)(CI)(M)"

Get-SmbShare | Where-Object {$_.Name -in $folders}
```

### 6.9 Script de lecteur reseau automatique

```powershell
$scriptPath = "C:\Windows\SYSVOL\sysvol\yops.local\scripts\map-drives.bat"
@"
@echo off
net use P: /delete /yes >nul 2>&1
net use P: \\YOPS-DC01\Public /persistent:no
"@ | Set-Content -Path $scriptPath -Encoding ASCII

Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,DC=yops,DC=local" | Set-ADUser -ScriptPath "map-drives.bat"
```

### 6.10 GPO securite postes

```powershell
Import-Module GroupPolicy

New-GPO -Name "YOPS - Securite postes"
New-GPLink -Name "YOPS - Securite postes" -Target "OU=Computers,OU=YOps,DC=yops,DC=local"
New-GPLink -Name "YOPS - Securite postes" -Target "OU=Users,OU=YOps,DC=yops,DC=local"

Set-GPRegistryValue -Name "YOPS - Securite postes" `
  -Key "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop" `
  -ValueName "ScreenSaveActive" -Type String -Value "1"

Set-GPRegistryValue -Name "YOPS - Securite postes" `
  -Key "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop" `
  -ValueName "ScreenSaverIsSecure" -Type String -Value "1"

Set-GPRegistryValue -Name "YOPS - Securite postes" `
  -Key "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop" `
  -ValueName "ScreenSaveTimeOut" -Type String -Value "600"

Set-GPRegistryValue -Name "YOPS - Securite postes" `
  -Key "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" `
  -ValueName "NoControlPanel" -Type DWord -Value 1

New-GPO -Name "YOPS - Pare-feu Windows"
New-GPLink -Name "YOPS - Pare-feu Windows" -Target "OU=Computers,OU=YOps,DC=yops,DC=local"

Get-GPO -All | Select-Object DisplayName
```

### 6.11 Ajouter les enregistrements DNS internes

```powershell
Add-DnsServerResourceRecordA -ZoneName "yops.local" -Name "pfsense" -IPv4Address "10.10.10.1" -CreatePtr
Add-DnsServerResourceRecordA -ZoneName "yops.local" -Name "web" -IPv4Address "10.10.10.20" -CreatePtr
Add-DnsServerResourceRecordA -ZoneName "yops.local" -Name "db" -IPv4Address "10.10.10.21" -CreatePtr
Add-DnsServerResourceRecordA -ZoneName "yops.local" -Name "mon" -IPv4Address "10.10.10.30" -CreatePtr

nslookup web.yops.local
nslookup db.yops.local
```

## 7. Configuration Windows client - YOPS-WIN01

Toutes les commandes se lancent dans PowerShell administrateur sur `YOPS-WIN01`.

### 7.1 Renommer et configurer l'IP

```powershell
Rename-Computer -NewName "YOPS-WIN01" -Restart
```

Apres redemarrage :

```powershell
$if = (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).Name
Get-NetIPAddress -InterfaceAlias $if -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false
New-NetIPAddress -InterfaceAlias $if -IPAddress 10.10.10.50 -PrefixLength 24 -DefaultGateway 10.10.10.1
Set-DnsClientServerAddress -InterfaceAlias $if -ServerAddresses 10.10.10.10
ipconfig /all
ping 10.10.10.10
nslookup yops.local
```

### 7.2 Joindre le domaine

```powershell
Add-Computer -DomainName "yops.local" -Credential "YOPS\Administrator" -Restart
```

Entrer le mot de passe administrateur du domaine.

### 7.3 Deplacer l'objet ordinateur dans l'OU Computers

Sur `YOPS-DC01`, PowerShell administrateur :

```powershell
Get-ADComputer YOPS-WIN01 | Move-ADObject -TargetPath "OU=Computers,OU=YOps,DC=yops,DC=local"
```

Sur `YOPS-WIN01`, apres redemarrage :

```powershell
gpupdate /force
gpresult /r
net use
```

Tester avec :

```text
YOPS\alice.martin
YOPS\sarah.diallo
YOPS\hugo.bernard
```

Mot de passe :

```text
YOps-User-2026!
```

Tests de droits :

```powershell
dir \\YOPS-DC01\Public
dir \\YOPS-DC01\Direction
dir \\YOPS-DC01\SOC
```

## 8. Configuration commune des serveurs Linux

Lancer sur chaque serveur Linux : `YOPS-WEB01`, `YOPS-DB01`, `YOPS-MON01`, `YOPS-LNX01`.

Connexion depuis Proxmox :

```bash
ssh yopsadmin@10.10.10.20
ssh yopsadmin@10.10.10.21
ssh yopsadmin@10.10.10.30
ssh yopsadmin@10.10.10.60
```

Commandes communes :

```bash
sudo timedatectl set-timezone Europe/Paris
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y
sudo apt install -y curl wget git vim htop net-tools ufw fail2ban unattended-upgrades ca-certificates gnupg lsb-release dnsutils netcat-openbsd
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 10.10.10.0/24 to any port 22 proto tcp
sudo ufw allow from 100.64.0.0/10 to any port 22 proto tcp
sudo ufw --force enable
```

Ajouter les noms locaux :

```bash
sudo tee -a /etc/hosts >/dev/null <<'EOF'
10.10.10.1 pfsense.yops.local pfsense
10.10.10.10 YOPS-DC01.yops.local YOPS-DC01
10.10.10.20 YOPS-WEB01.yops.local YOPS-WEB01 web.yops.local web
10.10.10.21 YOPS-DB01.yops.local YOPS-DB01 db.yops.local db
10.10.10.30 YOPS-MON01.yops.local YOPS-MON01 mon.yops.local mon
10.10.10.60 YOPS-LNX01.yops.local YOPS-LNX01
EOF
```

Verification :

```bash
hostname
ip -br addr
ip route
ping -c 3 10.10.10.1
ping -c 3 1.1.1.1
getent hosts web.yops.local
```

## 9. Configuration YOPS-WEB01

Sur `YOPS-WEB01` :

```bash
sudo hostnamectl set-hostname YOPS-WEB01
sudo apt install -y nginx php-fpm php-cli php-mbstring php-xml php-curl php-zip php-mysql php-bcmath php-tokenizer unzip composer
sudo systemctl enable nginx
PHP_FPM_SERVICE=$(systemctl list-unit-files 'php*-fpm.service' --no-legend | awk '{print $1}' | head -n 1)
sudo systemctl enable --now "$PHP_FPM_SERVICE"
sudo mkdir -p /var/www/yops/public
```

Page de test temporaire :

```bash
sudo tee /var/www/yops/public/index.php >/dev/null <<'EOF'
<?php
echo "<h1>YOps Web OK</h1>";
echo "<p>Serveur: " . gethostname() . "</p>";
echo "<p>PHP: " . phpversion() . "</p>";
EOF
sudo chown -R www-data:www-data /var/www/yops
```

Trouver le socket PHP-FPM :

```bash
PHP_SOCK=$(find /run/php -name "php*-fpm.sock" | head -n 1)
echo "$PHP_SOCK"
```

Creer le vhost Nginx :

```bash
sudo tee /etc/nginx/sites-available/yops >/dev/null <<EOF
server {
    listen 80;
    server_name yops.local web.yops.local 10.10.10.20;
    root /var/www/yops/public;
    index index.php index.html;

    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:${PHP_SOCK};
    }

    location ~ /\.ht {
        deny all;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/yops /etc/nginx/sites-enabled/yops
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
sudo ufw allow from 10.10.10.0/24 to any port 80 proto tcp
sudo ufw allow from 100.64.0.0/10 to any port 80 proto tcp
sudo ufw status numbered
curl -I http://10.10.10.20
```

## 10. Configuration YOPS-DB01

Sur `YOPS-DB01` :

```bash
sudo hostnamectl set-hostname YOPS-DB01
sudo apt install -y mariadb-server
sudo systemctl enable mariadb
sudo systemctl start mariadb
sudo sed -i 's/^bind-address.*/bind-address = 10.10.10.21/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb
```

Creer la base et les comptes :

```bash
sudo mariadb <<'SQL'
CREATE DATABASE IF NOT EXISTS yops_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'yops_app'@'10.10.10.20' IDENTIFIED BY 'YOps_DB_2026!';
GRANT ALL PRIVILEGES ON yops_app.* TO 'yops_app'@'10.10.10.20';
CREATE USER IF NOT EXISTS 'yops_backup'@'localhost' IDENTIFIED BY 'YOps_Backup_2026!';
GRANT SELECT, SHOW VIEW, TRIGGER, LOCK TABLES, EVENT ON yops_app.* TO 'yops_backup'@'localhost';
FLUSH PRIVILEGES;
SQL
```

Firewall :

```bash
sudo ufw allow from 10.10.10.20 to any port 3306 proto tcp
sudo ufw allow from 10.10.10.30 to any port 3306 proto tcp
sudo ufw status numbered
```

Test local :

```bash
sudo ss -lntp | grep 3306
mariadb -u yops_backup -pYOps_Backup_2026! -e "SHOW DATABASES;"
```

Test depuis `YOPS-WEB01` :

```bash
mysql -h 10.10.10.21 -u yops_app -pYOps_DB_2026! -e "SHOW DATABASES;"
```

Si la commande `mysql` manque sur `YOPS-WEB01` :

```bash
sudo apt install -y default-mysql-client
mysql -h 10.10.10.21 -u yops_app -pYOps_DB_2026! -e "SHOW DATABASES;"
```

## 11. Configuration YOPS-MON01

Sur `YOPS-MON01` :

```bash
sudo hostnamectl set-hostname YOPS-MON01
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo docker run -d \
  --restart=always \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  --name uptime-kuma \
  louislam/uptime-kuma:1
sudo ufw allow from 10.10.10.0/24 to any port 3001 proto tcp
sudo ufw allow from 100.64.0.0/10 to any port 3001 proto tcp
sudo ufw status numbered
curl -I http://10.10.10.30:3001
```

Dans Uptime Kuma :

```text
URL : http://10.10.10.30:3001
```

Creer les sondes :

| Nom | Type | Cible |
|---|---|---|
| pfSense LAN | Ping | 10.10.10.1 |
| YOPS-DC01 | Ping | 10.10.10.10 |
| YOPS-WEB01 HTTP | HTTP(s) | http://10.10.10.20 |
| YOPS-DB01 MariaDB | TCP Port | 10.10.10.21:3306 |
| YOPS-MON01 Kuma | HTTP(s) | http://10.10.10.30:3001 |

## 12. Sauvegardes Linux

### 12.1 Sauvegarde DB sur YOPS-DB01

Sur `YOPS-DB01` :

```bash
sudo mkdir -p /backup/mysql
sudo tee /usr/local/sbin/backup-yops-db.sh >/dev/null <<'EOF'
#!/bin/sh
set -eu
DATE="$(date +%F_%H-%M-%S)"
OUT="/backup/mysql/yops_app_${DATE}.sql.gz"
mysqldump -u yops_backup -p'YOps_Backup_2026!' yops_app | gzip > "$OUT"
find /backup/mysql -type f -name 'yops_app_*.sql.gz' -mtime +14 -delete
EOF
sudo chmod 700 /usr/local/sbin/backup-yops-db.sh
sudo /usr/local/sbin/backup-yops-db.sh
ls -lh /backup/mysql
```

Planifier :

```bash
echo "0 2 * * * root /usr/local/sbin/backup-yops-db.sh" | sudo tee /etc/cron.d/yops-db-backup
sudo systemctl restart cron
```

### 12.2 Sauvegarde web sur YOPS-WEB01

Sur `YOPS-WEB01` :

```bash
sudo mkdir -p /backup/web
sudo tee /usr/local/sbin/backup-yops-web.sh >/dev/null <<'EOF'
#!/bin/sh
set -eu
DATE="$(date +%F_%H-%M-%S)"
tar -czf "/backup/web/yops_web_${DATE}.tar.gz" /var/www/yops
find /backup/web -type f -name 'yops_web_*.tar.gz' -mtime +14 -delete
EOF
sudo chmod 700 /usr/local/sbin/backup-yops-web.sh
sudo /usr/local/sbin/backup-yops-web.sh
ls -lh /backup/web
echo "30 2 * * * root /usr/local/sbin/backup-yops-web.sh" | sudo tee /etc/cron.d/yops-web-backup
sudo systemctl restart cron
```

### 12.3 Sauvegarde Proxmox

Sur Proxmox, creer une sauvegarde ponctuelle des VMs :

```bash
mkdir -p /var/lib/vz/dump
vzdump 110 120 121 130 150 160 --mode snapshot --compress zstd --dumpdir /var/lib/vz/dump
ls -lh /var/lib/vz/dump
```

Planifier dans le GUI :

```text
Datacenter > Backup > Add
Selection : YOPS-DC01, YOPS-WEB01, YOPS-DB01, YOPS-MON01, YOPS-WIN01, YOPS-LNX01
Mode : Snapshot
Compression : ZSTD
Schedule : hebdomadaire
Retention : 2 ou 3 sauvegardes
```

### 12.4 Sauvegarde pfSense

Dans pfSense GUI :

```text
Diagnostics > Backup & Restore > Download configuration as XML
```

Nom conseille :

```text
pfsense-yops-config-YYYY-MM-DD.xml
```

## 13. Validation finale technique

### 13.1 Depuis le PC local

```bash
tailscale status
tailscale ping 100.94.68.82
tailscale ping 100.88.50.5
ssh admin@100.94.68.82
ssh root@100.88.50.5
ping -c 3 10.10.10.1
ping -c 3 10.10.10.10
ping -c 3 10.10.10.20
curl -I http://10.10.10.20
curl -I http://10.10.10.30:3001
nc -vz 10.10.10.21 3306
```

### 13.2 Depuis YOPS-DC01

```powershell
dcdiag
repadmin /replsummary
Get-ADUser -Filter * -SearchBase "OU=Users,OU=YOps,DC=yops,DC=local"
Get-ADGroup -Filter * -SearchBase "OU=Groups,OU=YOps,DC=yops,DC=local"
nslookup web.yops.local
```

Sur un seul controleur de domaine, `repadmin /replsummary` peut afficher peu d'informations. Ce n'est pas bloquant.

### 13.3 Depuis YOPS-WIN01

```powershell
whoami
ipconfig /all
nslookup yops.local
gpupdate /force
gpresult /r
net use
dir \\YOPS-DC01\Public
```

### 13.4 Depuis YOPS-WEB01

```bash
curl -I http://10.10.10.20
mysql -h 10.10.10.21 -u yops_app -pYOps_DB_2026! -e "SHOW DATABASES;"
```

### 13.5 Depuis YOPS-MON01

```bash
sudo docker ps
curl -I http://10.10.10.30:3001
nc -vz 10.10.10.21 3306
```

## 14. Captures a faire pour le rapport

Faire des captures de :

- Proxmox avec les VMs YOps ;
- pfSense interfaces ;
- pfSense regles Tailscale ;
- Tailscale status ;
- AD Users and Computers ;
- Group Policy Management ;
- partages et droits NTFS ;
- poste Windows joint au domaine ;
- page `YOps Web OK` ;
- Uptime Kuma avec les sondes vertes ;
- sauvegardes Proxmox ou fichiers backup.

## 15. Ordre exact a suivre

1. Verifier Tailscale PC, pfSense et Proxmox.
2. Verifier pfSense.
3. Verifier Proxmox.
4. Creer `YOPS-DC01`.
5. Installer Windows Server GUI.
6. Creer `YOPS-WIN01`.
7. Installer Windows client sans le joindre au domaine pour l'instant.
8. Creer template Debian.
9. Creer `YOPS-WEB01`, `YOPS-DB01`, `YOPS-MON01`, `YOPS-LNX01`.
10. Configurer `YOPS-DC01` avec AD/DNS/fichiers/GPO.
11. Joindre `YOPS-WIN01` au domaine.
12. Appliquer la configuration commune Linux.
13. Configurer web.
14. Configurer DB.
15. Configurer supervision.
16. Configurer sauvegardes.
17. Faire validation finale.
18. Faire captures.

## 16. Depannage rapide

### Une VM Linux ne ping pas Internet

```bash
ip route
ping -c 3 10.10.10.1
ping -c 3 192.168.1.1
ping -c 3 1.1.1.1
```

Verifier que la VM est sur `vmbr1` et que pfSense NAT le LAN vers WAN.

### Un client Windows ne trouve pas le domaine

```powershell
ipconfig /all
nslookup yops.local
ping 10.10.10.10
```

Le DNS du client doit etre `10.10.10.10`, pas `10.10.10.1`.

### SSH Tailscale vers pfSense ne marche pas

Sur pfSense :

```sh
tailscale status
service tailscaled restart
sockstat -4 -l | grep ssh
```

Verifier la regle firewall sur OPT1/Tailscale.

### Nginx ne demarre pas

Sur `YOPS-WEB01` :

```bash
sudo nginx -t
sudo journalctl -xeu nginx --no-pager
find /run/php -name "php*-fpm.sock"
```

### MariaDB refuse la connexion depuis le web

Sur `YOPS-DB01` :

```bash
sudo ss -lntp | grep 3306
sudo ufw status numbered
sudo mariadb -e "SELECT user,host FROM mysql.user;"
```

Sur `YOPS-WEB01` :

```bash
nc -vz 10.10.10.21 3306
mysql -h 10.10.10.21 -u yops_app -pYOps_DB_2026! -e "SHOW DATABASES;"
```
