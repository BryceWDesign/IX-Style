"""Repository-level self-audits for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ix_style.messages import (
    CONTROL_MESSAGE_SCHEMA,
    DECISION_RECEIPT_SCHEMA,
    MISSION_HEALTH_SNAPSHOT_SCHEMA,
    SchemaValidator,
)

from .audit import audit_traceability_seed_file


@dataclass(slots=True, frozen=True)
class SelfAuditCheck:
    """One repository self-audit check result."""

    check_id: str
    passed: bool
    summary: str
    details: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "summary": self.summary,
            "details": list(self.details),
        }


@dataclass(slots=True, frozen=True)
class RepositoryAuditReport:
    """Aggregated repository self-audit report."""

    passed: bool
    checks: tuple[SelfAuditCheck, ...]
    repo_root: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return {
            "passed": self.passed,
            "repo_root": self.repo_root,
            "checks": [check.as_dict() for check in self.checks],
        }


@dataclass(slots=True)
class RepositorySelfAuditor:
    """Runs repository-level sanity checks over IX-Style artifacts."""

    repo_root: Path = field(default_factory=lambda: _default_repo_root())
    validator: SchemaValidator = field(
        default_factory=lambda: SchemaValidator(repo_root=_default_repo_root())
    )

    def run(self) -> RepositoryAuditReport:
        """Run all repository self-audits and return a structured report."""
        checks = (
            self._check_required_paths(),
            self._check_schema_loads(),
            self._check_traceability_seed(),
            self._check_example_scripts(),
        )
        return RepositoryAuditReport(
            passed=all(check.passed for check in checks),
            checks=checks,
            repo_root=str(self.repo_root),
        )

    def _check_required_paths(self) -> SelfAuditCheck:
        required_paths = (
            "LICENSE",
            "NOTICE",
            "docs/PROJECT_CHARTER.md",
            "docs/requirements/IXS-SYS-REQ-BASELINE.md",
            "docs/hazards/IXS-HAZARD-REGISTER.md",
            "docs/architecture/IXS-OPERATIONAL-MODE-MODEL.md",
            "docs/architecture/IXS-COMMAND-AUTHORITY-MODEL.md",
            "docs/architecture/IXS-RUNTIME-ASSURANCE-GUARD.md",
            "docs/architecture/IXS-FDIR-ARCHITECTURE.md",
            "docs/architecture/IXS-SENSOR-TRUST-AND-ESTIMATION-FRAMEWORK.md",
            "docs/architecture/IXS-SECURE-MESSAGING-AND-EVIDENCE-ARCHITECTURE.md",
            "docs/architecture/IXS-CONSTRAINT-CATALOG.md",
            "docs/architecture/IXS-MODE-ALLOCATION-AND-POSTURE-RESOLUTION.md",
            "docs/architecture/IXS-RECOVERY-GATE-AND-AUTHORITY-RESTORATION.md",
            "docs/architecture/IXS-TAMPER-EVIDENT-EVIDENCE-BUNDLES.md",
            "docs/developer/IXS-DEVELOPER-ONBOARDING-AND-QUICKSTART.md",
            "docs/operations/IXS-MISSION-HEALTH-AND-OPERATOR-SUPPORT.md",
            "docs/operations/IXS-OPERATOR-RATIONALE-AND-SUMMARY-LAYER.md",
            "docs/review/IXS-REVIEW-WALKTHROUGH.md",
            "docs/verification/IXS-VERIFICATION-AND-TRACEABILITY-STRATEGY.md",
            "docs/verification/IXS-REVIEW-ARTIFACT-PACKAGES.md",
            "docs/verification/IXS-INVARIANT-CHECKS-AND-PROPERTY-LAYER.md",
            "artifacts/traceability/ix_style_traceability_seed.yaml",
            "examples/power_fault_clamp_demo.py",
            "examples/nav_spoof_transition_demo.py",
            "scripts/run_repo_self_audit.py",
            "scripts/run_sample_scenarios.py",
            "scripts/run_invariant_checks.py",
            "scripts/run_quickstart_flow.py",
        )

        missing = tuple(
            path for path in required_paths if not (self.repo_root / path).exists()
        )
        if missing:
            return SelfAuditCheck(
                check_id="required_paths",
                passed=False,
                summary="one or more required repository artifacts are missing",
                details=missing,
            )

        return SelfAuditCheck(
            check_id="required_paths",
            passed=True,
            summary="required repository artifacts are present",
        )

    def _check_schema_loads(self) -> SelfAuditCheck:
        schema_paths = (
            CONTROL_MESSAGE_SCHEMA,
            DECISION_RECEIPT_SCHEMA,
            MISSION_HEALTH_SNAPSHOT_SCHEMA,
        )
        errors: list[str] = []

        for schema_path in schema_paths:
            try:
                schema = self.validator.load_schema(schema_path)
                if "$schema" not in schema:
                    errors.append(f"{schema_path} missing $schema declaration")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{schema_path}: {exc}")

        if errors:
            return SelfAuditCheck(
                check_id="schema_loads",
                passed=False,
                summary="schema loading check failed",
                details=tuple(errors),
            )

        return SelfAuditCheck(
            check_id="schema_loads",
            passed=True,
            summary="repository schemas loaded successfully",
        )

    def _check_traceability_seed(self) -> SelfAuditCheck:
        report = audit_traceability_seed_file(
            self.repo_root / "artifacts" / "traceability" / "ix_style_traceability_seed.yaml"
        )
        if not report.passed:
            return SelfAuditCheck(
                check_id="traceability_seed",
                passed=False,
                summary="traceability seed audit failed",
                details=report.errors,
            )

        details = report.warnings if report.warnings else ()
        return SelfAuditCheck(
            check_id="traceability_seed",
            passed=True,
            summary="traceability seed audit passed",
            details=details,
        )

    def _check_example_scripts(self) -> SelfAuditCheck:
        example_paths = (
            "examples/power_fault_clamp_demo.py",
            "examples/nav_spoof_transition_demo.py",
        )
        missing = tuple(
            path for path in example_paths if not (self.repo_root / path).is_file()
        )
        if missing:
            return SelfAuditCheck(
                check_id="example_scripts",
                passed=False,
                summary="one or more example scripts are missing",
                details=missing,
            )

        return SelfAuditCheck(
            check_id="example_scripts",
            passed=True,
            summary="example scenario scripts are present",
        )


def _default_repo_root() -> Path:
    """Return the repository root path."""
    return Path(__file__).resolve().parents[3]
