"""Stable identifier helpers for IX-Style artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4


class IdPrefix(StrEnum):
    MESSAGE = "MSG"
    DECISION = "DEC"
    RECEIPT = "RCPT"
    EVENT = "EV"
    FAULT = "FLT"
    TRUST = "TR"
    SCENARIO = "SCN"
    SNAPSHOT = "SNAP"
    SESSION = "SES"


def make_id(prefix: IdPrefix | str) -> str:
    """Create a stable-prefixed identifier."""
    normalized = prefix.value if isinstance(prefix, IdPrefix) else str(prefix).strip()
    if not normalized:
        raise ValueError("prefix must not be empty")
    return f"{normalized}-{uuid4().hex[:12].upper()}"


def validate_prefixed_id(value: str, prefix: IdPrefix | str) -> bool:
    """Return True when the identifier begins with the expected prefix."""
    normalized = prefix.value if isinstance(prefix, IdPrefix) else str(prefix).strip()
    return value.startswith(f"{normalized}-") and len(value) > len(normalized) + 1


@dataclass(slots=True, frozen=True)
class IdFactory:
    """Convenience generator for common IX-Style identifiers."""

    def message_id(self) -> str:
        return make_id(IdPrefix.MESSAGE)

    def decision_id(self) -> str:
        return make_id(IdPrefix.DECISION)

    def receipt_id(self) -> str:
        return make_id(IdPrefix.RECEIPT)

    def event_id(self) -> str:
        return make_id(IdPrefix.EVENT)

    def fault_id(self) -> str:
        return make_id(IdPrefix.FAULT)

    def trust_record_id(self) -> str:
        return make_id(IdPrefix.TRUST)

    def scenario_id(self) -> str:
        return make_id(IdPrefix.SCENARIO)

    def snapshot_id(self) -> str:
        return make_id(IdPrefix.SNAPSHOT)

    def session_id(self) -> str:
        return make_id(IdPrefix.SESSION)
