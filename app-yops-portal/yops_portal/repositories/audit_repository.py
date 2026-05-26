from yops_portal.models.entities import Audit
from yops_portal.repositories.base import BaseRepository


class AuditRepository(BaseRepository):
    def list_audits(self) -> list[Audit]:
        rows = self.fetch_all(
            """
            SELECT audits.*, clients.name AS client_name, users.name AS owner_name
            FROM audits
            JOIN clients ON clients.id = audits.client_id
            JOIN users ON users.id = audits.owner_id
            ORDER BY audits.starts_at DESC
            """
        )
        return [self._map(row) for row in rows]

    def list_for_client(self, client_id: int) -> list[Audit]:
        rows = self.fetch_all(
            """
            SELECT audits.*, clients.name AS client_name, users.name AS owner_name
            FROM audits
            JOIN clients ON clients.id = audits.client_id
            JOIN users ON users.id = audits.owner_id
            WHERE clients.id = ?
            ORDER BY audits.starts_at DESC
            """,
            (client_id,),
        )
        return [self._map(row) for row in rows]

    def find(self, audit_id: int) -> Audit | None:
        row = self.fetch_one(
            """
            SELECT audits.*, clients.name AS client_name, users.name AS owner_name
            FROM audits
            JOIN clients ON clients.id = audits.client_id
            JOIN users ON users.id = audits.owner_id
            WHERE audits.id = ?
            """,
            (audit_id,),
        )
        return self._map(row) if row else None

    def _map(self, row) -> Audit:
        return Audit(
            row["id"],
            row["client_id"],
            row["client_name"],
            row["owner_name"],
            row["title"],
            row["audit_type"],
            row["starts_at"],
            row["ends_at"],
            row["status"],
        )
