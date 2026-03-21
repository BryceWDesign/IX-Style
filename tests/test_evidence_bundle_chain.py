from __future__ import annotations

from datetime import UTC, datetime

from ix_style.messages import EvidenceBundleBuilder


def _now() -> datetime:
    return datetime.now(tz=UTC)


def test_evidence_bundle_validates_when_untampered() -> None:
    builder = EvidenceBundleBuilder()
    bundle = builder.build(
        scenario_id="TEST-BUNDLE-001",
        decision_receipt={
            "decision_id": "DEC-TEST-000001",
            "final_outcome": "CLAMP",
            "rationale_summary": "resource clamp applied",
        },
        trust_transitions=(
            {
                "event_id": "EV-TRUST-000001",
                "event_time": _now().isoformat(),
                "summary": "trust degraded",
                "payload": {
                    "trust_record_id": "TR-TEST-000001",
                    "previous_trust_state": "TRUSTED",
                    "new_trust_state": "DEGRADED",
                },
            },
        ),
        fault_transitions=(
            {
                "event_id": "EV-FAULT-000001",
                "event_time": _now().isoformat(),
                "summary": "fault confirmed",
                "payload": {
                    "fault_id": "FLT-TEST-000001",
                    "previous_state": "SUSPECTED",
                    "new_state": "CONFIRMED",
                },
            },
        ),
    )

    errors = builder.validate(bundle)

    assert errors == ()
    assert bundle["integrity"]["item_count"] == len(bundle["items"])


def test_evidence_bundle_validation_fails_after_tamper() -> None:
    builder = EvidenceBundleBuilder()
    bundle = builder.build(
        scenario_id="TEST-BUNDLE-002",
        decision_receipt={
            "decision_id": "DEC-TEST-000002",
            "final_outcome": "VETO",
            "rationale_summary": "navigation spoof suspected",
        },
    )

    bundle["items"][0]["data"]["rationale_summary"] = "rewritten later by tamper"
    errors = builder.validate(bundle)

    assert errors != ()
    assert any("item_hash mismatch" in error or "chain_hash mismatch" in error for error in errors)
