from __future__ import annotations

from yops_portal.repositories.client_repository import ClientRepository
from yops_portal.repositories.user_repository import UserRepository
from yops_portal.services.validation import ValidationError, require_fields


class RegistrationService:
    def __init__(self, clients: ClientRepository, users: UserRepository) -> None:
        self.clients = clients
        self.users = users

    def register_client(self, data: dict[str, str]) -> None:
        require_fields(data, ["company", "sector", "name", "email", "phone", "password"])
        if len(data["password"]) < 10:
            raise ValidationError(["Le mot de passe doit contenir au moins 10 caracteres."])
        if self.users.email_exists(data["email"]):
            raise ValidationError(["Un compte existe deja avec cet email."])
        client_id = self.clients.create(
            {
                "name": data["company"],
                "sector": data["sector"],
                "contact_name": data["name"],
                "email": data["email"],
                "phone": data["phone"],
                "status": "prospect",
            }
        )
        self.users.create_client_user(client_id, data["name"], data["email"], data["password"])
