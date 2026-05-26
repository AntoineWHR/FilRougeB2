from yops_portal.models.entities import ClientNote
from yops_portal.repositories.base import BaseRepository


class ClientNoteRepository(BaseRepository):
    def list_for_client(self, client_id: int) -> list[ClientNote]:
        rows = self.fetch_all(
            """
            SELECT client_notes.*, clients.name AS client_name, users.name AS author_name
            FROM client_notes
            JOIN clients ON clients.id = client_notes.client_id
            JOIN users ON users.id = client_notes.author_id
            WHERE client_notes.client_id = ?
            ORDER BY client_notes.created_at DESC
            """,
            (client_id,),
        )
        return [self._map(row) for row in rows]

    def list_recent(self, limit: int = 6) -> list[ClientNote]:
        rows = self.fetch_all(
            """
            SELECT client_notes.*, clients.name AS client_name, users.name AS author_name
            FROM client_notes
            JOIN clients ON clients.id = client_notes.client_id
            JOIN users ON users.id = client_notes.author_id
            ORDER BY client_notes.created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [self._map(row) for row in rows]

    def create(self, client_id: int, author_id: int, kind: str, body: str) -> int:
        return self.execute(
            """
            INSERT INTO client_notes (client_id, author_id, kind, body)
            VALUES (?, ?, ?, ?)
            """,
            (client_id, author_id, kind, body),
        )

    def _map(self, row) -> ClientNote:
        return ClientNote(
            row["id"],
            row["client_id"],
            row["client_name"],
            row["author_name"],
            row["kind"],
            row["body"],
            row["created_at"],
        )
