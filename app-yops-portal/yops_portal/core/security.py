import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from typing import Optional


PBKDF2_ITERATIONS = 260_000


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    expected = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(expected, stored_hash)


@dataclass(frozen=True)
class SessionUser:
    id: int
    name: str
    email: str
    role: str
    client_id: int | None = None


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionUser] = {}

    def create(self, user: SessionUser) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = user
        return token

    def get(self, token: str | None) -> SessionUser | None:
        if not token:
            return None
        return self._sessions.get(token)

    def delete(self, token: str | None) -> None:
        if token:
            self._sessions.pop(token, None)

