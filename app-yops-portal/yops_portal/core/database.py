from __future__ import annotations

import sqlite3
from pathlib import Path

from yops_portal.core.security import hash_password


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
DATABASE_PATH = DATA_DIR / "yops_portal.sqlite"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as db:
        create_schema(db)
        seed_database(db)
        seed_notes_if_empty(db)
        seed_requests_if_empty(db)


def seed_requests_if_empty(db: sqlite3.Connection) -> None:
    existing = db.execute("SELECT COUNT(*) AS count FROM audit_requests").fetchone()["count"]
    if existing:
        return
    client_ids = {row["name"]: row["id"] for row in db.execute("SELECT id, name FROM clients")}
    rows = db.execute("SELECT id, client_id FROM users WHERE client_id IS NOT NULL").fetchall()
    client_user = {row["client_id"]: row["id"] for row in rows}
    if not client_user:
        return
    seeds = []
    if "Alphatech" in client_ids and client_ids["Alphatech"] in client_user:
        seeds.append((
            client_ids["Alphatech"], client_user[client_ids["Alphatech"]],
            "web", "Tester l'API mobile en pré-production : auth, paiements, gestion des sessions.",
            "Compte de test fourni, fenêtre de tir 22h-06h, pas de DDoS, pas d'exfiltration de données réelles.",
            "high", "2026-06-15"
        ))
        seeds.append((
            client_ids["Alphatech"], client_user[client_ids["Alphatech"]],
            "cloud", "Revue configuration AWS sur le tenant production (IAM, S3, secrets).",
            "Lecture seule sur les comptes IAM, exclusion des données client.",
            "normal", "2026-07-01"
        ))
    if seeds:
        db.executemany(
            """
            INSERT INTO audit_requests (client_id, requested_by, audit_type, scope, rules, urgency, target_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            seeds,
        )


def seed_notes_if_empty(db: sqlite3.Connection) -> None:
    existing = db.execute("SELECT COUNT(*) AS count FROM client_notes").fetchone()["count"]
    if existing:
        return
    client_ids = {row["name"]: row["id"] for row in db.execute("SELECT id, name FROM clients")}
    user_ids = {row["email"]: row["id"] for row in db.execute("SELECT id, email FROM users")}
    sarah = user_ids.get("sarah.diallo@yops.local")
    hugo = user_ids.get("hugo.bernard@yops.local")
    if not (sarah and hugo):
        return
    seeds = [
        ("Alphatech", sarah, "alert", "MFA toujours pas activé sur les comptes admin — relance prévue cette semaine.", "2026-05-19 09:14:00"),
        ("Alphatech", hugo, "contact", "Appel avec Mila Ferrand : extension du périmètre à l'API mobile validée.", "2026-05-17 14:32:00"),
        ("Alphatech", sarah, "note", "Préparer la démo de remédiation SQLi pour le prochain comité.", "2026-05-15 10:05:00"),
        ("MedSecure", sarah, "meeting", "Réunion PRA effectuée. RTO fixé à 4h, RPO à 1h sur les bases critiques.", "2026-05-12 16:00:00"),
        ("MedSecure", sarah, "alert", "TLS 1.0 toujours actif sur vpn-gateway, à corriger avant fin de sprint.", "2026-05-14 08:42:00"),
        ("RetailOne", hugo, "contact", "Lina Chau confirme la signature du contrat managé SOC.", "2026-05-03 11:20:00"),
        ("CityCloud", sarah, "alert", "Compte root cloud encore utilisé en quotidien — escalade en cours.", "2026-05-17 18:55:00"),
        ("CityCloud", hugo, "note", "Demande d'extension SOC vers leur tenant secondaire.", "2026-05-10 09:00:00"),
    ]
    db.executemany(
        "INSERT INTO client_notes (client_id, author_id, kind, body, created_at) VALUES (?, ?, ?, ?, ?)",
        [(client_ids[name], uid, kind, body, ts) for name, uid, kind, body, ts in seeds if name in client_ids],
    )


def create_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sector TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            client_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            audit_type TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            ends_at TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (owner_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL CHECK(severity IN ('low', 'medium', 'high', 'critical')),
            cvss_score REAL NOT NULL,
            asset TEXT NOT NULL,
            evidence TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            status TEXT NOT NULL,
            discovered_at TEXT NOT NULL,
            FOREIGN KEY (audit_id) REFERENCES audits(id)
        );

        CREATE TABLE IF NOT EXISTS remediation_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vulnerability_id INTEGER NOT NULL,
            assignee_id INTEGER NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id),
            FOREIGN KEY (assignee_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            executive_summary TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            FOREIGN KEY (audit_id) REFERENCES audits(id)
        );

        CREATE TABLE IF NOT EXISTS client_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            body TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'note' CHECK(kind IN ('note', 'contact', 'alert', 'meeting')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            requested_by INTEGER NOT NULL,
            audit_type TEXT NOT NULL,
            scope TEXT NOT NULL,
            rules TEXT NOT NULL DEFAULT '',
            urgency TEXT NOT NULL DEFAULT 'normal' CHECK(urgency IN ('low', 'normal', 'high', 'urgent')),
            target_date TEXT,
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
            admin_response TEXT NOT NULL DEFAULT '',
            responded_by INTEGER,
            responded_at TEXT,
            audit_id INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (requested_by) REFERENCES users(id),
            FOREIGN KEY (responded_by) REFERENCES users(id),
            FOREIGN KEY (audit_id) REFERENCES audits(id)
        );

        CREATE INDEX IF NOT EXISTS idx_vuln_severity ON vulnerabilities(severity);
        CREATE INDEX IF NOT EXISTS idx_vuln_status ON vulnerabilities(status);
        CREATE INDEX IF NOT EXISTS idx_tickets_due_date ON remediation_tickets(due_date);
        CREATE INDEX IF NOT EXISTS idx_notes_client ON client_notes(client_id);
        CREATE INDEX IF NOT EXISTS idx_notes_created ON client_notes(created_at);
        CREATE INDEX IF NOT EXISTS idx_requests_status ON audit_requests(status);
        CREATE INDEX IF NOT EXISTS idx_requests_client ON audit_requests(client_id);

        CREATE TABLE IF NOT EXISTS report_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            audit_id INTEGER,
            vulnerability_id INTEGER,
            sent_by INTEGER NOT NULL,
            kind TEXT NOT NULL DEFAULT 'remediation',
            verdict TEXT,
            admin_message TEXT NOT NULL DEFAULT '',
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            vuln_count INTEGER NOT NULL DEFAULT 0,
            critical_count INTEGER NOT NULL DEFAULT 0,
            delivered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (audit_id) REFERENCES audits(id),
            FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id),
            FOREIGN KEY (sent_by) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_deliveries_client ON report_deliveries(client_id);
        """
    )
    _ensure_column(db, "report_deliveries", "audit_id", "INTEGER")
    _ensure_column(db, "report_deliveries", "vulnerability_id", "INTEGER")
    _ensure_column(db, "report_deliveries", "kind", "TEXT NOT NULL DEFAULT 'remediation'")
    _ensure_column(db, "report_deliveries", "verdict", "TEXT")
    _ensure_column(db, "report_deliveries", "admin_message", "TEXT NOT NULL DEFAULT ''")


