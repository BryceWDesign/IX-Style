"""Traceability audit helpers for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True, frozen=True)
class TraceabilityAuditReport:
    """Result of auditing traceability records."""

    passed: bool
    record_count: int
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


def audit_traceability_seed_file(path: str | Path | None = None) -> TraceabilityAuditReport:
    """Load and audit the default traceability seed file or a caller-supplied path."""
    selected = Path(path) if path is not None else _default_seed_path()
    if not selected.is_file():
        return TraceabilityAuditReport(
            passed=False,
            record_count=0,
            errors=(f"traceability seed file not found: {selected}",),
        )

    with selected.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    if not isinstance(loaded, dict):
        return TraceabilityAuditReport(
            passed=False,
            record_count=0,
            errors=("traceability seed root must be a mapping",),
        )

    records = loaded.get("traceability_records")
    if not isinstance(records, list):
        return TraceabilityAuditReport(
            passed=False,
            record_count=0,
            errors=("traceability_records must be a list",),
        )

    report = audit_traceability_records(records)
    return TraceabilityAuditReport(
        passed=report.passed,
        record_count=report.record_count,
        errors=report.errors,
        warnings=report.warnings,
        metadata={"source_path": str(selected)},
    )


def audit_traceability_records(records: list[dict[str, Any]]) -> TraceabilityAuditReport:
    """Audit a list of traceability records for required structure and consistency."""
    errors: list[str] = []
    warnings: list[str] = []
    seen_trace_ids: set[str] = set()

    required_scalar_fields = (
        "trace_id",
        "requirement_id",
        "notes",
    )
    required_list_fields = (
        "hazard_ids",
        "architecture_ids",
        "planned_test_ids",
        "expected_evidence_ids",
    )
    optional_list_fields = (
        "monitor_ids",
        "rule_ids",
        "mode_ids",
        "message_schema_ids",
    )

    for index, record in enumerate(records):
        label = f"record[{index}]"

        if not isinstance(record, dict):
            errors.append(f"{label} must be a mapping")
            continue

        for field_name in required_scalar_fields:
            value = record.get(field_name)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{field_name} must be a non-empty string")

        trace_id = record.get("trace_id")
        if isinstance(trace_id, str) and trace_id.strip():
            if trace_id in seen_trace_ids:
                errors.append(f"{label}.trace_id duplicates an earlier record: {trace_id}")
            seen_trace_ids.add(trace_id)

        for field_name in required_list_fields:
            _audit_string_list(
                record=record,
                field_name=field_name,
                label=label,
                errors=errors,
                warnings=warnings,
                allow_empty=False,
            )

        for field_name in optional_list_fields:
            _audit_string_list(
                record=record,
                field_name=field_name,
                label=label,
                errors=errors,
                warnings=warnings,
                allow_empty=True,
            )

        if isinstance(record.get("planned_test_ids"), list) and isinstance(
            record.get("expected_evidence_ids"), list
        ):
            if not record["planned_test_ids"]:
                errors.append(f"{label}.planned_test_ids must not be empty")
            if not record["expected_evidence_ids"]:
                errors.append(f"{label}.expected_evidence_ids must not be empty")

        if isinstance(record.get("message_schema_ids"), list) and not record["message_schema_ids"]:
            warnings.append(f"{label}.message_schema_ids is empty")

    return TraceabilityAuditReport(
        passed=not errors,
        record_count=len(records),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _audit_string_list(
    *,
    record: dict[str, Any],
    field_name: str,
    label: str,
    errors: list[str],
    warnings: list[str],
    allow_empty: bool,
) -> None:
    value = record.get(field_name)

    if value is None:
        if allow_empty:
            warnings.append(f"{label}.{field_name} is missing")
        else:
            errors.append(f"{label}.{field_name} is missing")
        return

    if not isinstance(value, list):
        errors.append(f"{label}.{field_name} must be a list")
        return

    if not allow_empty and not value:
        errors.append(f"{label}.{field_name} must not be empty")
        return

    seen: set[str] = set()
    for item_index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(
                f"{label}.{field_name}[{item_index}] must be a non-empty string"
            )
            continue
        if item in seen:
            errors.append(f"{label}.{field_name} contains duplicate entry: {item}")
        seen.add(item)


def _default_seed_path() -> Path:
    """Return the repository-default traceability seed path."""
    return Path(__file__).resolve().parents[3] / "artifacts" / "traceability" / "ix_style_traceability_seed.yaml"
