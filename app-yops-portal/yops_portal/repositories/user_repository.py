from yops_portal.core.security import hash_password
from yops_portal.models.entities import User
from yops_portal.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def find_by_email_with_hash(self, email: str):
        return self.fetch_one(
            """
            SELECT users.*, roles.name AS role_name
            FROM users
            JOIN roles ON roles.id = users.role_id
            WHERE users.email = ?
            """,
            (email,),
        )

    def list_users(self) -> list[User]:
        rows = self.fetch_all(
            """
            SELECT users.id, users.name, users.email, users.client_id, roles.name AS role
            FROM users
            JOIN roles ON roles.id = users.role_id
            ORDER BY roles.name, users.name
            """
        )
        return [User(row["id"], row["name"], row["email"], row["role"], row["client_id"]) for row in rows]

    def email_exists(self, email: str) -> bool:
        row = self.fetch_one("SELECT id FROM users WHERE email = ?", (email,))
        return row is not None

    def create_client_user(self, client_id: int, name: str, email: str, password: str) -> int:
        role = self.fetch_one("SELECT id FROM roles WHERE name = 'client'")
        if role is None:
            raise RuntimeError("Role client introuvable.")
        return self.execute(
            """
            INSERT INTO users (role_id, client_id, name, email, password_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (role["id"], client_id, name, email, hash_password(password)),
        )
