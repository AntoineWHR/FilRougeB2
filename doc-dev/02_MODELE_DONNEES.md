# Modele de donnees - YOps Portal

## Tables principales

```text
users
roles
clients
audits
vulnerabilities
remediation_tickets
reports
comments
```

## Relations

```text
Un client possede plusieurs audits.
Un audit possede plusieurs vulnerabilites.
Une vulnerabilite peut avoir un ticket de remediation.
Un audit peut avoir un rapport.
Un utilisateur peut etre responsable d'un audit ou d'un ticket.
Un commentaire appartient a une vulnerabilite ou a un ticket.
```

## Structure simplifiee

### users

| Champ | Type | Role |
|---|---|---|
| id | integer | Identifiant |
| name | string | Nom |
| email | string | Connexion |
| password | string | Mot de passe hashe |
| role_id | foreign key | Role |

### roles

| Champ | Type | Role |
|---|---|---|
| id | integer | Identifiant |
| name | string | admin, analyst, sales, client |

### clients

| Champ | Type |
|---|---|
| id | integer |
| name | string |
| sector | string |
| contact_name | string |
| email | string |
| phone | string |
| status | string |

### audits

| Champ | Type |
|---|---|
| id | integer |
| client_id | foreign key |
| title | string |
| audit_type | string |
| starts_at | date |
| ends_at | date |
| status | string |
| owner_id | foreign key |

### vulnerabilities

| Champ | Type |
|---|---|
| id | integer |
| audit_id | foreign key |
| title | string |
| description | text |
| severity | string |
| cvss_score | decimal |
| asset | string |
| evidence | text |
| recommendation | text |
| status | string |

### remediation_tickets

| Champ | Type |
|---|---|
| id | integer |
| vulnerability_id | foreign key |
| assignee_id | foreign key |
| priority | string |
| due_date | date |
| status | string |
| comment | text |

### reports

| Champ | Type |
|---|---|
| id | integer |
| audit_id | foreign key |
| title | string |
| executive_summary | text |
| generated_at | datetime |

## Statuts proposes

### Audit

```text
planifie
en_cours
termine
annule
```

### Vulnerabilite

```text
ouverte
en_cours
corrigee
acceptee
```

### Ticket

```text
nouveau
en_cours
bloque
termine
```
