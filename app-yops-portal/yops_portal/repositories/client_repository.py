from yops_portal.models.entities import Client
from yops_portal.repositories.base import BaseRepository


class ClientRepository(BaseRepository):
    def list_clients(self) -> list[Client]:
        rows = self.fetch_all("SELECT * FROM clients ORDER BY name")
        return [Client(row["id"], row["name"], row["sector"], row["contact_name"], row["email"], row["phone"], row["status"]) for row in rows]

    def find(self, client_id: int) -> Client | None:
        row = self.fetch_one("SELECT * FROM clients WHERE id = ?", (client_id,))
        if row is None:
            return None
        return Client(row["id"], row["name"], row["sector"], row["contact_name"], row["email"], row["phone"], row["status"])

    def create(self, data: dict[str, str]) -> int:
        return self.execute(
            """
            INSERT INTO clients (name, sector, contact_name, email, phone, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data["name"], data["sector"], data["contact_name"], data["email"], data["phone"], data["status"]),
        )

