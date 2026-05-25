# Cloud hybride et sauvegardes

Le projet YOps est heberge localement sur Proxmox.  
Pour repondre au besoin cloud/hybride, l'idee n'est pas de tout migrer dans Azure ou AWS, mais d'ajouter une strategie de secours externe.

## Choix retenu

Le modele choisi est un modele hybride simple :

- les services tournent localement sur Proxmox ;
- les sauvegardes principales sont faites localement ;
- une copie chiffree peut etre envoyee vers un stockage cloud ;
- l'administration reste accessible via Tailscale.

Ce choix est realiste pour une petite entreprise : on garde la maitrise locale, mais on evite de tout perdre si l'hyperviseur ou le disque local tombe.

## Ce qui est deja fait

Une sauvegarde Proxmox des VMs importantes a ete realisee dans :

```text
/var/lib/vz/dump/yops
```

VMs sauvegardees :

- `YOPS-DC01`
- `YOPS-WEB01`
- `YOPS-DB01`
- `YOPS-MON01`
- `YOPS-WIN01`

## Strategie cible

| Element | Methode | Frequence | Conservation |
|---|---|---:|---:|
| VMs Proxmox | Backup Proxmox | quotidienne ou hebdo | 2 a 4 versions |
| Base MariaDB | Dump SQL | quotidienne | 7 jours |
| Portail web | Archive `/var/www/yops` | quotidienne | 7 jours |
| pfSense | Export XML | apres changement | 3 versions |
| Documentation | GitHub | a chaque modification | historique Git |

## Copie cloud proposee

Pour la partie cloud, je proposerais une copie chiffree vers :

- un bucket S3 compatible ;
- Azure Blob Storage ;
- ou un stockage type Backblaze B2.

Exemple de principe :

```text
Backup Proxmox local -> chiffrement -> copie cloud -> verification periodique
```

Je ne mets pas cette partie en production dans le lab pour eviter d'ajouter des comptes cloud et des secrets dans le projet. Par contre, la strategie est documentee et peut etre appliquee facilement.

## RPO et RTO

Pour une petite structure comme YOps, un objectif raisonnable serait :

| Donnee | RPO | RTO |
|---|---:|---:|
| Active Directory | 24 h | 2 a 4 h |
| Portail intranet | 24 h | 1 a 2 h |
| Base applicative | 24 h | 2 h |
| Documentation | quelques minutes | immediat |

RPO : perte de donnees maximale acceptee.  
RTO : temps estime pour remettre le service en ligne.

## Test de restauration

Une sauvegarde n'a de valeur que si elle peut etre restauree.

Tests a prevoir :

- restaurer une VM dans Proxmox sur un ID de test ;
- verifier que le serveur demarre ;
- restaurer un dump MariaDB dans une base temporaire ;
- restaurer un fichier depuis un partage ;
- verifier que la documentation GitHub est recuperable.

## Pourquoi cette approche est suffisante pour le projet

Le sujet demande de proposer une solution cloud ou hybride.  
Dans mon cas, je choisis une approche prudente : l'infra reste locale pour la demonstration, et le cloud sert surtout a proteger les sauvegardes.

C'est plus simple, moins risqué, et beaucoup plus facile a expliquer.

