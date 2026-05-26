from __future__ import annotations

import csv
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT_DIR / "data" / "yops_portal.sqlite"
REPORT_DIR = ROOT_DIR / "storage" / "reports"


def fetch_all(db: sqlite3.Connection, query: str, params: tuple = ()) -> list[sqlite3.Row]:
    return list(db.execute(query, params))


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def remediation_score(open_critical: int, overdue_tickets: int, remediation_rate: float) -> str:
    if open_critical >= 2 or overdue_tickets >= 3:
        return "risque eleve"
    if remediation_rate < 50:
        return "risque modere"
    return "risque maitrise"


def main() -> None:
    if not DATABASE_PATH.exists():
        raise SystemExit("Base absente. Lance d'abord: python3 run.py")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row

    severity = rows_to_dicts(
        fetch_all(
            db,
            """
            SELECT severity, COUNT(*) AS total, ROUND(AVG(cvss_score), 2) AS cvss_moyen
            FROM vulnerabilities
            GROUP BY severity
            ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
            """,
        )
    )
    client_risk = rows_to_dicts(
        fetch_all(
            db,
            """
            SELECT clients.name AS client,
                   COUNT(vulnerabilities.id) AS total_vulnerabilites,
                   SUM(CASE WHEN vulnerabilities.severity = 'critical' THEN 1 ELSE 0 END) AS critiques,
                   SUM(CASE WHEN vulnerabilities.severity = 'high' THEN 1 ELSE 0 END) AS hautes,
                   ROUND(AVG(vulnerabilities.cvss_score), 2) AS cvss_moyen
            FROM clients
            LEFT JOIN audits ON audits.client_id = clients.id
            LEFT JOIN vulnerabilities ON vulnerabilities.audit_id = audits.id
            GROUP BY clients.id
            ORDER BY critiques DESC, hautes DESC, cvss_moyen DESC
            """,
        )
    )
    overdue = rows_to_dicts(
        fetch_all(
            db,
            """
            SELECT clients.name AS client,
                   vulnerabilities.title AS vulnerabilite,
                   remediation_tickets.priority,
                   remediation_tickets.due_date,
                   remediation_tickets.status
            FROM remediation_tickets
            JOIN vulnerabilities ON vulnerabilities.id = remediation_tickets.vulnerability_id
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            WHERE remediation_tickets.due_date < date('now')
              AND remediation_tickets.status != 'termine'
            ORDER BY remediation_tickets.due_date ASC
            """,
        )
    )
    monthly_trend = rows_to_dicts(
        fetch_all(
            db,
            """
            SELECT substr(discovered_at, 1, 7) AS mois,
                   COUNT(*) AS total,
                   ROUND(AVG(cvss_score), 2) AS cvss_moyen
            FROM vulnerabilities
            GROUP BY substr(discovered_at, 1, 7)
            ORDER BY mois
            """,
        )
    )
    top_assets = rows_to_dicts(
        fetch_all(
            db,
            """
            SELECT asset, COUNT(*) AS total, MAX(cvss_score) AS cvss_max
            FROM vulnerabilities
            GROUP BY asset
            ORDER BY total DESC, cvss_max DESC
            LIMIT 10
            """,
        )
    )

    total_tickets = db.execute("SELECT COUNT(*) AS total FROM remediation_tickets").fetchone()["total"]
    closed_tickets = db.execute("SELECT COUNT(*) AS total FROM remediation_tickets WHERE status = 'termine'").fetchone()["total"]
    open_critical = db.execute(
        "SELECT COUNT(*) AS total FROM vulnerabilities WHERE severity = 'critical' AND status != 'corrigee'"
    ).fetchone()["total"]
    remediation_rate = round((closed_tickets / total_tickets) * 100, 1) if total_tickets else 0

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "database": str(DATABASE_PATH),
        "clients": db.execute("SELECT COUNT(*) AS total FROM clients").fetchone()["total"],
        "audits": db.execute("SELECT COUNT(*) AS total FROM audits").fetchone()["total"],
        "vulnerabilities": db.execute("SELECT COUNT(*) AS total FROM vulnerabilities").fetchone()["total"],
        "open_critical": open_critical,
        "overdue_tickets": len(overdue),
        "remediation_rate": remediation_rate,
        "reading": remediation_score(open_critical, len(overdue), remediation_rate),
    }

    (REPORT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(REPORT_DIR / "severity.csv", severity)
    write_csv(REPORT_DIR / "client_risk.csv", client_risk)
    write_csv(REPORT_DIR / "overdue_tickets.csv", overdue)
    write_csv(REPORT_DIR / "monthly_trend.csv", monthly_trend)
    write_csv(REPORT_DIR / "top_assets.csv", top_assets)

    print("Rapports generes dans", REPORT_DIR)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
