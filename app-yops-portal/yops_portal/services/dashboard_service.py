from yops_portal.repositories.base import BaseRepository
from yops_portal.services.client_risk_service import ClientRiskService


class DashboardService:
    def __init__(self, repository: BaseRepository, risk_service: ClientRiskService) -> None:
        self.repository = repository
        self.risk_service = risk_service

    def get_dashboard(self) -> dict:
        return {
            "stats": self._stats(),
            "severity": self._severity_breakdown(),
            "recent_vulnerabilities": self._recent_vulnerabilities(),
            "late_tickets": self._late_tickets(),
            "client_risks": self.risk_service.calculate(),
            "top_assets": self._top_assets(),
            "audit_progress": self._audit_progress(),
            "activity": self._activity_feed(),
        }

    def _stats(self) -> dict[str, int | float]:
        row = self.repository.fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM clients WHERE status = 'active') AS active_clients,
                (SELECT COUNT(*) FROM audits WHERE status = 'en_cours') AS active_audits,
                (SELECT COUNT(*) FROM vulnerabilities WHERE severity = 'critical' AND status != 'corrigee') AS critical_open,
                (SELECT COUNT(*) FROM remediation_tickets WHERE due_date < date('now') AND status != 'termine') AS late_tickets,
                (SELECT COUNT(*) FROM remediation_tickets WHERE status = 'termine') AS closed_tickets,
                (SELECT COUNT(*) FROM remediation_tickets) AS total_tickets
            """
        )
        total = int(row["total_tickets"] or 0)
        closed = int(row["closed_tickets"] or 0)
        remediation_rate = round((closed / total) * 100, 1) if total else 0
        return {
            "active_clients": row["active_clients"],
            "active_audits": row["active_audits"],
            "critical_open": row["critical_open"],
            "late_tickets": row["late_tickets"],
            "remediation_rate": remediation_rate,
        }

    def _severity_breakdown(self) -> list[dict]:
        rows = self.repository.fetch_all(
            """
            SELECT severity, COUNT(*) AS total
            FROM vulnerabilities
            GROUP BY severity
            ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
            """
        )
        return [{"severity": row["severity"], "total": row["total"]} for row in rows]

    def _recent_vulnerabilities(self) -> list[dict]:
        rows = self.repository.fetch_all(
            """
            SELECT vulnerabilities.id, vulnerabilities.title, vulnerabilities.severity,
                   vulnerabilities.status, vulnerabilities.cvss_score,
                   clients.name AS client_name
            FROM vulnerabilities
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            ORDER BY vulnerabilities.cvss_score DESC, vulnerabilities.discovered_at DESC
            LIMIT 6
            """
        )
        return [dict(row) for row in rows]

    def _top_assets(self) -> list[dict]:
        rows = self.repository.fetch_all(
            """
            SELECT vulnerabilities.asset,
                   clients.name AS client_name,
                   COUNT(*) AS total,
                   SUM(CASE WHEN vulnerabilities.status != 'corrigee' THEN 1 ELSE 0 END) AS open_count,
                   MAX(vulnerabilities.cvss_score) AS max_cvss
            FROM vulnerabilities
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            GROUP BY vulnerabilities.asset, clients.name
            HAVING open_count > 0
            ORDER BY open_count DESC, max_cvss DESC
            LIMIT 5
            """
        )
        return [dict(row) for row in rows]

    def _audit_progress(self) -> list[dict]:
        rows = self.repository.fetch_all(
            """
            SELECT audits.id, audits.title, audits.status, clients.name AS client_name,
                   COUNT(vulnerabilities.id) AS total,
                   SUM(CASE WHEN vulnerabilities.status = 'corrigee' THEN 1 ELSE 0 END) AS fixed
            FROM audits
            JOIN clients ON clients.id = audits.client_id
            LEFT JOIN vulnerabilities ON vulnerabilities.audit_id = audits.id
            WHERE audits.status IN ('en_cours', 'planifie')
            GROUP BY audits.id
            ORDER BY audits.starts_at DESC
            LIMIT 4
            """
        )
        result = []
        for row in rows:
            total = int(row["total"] or 0)
            fixed = int(row["fixed"] or 0)
            percent = round((fixed / total) * 100) if total else 0
            result.append({
                "id": row["id"],
                "title": row["title"],
                "client_name": row["client_name"],
                "status": row["status"],
                "total": total,
                "fixed": fixed,
                "percent": percent,
            })
        return result

    def _activity_feed(self) -> list[dict]:
        rows = self.repository.fetch_all(
            """
            SELECT 'vulnerability' AS kind, vulnerabilities.id AS ref_id,
                   vulnerabilities.title AS label, vulnerabilities.severity AS detail,
                   clients.name AS client_name, vulnerabilities.discovered_at AS happened_at
            FROM vulnerabilities
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id

            UNION ALL

            SELECT 'note' AS kind, client_notes.id AS ref_id,
                   client_notes.body AS label, client_notes.kind AS detail,
                   clients.name AS client_name, client_notes.created_at AS happened_at
            FROM client_notes
            JOIN clients ON clients.id = client_notes.client_id

            UNION ALL

            SELECT 'report' AS kind, reports.id AS ref_id,
                   reports.title AS label, '' AS detail,
                   clients.name AS client_name, reports.generated_at AS happened_at
            FROM reports
            JOIN audits ON audits.id = reports.audit_id
            JOIN clients ON clients.id = audits.client_id

            ORDER BY happened_at DESC
            LIMIT 8
            """
        )
        return [dict(row) for row in rows]

    def _late_tickets(self) -> list[dict]:
        rows = self.repository.fetch_all(
            """
            SELECT remediation_tickets.priority, remediation_tickets.due_date,
                   remediation_tickets.status, vulnerabilities.title, clients.name AS client_name
            FROM remediation_tickets
            JOIN vulnerabilities ON vulnerabilities.id = remediation_tickets.vulnerability_id
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            WHERE remediation_tickets.due_date < date('now') AND remediation_tickets.status != 'termine'
            ORDER BY remediation_tickets.due_date ASC
            LIMIT 5
            """
        )
        return [dict(row) for row in rows]

