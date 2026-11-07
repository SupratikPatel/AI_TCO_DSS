"""Error hierarchy (design.md § "Error Handling")."""

from pathlib import Path


class DssError(Exception):
    """Base class of all DSS errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CatalogLoadError(DssError):
    """Catalog files failed to load; carries every `(file, field_path, message)`."""

    def __init__(self, errors: tuple[tuple[str, str, str], ...]) -> None:
        lines = [f"{file}: {field}: {message}" for file, field, message in errors]
        super().__init__(f"{len(errors)} catalog errors\n" + "\n".join(lines))
        self.errors = errors


class WorkloadFileError(DssError):
    def __init__(self, path: Path, fields: tuple[str, ...]) -> None:
        super().__init__(f"{path}: invalid workload file ({', '.join(fields) or 'unreadable'})")
        self.path = path
        self.fields = fields


class ConfigurationError(DssError):
    def __init__(self, setting: str, value: object) -> None:
        super().__init__(f"invalid setting {setting}={value!r}")
        self.setting = setting
        self.value = value


class UnknownIdentifierError(DssError):
    def __init__(self, item_type: str, identifier: str) -> None:
        super().__init__(f"unknown {item_type} id: {identifier}")
        self.item_type = item_type
        self.identifier = identifier


class EngineInputError(DssError, ValueError):
    """Invalid engine input; names the field, the allowed range and the item id if known."""

    def __init__(self, field: str, allowed: str, item_id: str | None = None) -> None:
        suffix = f" ({item_id})" if item_id else ""
        super().__init__(f"invalid {field}{suffix}: allowed {allowed}")
        self.field = field
        self.allowed = allowed
        self.item_id = item_id
