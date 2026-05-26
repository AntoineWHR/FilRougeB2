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
            SELECT vulnerabilities.title, vulnerabilities.severity, vulnerabilities.status,
                   vulnerabilities.cvss_score, clients.name AS client_name
            FROM vulnerabilities
            JOIN audits ON audits.id = vulnerabilities.audit_id
            JOIN clients ON clients.id = audits.client_id
            ORDER BY vulnerabilities.discovered_at DESC
            LIMIT 6
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

