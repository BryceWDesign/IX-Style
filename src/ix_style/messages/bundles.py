"""Evidence-bundle construction and verification for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ix_style.core.ids import IdFactory

from .chain import EvidenceChain, GENESIS_MARKER


def _utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


@dataclass(slots=True)
class EvidenceBundleBuilder:
    """Builds tamper-evident evidence bundles from related review artifacts."""

    id_factory: IdFactory = field(default_factory=IdFactory)
    chain: EvidenceChain = field(default_factory=EvidenceChain)
    schema_version: str = "0.1.0"

    def build(
        self,
        *,
        scenario_id: str,
        decision_receipt: dict[str, Any],
        trust_transitions: tuple[dict[str, Any], ...] = (),
        fault_transitions: tuple[dict[str, Any], ...] = (),
        mode_transitions: tuple[dict[str, Any], ...] = (),
        created_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Build a deterministic tamper-evident bundle."""
        if not scenario_id.strip():
            raise ValueError("scenario_id must not be empty")

        created = created_at or _utc_now()
        items = self._ordered_items(
            decision_receipt=decision_receipt,
            trust_transitions=trust_transitions,
            fault_transitions=fault_transitions,
            mode_transitions=mode_transitions,
        )

        chain_input = [
            (item["item_type"], item["item_id"], item["data"])
            for item in items
        ]
        links, head_hash = self.chain.build_links(chain_input)

        bundle_items: list[dict[str, Any]] = []
        for item, link in zip(items, links):
            bundle_items.append(
                {
                    "item_index": link.item_index,
                    "item_type": link.item_type,
                    "item_id": link.item_id,
                    "item_hash": link.item_hash,
                    "previous_chain_hash": link.previous_chain_hash,
                    "chain_hash": link.chain_hash,
                    "data": item["data"],
                }
            )

        return {
            "bundle_id": self.id_factory.receipt_id(),
            "schema_version": self.schema_version,
            "created_at": created.isoformat(),
            "scenario_id": scenario_id,
            "integrity": {
                "algorithm": "sha256",
                "genesis_marker": GENESIS_MARKER,
                "head_chain_hash": head_hash,
                "item_count": len(bundle_items),
            },
            "items": bundle_items,
        }

    def validate(self, bundle: dict[str, Any]) -> tuple[str, ...]:
        """Return validation errors for an evidence bundle."""
        errors: list[str] = []

        for field_name in ("bundle_id", "schema_version", "created_at", "scenario_id", "integrity", "items"):
            if field_name not in bundle:
                errors.append(f"missing required bundle field: {field_name}")

        if errors:
            return tuple(errors)

        integrity = bundle["integrity"]
        if not isinstance(integrity, dict):
            return ("integrity field must be a mapping",)

        for field_name in ("algorithm", "genesis_marker", "head_chain_hash", "item_count"):
            if field_name not in integrity:
                errors.append(f"missing required integrity field: {field_name}")

        items = bundle["items"]
        if not isinstance(items, list):
            errors.append("items must be a list")
            return tuple(errors)

        if integrity.get("item_count") != len(items):
            errors.append("integrity.item_count does not match items length")

        ordered_items: list[tuple[str, str, dict[str, Any]]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{index}] must be a mapping")
                continue

            for field_name in (
                "item_index",
                "item_type",
                "item_id",
                "item_hash",
                "previous_chain_hash",
                "chain_hash",
                "data",
            ):
                if field_name not in item:
                    errors.append(f"items[{index}] missing field: {field_name}")

            if errors:
                continue

            data = item["data"]
            if not isinstance(data, dict):
                errors.append(f"items[{index}].data must be a mapping")
                continue

            ordered_items.append((item["item_type"], item["item_id"], data))

        if errors:
            return tuple(errors)

        chain_errors = self.chain.verify_links(
            ordered_items,
            items,
            expected_head_chain_hash=integrity["head_chain_hash"],
        )
        return tuple(errors) + chain_errors

    @staticmethod
    def _ordered_items(
        *,
        decision_receipt: dict[str, Any],
        trust_transitions: tuple[dict[str, Any], ...],
        fault_transitions: tuple[dict[str, Any], ...],
        mode_transitions: tuple[dict[str, Any], ...],
    ) -> list[dict[str, Any]]:
        """Return ordered bundle items in a deterministic review-oriented order."""
        items: list[dict[str, Any]] = [
            {
                "item_type": "decision_receipt",
                "item_id": str(decision_receipt["decision_id"]),
                "data": decision_receipt,
            }
        ]

        for event in trust_transitions:
            items.append(
                {
                    "item_type": "trust_transition",
                    "item_id": str(event["event_id"]),
                    "data": event,
                }
            )

        for event in fault_transitions:
            items.append(
                {
                    "item_type": "fault_transition",
                    "item_id": str(event["event_id"]),
                    "data": event,
                }
            )

        for event in mode_transitions:
            items.append(
                {
                    "item_type": "mode_transition",
                    "item_id": str(event["event_id"]),
                    "data": event,
                }
            )

        return items
