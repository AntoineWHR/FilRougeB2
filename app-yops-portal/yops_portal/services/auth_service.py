from yops_portal.core.security import SessionUser, verify_password
from yops_portal.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def authenticate(self, email: str, password: str) -> SessionUser | None:
        row = self.users.find_by_email_with_hash(email)
        if row is None:
            return None
        if not verify_password(password, row["password_hash"]):
            return None
        return SessionUser(row["id"], row["name"], row["email"], row["role_name"], row["client_id"])

