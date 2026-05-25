# Playbook Linux - Web, base de donnees, supervision

## Objectif

Mettre en place les serveurs Linux de YOps :

- `YOPS-WEB01` pour l'application Laravel ;
- `YOPS-DB01` pour la base de donnees ;
- `YOPS-MON01` pour supervision et sauvegardes.

Pour les commandes exactes d'installation, configuration, firewall, sauvegardes et validation, suivre :

```text
docs/08_RUNBOOK_EXECUTION_INFRA_A_Z.md
```

Distribution recommandee :

```text
Debian 12 ou Ubuntu Server LTS
```

## Configuration reseau

| Serveur | IP | Gateway | DNS |
|---|---|---|---|
| YOPS-WEB01 | 10.10.10.20/24 | 10.10.10.1 | 10.10.10.10 |
| YOPS-DB01 | 10.10.10.21/24 | 10.10.10.1 | 10.10.10.10 |
| YOPS-MON01 | 10.10.10.30/24 | 10.10.10.1 | 10.10.10.10 |

Commandes de base apres installation :

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y curl wget git vim htop net-tools ufw ca-certificates
```

Configurer le hostname :

```bash
sudo hostnamectl set-hostname YOPS-WEB01
```

Adapter selon le serveur.

## YOPS-WEB01 - Nginx, PHP, Laravel

Installer les paquets :

```bash
sudo apt install -y nginx php-fpm php-cli php-mbstring php-xml php-curl php-zip php-mysql php-bcmath php-tokenizer unzip composer
```

Activer Nginx :

```bash
sudo systemctl enable nginx
sudo systemctl status nginx
```

Dossier application :

```bash
sudo mkdir -p /var/www/yops
sudo chown -R www-data:www-data /var/www/yops
```

Configuration Nginx type :

```nginx
server {
    listen 80;
    server_name yops.local 10.10.10.20;
    root /var/www/yops/public;

    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php-fpm.sock;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

Adapter `php-fpm.sock` selon la version PHP.

Tests :

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I http://10.10.10.20
```

## YOPS-DB01 - MariaDB

Installer MariaDB :

```bash
sudo apt install -y mariadb-server
sudo systemctl enable mariadb
sudo mysql_secure_installation
```

Creer la base :

```sql
CREATE DATABASE yops_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'yops_app'@'10.10.10.20' IDENTIFIED BY 'MotDePasseFortAChanger!';
GRANT ALL PRIVILEGES ON yops_app.* TO 'yops_app'@'10.10.10.20';
FLUSH PRIVILEGES;
```

Autoriser MariaDB a ecouter sur le LAN :

```bash
sudo sed -i 's/^bind-address.*/bind-address = 10.10.10.21/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb
```

Firewall :

```bash
sudo ufw allow from 10.10.10.20 to any port 3306 proto tcp
sudo ufw enable
```

## YOPS-MON01 - Supervision

Option simple recommandee : Uptime Kuma.

Installation via Docker :

```bash
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

Acces :

```text
http://10.10.10.30:3001
```

Sondes a creer :

| Service | Type | Cible |
|---|---|---|
| pfSense LAN | Ping | 10.10.10.1 |
| AD/DNS | Ping | 10.10.10.10 |
| Web YOps | HTTP | http://10.10.10.20 |
| DB | Port TCP | 10.10.10.21:3306 |
| Supervision | HTTP | http://10.10.10.30:3001 |

## Sauvegardes Linux

Sauvegarde DB quotidienne depuis `YOPS-DB01` :

```bash
sudo mkdir -p /backup/mysql
sudo crontab -e
```

Entrer :

```cron
0 2 * * * mysqldump yops_app | gzip > /backup/mysql/yops_app_$(date +\%F).sql.gz
```

Sauvegarde application depuis `YOPS-WEB01` :

```bash
sudo tar -czf /backup/yops_app_files_$(date +%F).tar.gz /var/www/yops
```

## Durcissement minimal

Sur chaque serveur Linux :

```bash
sudo apt install -y unattended-upgrades fail2ban
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 10.10.10.0/24 to any port 22 proto tcp
sudo ufw allow from 100.64.0.0/10 to any port 22 proto tcp
sudo ufw enable
```

Adapter les ports selon le role :

- web : autoriser 80/443 ;
- DB : autoriser 3306 seulement depuis `YOPS-WEB01` ;
- supervision : autoriser 3001 depuis LAN/Tailscale.

## Tests de validation

Depuis le PC admin via Tailscale :

```bash
ping 10.10.10.20
curl -I http://10.10.10.20
ping 10.10.10.21
nc -vz 10.10.10.21 3306
curl -I http://10.10.10.30:3001
```