def _ensure_column(db: sqlite3.Connection, table: str, column: str, declaration: str) -> None:
    existing = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def seed_database(db: sqlite3.Connection) -> None:
    existing = db.execute("SELECT COUNT(*) AS count FROM roles").fetchone()["count"]
    if existing:
        return

    roles = [
        ("admin", "Administrateur"),
        ("analyst", "Analyste SOC"),
        ("sales", "Commercial"),
        ("client", "Client"),
    ]
    db.executemany("INSERT INTO roles (name, label) VALUES (?, ?)", roles)

    clients = [
        ("Alphatech", "SaaS B2B", "Mila Ferrand", "security@alphatech.local", "01 44 20 10 11", "active"),
        ("MedSecure", "Sante", "Noe Perrin", "it@medsecure.local", "01 44 20 10 12", "active"),
        ("RetailOne", "E-commerce", "Lina Chau", "secops@retailone.local", "01 44 20 10 13", "active"),
        ("CityCloud", "Cloud public", "Hugo Mael", "cloudsec@citycloud.local", "01 44 20 10 14", "active"),
    ]
    db.executemany(
        """
        INSERT INTO clients (name, sector, contact_name, email, phone, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        clients,
    )

    role_ids = {row["name"]: row["id"] for row in db.execute("SELECT id, name FROM roles")}
    client_ids = {row["name"]: row["id"] for row in db.execute("SELECT id, name FROM clients")}

    users = [
        ("YOps Admin", "admin@yops.local", "admin", None, "YOps-Admin-2026!"),
        ("Sarah Diallo", "sarah.diallo@yops.local", "analyst", None, "YOps-User-2026!"),
        ("Hugo Bernard", "hugo.bernard@yops.local", "sales", None, "YOps-User-2026!"),
        ("Client Alphatech", "client@alphatech.local", "client", client_ids["Alphatech"], "YOps-Client-2026!"),
    ]
    db.executemany(
        """
        INSERT INTO users (name, email, role_id, client_id, password_hash)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(name, email, role_ids[role], client_id, hash_password(password)) for name, email, role, client_id, password in users],
    )

    user_ids = {row["email"]: row["id"] for row in db.execute("SELECT id, email FROM users")}
    audits = [
        (client_ids["Alphatech"], user_ids["sarah.diallo@yops.local"], "Audit web portail client", "web", "2026-05-03", "2026-05-17", "en_cours"),
        (client_ids["Alphatech"], user_ids["sarah.diallo@yops.local"], "Revue Active Directory", "ad", "2026-04-11", "2026-04-22", "termine"),
        (client_ids["MedSecure"], user_ids["sarah.diallo@yops.local"], "Audit infrastructure interne", "infra", "2026-05-08", "2026-05-28", "en_cours"),
        (client_ids["RetailOne"], user_ids["sarah.diallo@yops.local"], "Audit API paiement", "web", "2026-04-20", "2026-05-02", "termine"),
        (client_ids["CityCloud"], user_ids["sarah.diallo@yops.local"], "Audit configuration cloud", "cloud", "2026-05-14", "2026-06-01", "planifie"),
        (client_ids["MedSecure"], user_ids["sarah.diallo@yops.local"], "Revue sauvegardes et PRA", "infra", "2026-03-20", "2026-04-04", "termine"),
    ]
    db.executemany(
        """
        INSERT INTO audits (client_id, owner_id, title, audit_type, starts_at, ends_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        audits,
    )

    audit_ids = [row["id"] for row in db.execute("SELECT id FROM audits ORDER BY id")]
    vulnerabilities = [
        (audit_ids[0], "MFA absent sur compte administrateur", "Compte admin exposé sans second facteur.", "critical", 9.1, "portal.alphatech.local", "Capture login + politique MFA absente", "Activer MFA obligatoire sur comptes privilegies.", "ouverte", "2026-05-05"),
        (audit_ids[0], "Injection SQL sur endpoint de recherche", "Parametre q injectable dans la recherche.", "critical", 9.4, "/api/search", "Payload union-based en environnement de test", "Utiliser requetes preparees et validation stricte.", "en_cours", "2026-05-06"),
        (audit_ids[0], "Headers de securite incomplets", "CSP et HSTS absents.", "medium", 5.4, "portal.alphatech.local", "Analyse HTTP response", "Ajouter CSP, HSTS et X-Content-Type-Options.", "ouverte", "2026-05-07"),
        (audit_ids[1], "Partage SMB accessible a tous", "ACL trop large sur un partage interne.", "high", 8.0, "filesrv01", "Enum SMB", "Restreindre par groupes metiers.", "corrigee", "2026-04-12"),
        (audit_ids[1], "Mot de passe faible sur compte de service", "Compte svc_backup avec mot de passe predictible.", "high", 7.8, "AD", "Audit politique comptes", "Rotation du secret et coffre-fort.", "corrigee", "2026-04-13"),
        (audit_ids[2], "Version Nginx obsolete", "Nginx expose une version ancienne.", "medium", 5.9, "reverse-proxy", "Banniere serveur", "Mettre a jour le paquet et masquer la version.", "ouverte", "2026-05-10"),
        (audit_ids[2], "SSH autorise par mot de passe", "PasswordAuthentication active sur serveurs critiques.", "high", 7.1, "linux-prod", "Audit sshd_config", "Imposer cles SSH et MFA admin.", "en_cours", "2026-05-11"),
        (audit_ids[2], "Sauvegarde non testee", "Aucun test de restauration recent.", "medium", 6.0, "backup-nas", "Entretien + absence logs restore", "Planifier tests trimestriels.", "ouverte", "2026-05-12"),
        (audit_ids[3], "Absence de rate limiting", "Endpoint login API non limite.", "high", 7.5, "/api/auth/login", "Bruteforce controle", "Ajouter limitation par IP et compte.", "corrigee", "2026-04-21"),
        (audit_ids[3], "IDOR sur facture client", "Changement ID permet de lire une autre facture.", "critical", 9.0, "/api/invoices/{id}", "Deux comptes de test", "Verifier l'appartenance objet/utilisateur.", "corrigee", "2026-04-22"),
        (audit_ids[4], "Bucket public non documente", "Objet cloud lisible publiquement.", "high", 8.2, "citycloud-assets", "Listing public", "Passer en private et ajouter revue IAM.", "ouverte", "2026-05-15"),
        (audit_ids[4], "Cle API longue duree", "Cle sans rotation depuis plus d'un an.", "medium", 6.1, "cloud-api-key", "Inventaire IAM", "Rotation + duree de vie limitee.", "ouverte", "2026-05-16"),
        (audit_ids[5], "PRA non formalise", "RTO/RPO non valides avec les metiers.", "medium", 5.8, "PRA", "Documentation incomplete", "Formaliser RTO/RPO et exercice annuel.", "corrigee", "2026-03-21"),
        (audit_ids[5], "Sauvegardes non chiffrees", "Export de sauvegarde sans chiffrement.", "high", 7.4, "backup repository", "Controle configuration", "Chiffrer au repos et en transit.", "corrigee", "2026-03-22"),
        (audit_ids[0], "Cookie session sans SameSite strict", "Attribut SameSite absent.", "low", 3.2, "portal.alphatech.local", "Inspection cookie", "Configurer SameSite=Lax ou Strict.", "ouverte", "2026-05-08"),
        (audit_ids[2], "Journalisation insuffisante", "Logs auth conserves seulement 24h.", "medium", 5.1, "siem", "Controle retention", "Augmenter retention et centraliser.", "ouverte", "2026-05-13"),
        (audit_ids[3], "CORS trop permissif", "Access-Control-Allow-Origin wildcard.", "medium", 5.6, "/api", "Headers API", "Limiter aux origines de confiance.", "corrigee", "2026-04-24"),
        (audit_ids[4], "Compte root cloud actif", "Compte root utilise recemment.", "critical", 9.2, "cloud tenant", "Audit logs cloud", "Desactiver usage quotidien et activer MFA.", "ouverte", "2026-05-17"),
        (audit_ids[1], "GPO mot de passe insuffisante", "Longueur minimale trop faible.", "medium", 5.5, "AD", "gpresult", "Passer a 12+ caracteres et historique.", "corrigee", "2026-04-14"),
        (audit_ids[2], "TLS 1.0 encore actif", "Ancien protocole accepte.", "high", 7.0, "vpn-gateway", "Scan TLS", "Desactiver TLS 1.0/1.1.", "ouverte", "2026-05-14"),
    ]
    db.executemany(
        """
        INSERT INTO vulnerabilities
        (audit_id, title, description, severity, cvss_score, asset, evidence, recommendation, status, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        vulnerabilities,
    )

    vulnerability_ids = [row["id"] for row in db.execute("SELECT id FROM vulnerabilities ORDER BY id LIMIT 10")]
    tickets = [
        (vulnerability_ids[0], user_ids["sarah.diallo@yops.local"], "P1", "2026-05-29", "ouvert", "MFA prioritaire comptes privilegies."),
        (vulnerability_ids[1], user_ids["sarah.diallo@yops.local"], "P1", "2026-05-30", "en_cours", "Correctif prepare par l'equipe dev."),
        (vulnerability_ids[2], user_ids["hugo.bernard@yops.local"], "P3", "2026-06-12", "ouvert", "A planifier avec l'hebergeur."),
        (vulnerability_ids[3], user_ids["sarah.diallo@yops.local"], "P2", "2026-04-25", "termine", "ACL corrigees."),
        (vulnerability_ids[4], user_ids["sarah.diallo@yops.local"], "P2", "2026-04-26", "termine", "Mot de passe remplace."),
        (vulnerability_ids[5], user_ids["sarah.diallo@yops.local"], "P3", "2026-06-05", "ouvert", "Maintenance a prevoir."),
        (vulnerability_ids[6], user_ids["sarah.diallo@yops.local"], "P2", "2026-06-01", "en_cours", "Migration cles SSH en cours."),
        (vulnerability_ids[7], user_ids["hugo.bernard@yops.local"], "P3", "2026-06-20", "ouvert", "Plan de test a valider."),
        (vulnerability_ids[8], user_ids["sarah.diallo@yops.local"], "P2", "2026-05-01", "termine", "Rate limit ajoute."),
        (vulnerability_ids[9], user_ids["sarah.diallo@yops.local"], "P1", "2026-04-28", "termine", "Controle ownership ajoute."),
    ]
    db.executemany(
        """
        INSERT INTO remediation_tickets
        (vulnerability_id, assignee_id, priority, due_date, status, comment)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        tickets,
    )

    reports = [
        (audit_ids[0], "Synthese executif - Alphatech Web", "Risque eleve lie a deux vulnerabilites critiques sur le portail client.", "2026-05-18"),
        (audit_ids[1], "Rapport final - Revue AD Alphatech", "Les droits fichiers et comptes de service ont ete corriges apres revue.", "2026-04-23"),
        (audit_ids[3], "Rapport final - API RetailOne", "Les failles IDOR et rate limiting ont ete corrigees et validees.", "2026-05-03"),
    ]
    db.executemany(
        "INSERT INTO reports (audit_id, title, executive_summary, generated_at) VALUES (?, ?, ?, ?)",
        reports,
    )

    notes = [
        (client_ids["Alphatech"], user_ids["sarah.diallo@yops.local"], "alert", "MFA toujours pas activé sur les comptes admin — relance prévue cette semaine.", "2026-05-19 09:14:00"),
        (client_ids["Alphatech"], user_ids["hugo.bernard@yops.local"], "contact", "Appel avec Mila Ferrand : extension du périmètre à l'API mobile validée.", "2026-05-17 14:32:00"),
        (client_ids["Alphatech"], user_ids["sarah.diallo@yops.local"], "note", "Préparer la démo de remédiation SQLi pour le prochain comité.", "2026-05-15 10:05:00"),
        (client_ids["MedSecure"], user_ids["sarah.diallo@yops.local"], "meeting", "Réunion PRA effectuée. RTO fixé à 4h, RPO à 1h sur les bases critiques.", "2026-05-12 16:00:00"),
        (client_ids["MedSecure"], user_ids["sarah.diallo@yops.local"], "alert", "TLS 1.0 toujours actif sur vpn-gateway, à corriger avant fin de sprint.", "2026-05-14 08:42:00"),
        (client_ids["RetailOne"], user_ids["hugo.bernard@yops.local"], "contact", "Lina Chau confirme la signature du contrat managé SOC.", "2026-05-03 11:20:00"),
        (client_ids["CityCloud"], user_ids["sarah.diallo@yops.local"], "alert", "Compte root cloud encore utilisé en quotidien — escalade en cours.", "2026-05-17 18:55:00"),
        (client_ids["CityCloud"], user_ids["hugo.bernard@yops.local"], "note", "Demande d'extension SOC vers leur tenant secondaire.", "2026-05-10 09:00:00"),
    ]
    db.executemany(
        """
        INSERT INTO client_notes (client_id, author_id, kind, body, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        notes,
    )

