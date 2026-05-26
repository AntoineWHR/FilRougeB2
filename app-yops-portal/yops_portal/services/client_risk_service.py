from dataclasses import dataclass

from yops_portal.repositories.base import BaseRepository


@dataclass(frozen=True)
class ClientRisk:
    client_name: str
    critical: int
    high: int
    medium: int
    low: int
    score: int
    level: str


class ClientRiskService:
    def __init__(self, repository: BaseRepository) -> None:
        self.repository = repository

    def calculate(self) -> list[ClientRisk]:
        rows = self.repository.fetch_all(
            """
            SELECT clients.name AS client_name,
                   SUM(CASE WHEN vulnerabilities.severity = 'critical' THEN 1 ELSE 0 END) AS critical,
                   SUM(CASE WHEN vulnerabilities.severity = 'high' THEN 1 ELSE 0 END) AS high,
                   SUM(CASE WHEN vulnerabilities.severity = 'medium' THEN 1 ELSE 0 END) AS medium,
                   SUM(CASE WHEN vulnerabilities.severity = 'low' THEN 1 ELSE 0 END) AS low
            FROM clients
            LEFT JOIN audits ON audits.client_id = clients.id
            LEFT JOIN vulnerabilities ON vulnerabilities.audit_id = audits.id
            GROUP BY clients.id
            ORDER BY critical DESC, high DESC, medium DESC
            """
        )
        risks: list[ClientRisk] = []
        for row in rows:
            critical = int(row["critical"] or 0)
            high = int(row["high"] or 0)
            medium = int(row["medium"] or 0)
            low = int(row["low"] or 0)
            score = critical * 25 + high * 12 + medium * 5 + low * 2
            level = "critique" if score >= 50 else "eleve" if score >= 25 else "modere" if score >= 10 else "faible"
            risks.append(ClientRisk(row["client_name"], critical, high, medium, low, score, level))
        return risks

