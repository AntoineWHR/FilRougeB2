from yops_portal.models.entities import AuditRequest
from yops_portal.repositories.base import BaseRepository


SELECT_BASE = """
SELECT audit_requests.*,
       clients.name AS client_name,
       requester.name AS requested_by_name,
       responder.name AS responded_by_name
FROM audit_requests
JOIN clients ON clients.id = audit_requests.client_id
JOIN users AS requester ON requester.id = audit_requests.requested_by
LEFT JOIN users AS responder ON responder.id = audit_requests.responded_by
"""


class AuditRequestRepository(BaseRepository):
    def list_pending(self) -> list[AuditRequest]:
        rows = self.fetch_all(SELECT_BASE + "WHERE audit_requests.status = 'pending' ORDER BY audit_requests.created_at DESC")
        return [self._map(row) for row in rows]

    def list_all(self) -> list[AuditRequest]:
        rows = self.fetch_all(SELECT_BASE + "ORDER BY audit_requests.created_at DESC")
        return [self._map(row) for row in rows]

    def list_for_client(self, client_id: int) -> list[AuditRequest]:
        rows = self.fetch_all(
            SELECT_BASE + "WHERE audit_requests.client_id = ? ORDER BY audit_requests.created_at DESC",
            (client_id,),
        )
        return [self._map(row) for row in rows]

    def find(self, request_id: int) -> AuditRequest | None:
        row = self.fetch_one(SELECT_BASE + "WHERE audit_requests.id = ?", (request_id,))
        return self._map(row) if row else None

    def create(self, data: dict) -> int:
        return self.execute(
            """
            INSERT INTO audit_requests (client_id, requested_by, audit_type, scope, rules, urgency, target_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["client_id"],
                data["requested_by"],
                data["audit_type"],
                data["scope"],
                data.get("rules", ""),
                data.get("urgency", "normal"),
                data.get("target_date") or None,
            ),
        )

    def respond(self, request_id: int, status: str, responder_id: int, message: str, audit_id: int | None) -> None:
        self.execute(
            """
            UPDATE audit_requests
            SET status = ?,
                admin_response = ?,
                responded_by = ?,
                responded_at = CURRENT_TIMESTAMP,
                audit_id = ?
            WHERE id = ?
            """,
            (status, message, responder_id, audit_id, request_id),
        )

    def count_pending(self) -> int:
        row = self.fetch_one("SELECT COUNT(*) AS total FROM audit_requests WHERE status = 'pending'")
        return int(row["total"] if row else 0)

    def _map(self, row) -> AuditRequest:
        return AuditRequest(
            id=row["id"],
            client_id=row["client_id"],
            client_name=row["client_name"],
            requested_by_name=row["requested_by_name"],
            audit_type=row["audit_type"],
            scope=row["scope"],
            rules=row["rules"],
            urgency=row["urgency"],
            target_date=row["target_date"],
            status=row["status"],
            admin_response=row["admin_response"],
            responded_by_name=row["responded_by_name"],
            responded_at=row["responded_at"],
            audit_id=row["audit_id"],
            created_at=row["created_at"],
        )
