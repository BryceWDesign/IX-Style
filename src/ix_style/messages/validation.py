"""Schema loading and validation utilities for IX-Style."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


CONTROL_MESSAGE_SCHEMA = "schemas/messages/control_message.schema.json"
DECISION_RECEIPT_SCHEMA = "schemas/evidence/decision_receipt.schema.json"


class SchemaValidationError(ValueError):
    """Raised when a document does not satisfy the selected schema."""

    def __init__(self, schema_path: str, errors: tuple[str, ...]) -> None:
        self.schema_path = schema_path
        self.errors = errors
        joined = "; ".join(errors) if errors else "unknown validation error"
        super().__init__(f"{schema_path} validation failed: {joined}")


@dataclass(slots=True)
class SchemaValidator:
    """Loads repository schemas and validates structured artifacts against them."""

    repo_root: Path = field(default_factory=lambda: _default_repo_root())

    def schema_path(self, relative_path: str) -> Path:
        """Return the resolved path to a schema within the repository."""
        path = self.repo_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"schema not found: {path}")
        return path

    def load_schema(self, relative_path: str) -> dict[str, Any]:
        """Load and return a JSON schema document."""
        return _load_schema_file(self.schema_path(relative_path))

    def validate(self, relative_path: str, document: dict[str, Any]) -> tuple[str, ...]:
        """Return a tuple of validation errors. Empty tuple means success."""
        schema = self.load_schema(relative_path)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
        return tuple(_format_error(error) for error in errors)

    def validate_or_raise(self, relative_path: str, document: dict[str, Any]) -> None:
        """Validate a document and raise SchemaValidationError when invalid."""
        errors = self.validate(relative_path, document)
        if errors:
            raise SchemaValidationError(relative_path, errors)


def _default_repo_root() -> Path:
    """Return the repository root path based on this module location."""
    return Path(__file__).resolve().parents[3]


@lru_cache(maxsize=16)
def _load_schema_file(path: Path) -> dict[str, Any]:
    """Load a JSON schema file with a small cache."""
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise TypeError(f"schema at {path} must be a JSON object")
    return loaded


def _format_error(error: Any) -> str:
    """Return a stable, human-readable validation error string."""
    location = "$"
    if error.path:
        location += "." + ".".join(str(item) for item in error.path)
    return f"{location}: {error.message}"
