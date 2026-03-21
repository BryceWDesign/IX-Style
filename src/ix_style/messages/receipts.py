"""Decision-evidence receipt builders for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ix_style.core.enums import (
    IntegrityState,
    ReviewSignificance,
)
from ix_style.core.ids import IdFactory
from ix_style.core.models import DecisionReceiptPayload


def _utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


@dataclass(slots=True)
class DecisionReceiptBuilder:
    """Builds full decision-receipt documents aligned to the evidence schema."""

    id_factory: IdFactory = field(default_factory=IdFactory)
    schema_version: str = "0.1.0"
    source_id: str = "ix-style"
    source_kind: str = "infrastructure"

    def build(
        self,
        *,
        payload: DecisionReceiptPayload,
        session_id: str,
        sequence_number: int,
        review_significance: ReviewSignificance = ReviewSignificance.IMPORTANT,
        parent_message_id: str | None = None,
        triggering_event_id: str | None = None,
        integrity_state: IntegrityState = IntegrityState.INTEGRITY_VALID,
        signature_present: bool = False,
        chain_hash: str | None = None,
        verification_rationale: str | None = None,
        created_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Return a full receipt document ready for schema validation or storage."""
        if not session_id.strip():
            raise ValueError("session_id must not be empty")
        if sequence_number < 0:
            raise ValueError("sequence_number must be non-negative")

        created = created_at or _utc_now()
        payload_dict = payload.as_dict()

        ordering: dict[str, Any] = {
            "sequence_number": sequence_number,
            "session_id": session_id,
            "review_significance": review_significance.value,
        }
        if parent_message_id is not None:
            ordering["parent_message_id"] = parent_message_id
        if triggering_event_id is not None:
            ordering["triggering_event_id"] = triggering_event_id

        integrity: dict[str, Any] = {
            "integrity_state": integrity_state.value,
            "signature_present": signature_present,
        }
        if chain_hash is not None:
            integrity["chain_hash"] = chain_hash
        if verification_rationale is not None:
            integrity["verification_rationale"] = verification_rationale

        return {
            "schema_version": self.schema_version,
            "message_id": self.id_factory.receipt_id(),
            "message_class": "EVIDENCE",
            "message_type": "evidence.decision_receipt",
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "created_at": created.isoformat(),
            "ordering": ordering,
            "integrity": integrity,
            "payload": payload_dict,
        }
