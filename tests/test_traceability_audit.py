from __future__ import annotations

from ix_style.verification import audit_traceability_records, audit_traceability_seed_file


def test_traceability_seed_file_passes_baseline_audit() -> None:
    report = audit_traceability_seed_file()

    assert report.passed is True
    assert report.record_count > 0
    assert report.errors == ()


def test_traceability_audit_fails_on_missing_required_fields() -> None:
    report = audit_traceability_records(
        [
            {
                "trace_id": "TR-INVALID-001",
                "requirement_id": "IXS-SYS-999",
                "notes": "intentionally incomplete record for audit test",
                "hazard_ids": [],
                "architecture_ids": ["IXS-RUNTIME-ASSURANCE-GUARD"],
                "planned_test_ids": [],
                "expected_evidence_ids": ["EV-DECISION-RECEIPT"],
            }
        ]
    )

    assert report.passed is False
    assert any("hazard_ids" in error for error in report.errors)
    assert any("planned_test_ids" in error for error in report.errors)
