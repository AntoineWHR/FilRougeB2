from yops_portal.models.entities import Report
from yops_portal.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    def list_reports(self) -> list[Report]:
        rows = self.fetch_all(
            """
            SELECT reports.*, audits.title AS audit_title, clients.name AS client_name
            FROM reports
            JOIN audits ON audits.id = reports.audit_id
            JOIN clients ON clients.id = audits.client_id
            ORDER BY reports.generated_at DESC
            """
        )
        return [
            Report(
                row["id"],
                row["audit_title"],
                row["client_name"],
                row["title"],
                row["executive_summary"],
                row["generated_at"],
            )
            for row in rows
        ]

    def list_for_client(self, client_id: int) -> list[Report]:
        rows = self.fetch_all(
            """
            SELECT reports.*, audits.title AS audit_title, clients.name AS client_name
            FROM reports
            JOIN audits ON audits.id = reports.audit_id
            JOIN clients ON clients.id = audits.client_id
            WHERE clients.id = ?
            ORDER BY reports.generated_at DESC
            """,
            (client_id,),
        )
        return [
            Report(
                row["id"],
                row["audit_title"],
                row["client_name"],
                row["title"],
                row["executive_summary"],
                row["generated_at"],
            )
            for row in rows
        ]
