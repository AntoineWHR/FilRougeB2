class ValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(", ".join(errors))


def require_fields(data: dict[str, str], fields: list[str]) -> None:
    errors = [f"Le champ {field} est obligatoire." for field in fields if not data.get(field, "").strip()]
    if errors:
        raise ValidationError(errors)

