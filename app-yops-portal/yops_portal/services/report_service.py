from pathlib import Path

from yops_portal.repositories.base import BaseRepository


class ReportService:
    def __init__(self, repository: BaseRepository, output_dir: Path) -> None:
        self.repository = repository
        self.output_dir = output_dir

    def executive_summary(self) -> dict:
        rows = self.repository.fetch_all(
            """
            SELECT clients.name AS client_name,
                   COUNT(vulnerabilities.id) AS vulnerabilities,
                   SUM(CASE WHEN vulnerabilities.severity = 'critical' THEN 1 ELSE 0 END) AS critical,
                   SUM(CASE WHEN vulnerabilities.severity = 'high' THEN 1 ELSE 0 END) AS high
            FROM clients
            LEFT JOIN audits ON audits.client_id = clients.id
            LEFT JOIN vulnerabilities ON vulnerabilities.audit_id = audits.id
            GROUP BY clients.id
            ORDER BY critical DESC, high DESC
            """
        )
        return {"clients": [dict(row) for row in rows]}

