from yops_portal.models.entities import ReportDelivery
from yops_portal.repositories.base import BaseRepository


SELECT_BASE = """
SELECT report_deliveries.*,
       clients.name AS client_name,
       users.name AS sent_by_name
FROM report_deliveries
JOIN clients ON clients.id = report_deliveries.client_id
JOIN users ON users.id = report_deliveries.sent_by
"""


class ReportDeliveryRepository(BaseRepository):
    def create(self, client_id: int, sent_by: int, filename: str, file_path: str, vuln_count: int, critical_count: int) -> int:
        return self.execute(
            """
            INSERT INTO report_deliveries (client_id, sent_by, filename, file_path, vuln_count, critical_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (client_id, sent_by, filename, file_path, vuln_count, critical_count),
        )

    def list_for_client(self, client_id: int) -> list[ReportDelivery]:
        rows = self.fetch_all(
            SELECT_BASE + "WHERE report_deliveries.client_id = ? ORDER BY report_deliveries.delivered_at DESC",
            (client_id,),
        )
        return [self._map(row) for row in rows]

    def list_recent(self, limit: int = 8) -> list[ReportDelivery]:
        rows = self.fetch_all(
            SELECT_BASE + "ORDER BY report_deliveries.delivered_at DESC LIMIT ?",
            (limit,),
        )
        return [self._map(row) for row in rows]

    def find(self, delivery_id: int) -> ReportDelivery | None:
        row = self.fetch_one(SELECT_BASE + "WHERE report_deliveries.id = ?", (delivery_id,))
        return self._map(row) if row else None

    def mark_read(self, delivery_id: int) -> None:
        self.execute(
            "UPDATE report_deliveries SET read_at = CURRENT_TIMESTAMP WHERE id = ? AND read_at IS NULL",
            (delivery_id,),
        )

    def _map(self, row) -> ReportDelivery:
        return ReportDelivery(
            id=row["id"],
            client_id=row["client_id"],
            client_name=row["client_name"],
            sent_by_name=row["sent_by_name"],
            filename=row["filename"],
            file_path=row["file_path"],
            vuln_count=row["vuln_count"],
            critical_count=row["critical_count"],
            delivered_at=row["delivered_at"],
            read_at=row["read_at"],
        )
