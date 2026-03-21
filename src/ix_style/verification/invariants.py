"""Executable invariant checks for IX-Style verification results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ix_style.messages import EvidenceBundleBuilder

from .models import VerificationResult


@dataclass(slots=True, frozen=True)
class InvariantCheckResult:
    """Result of one invariant check."""

    invariant_id: str
    passed: bool
    summary: str
    details: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return {
            "invariant_id": self.invariant_id,
            "passed": self.passed,
            "summary": self.summary,
            "details": list(self.details),
        }


@dataclass(slots=True, frozen=True)
class InvariantReport:
    """Aggregated invariant report for one verification result."""

    scenario_id: str
    passed: bool
    checks: tuple[InvariantCheckResult, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "passed": self.passed,
            "checks": [check.as_dict() for check in self.checks],
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class InvariantChecker:
    """Checks baseline executable invariants over one verification result."""

    bundle_builder: EvidenceBundleBuilder = field(default_factory=EvidenceBundleBuilder)

    def evaluate(self, result: VerificationResult) -> InvariantReport:
        """Run all baseline invariant checks for one verification result."""
        checks = (
            self._check_recovery_gate_blocks_before_authority(result),
            self._check_authority_accepted_reaches_guard(result),
            self._check_recovery_actions_require_gate_evidence(result),
            self._check_posture_changes_emit_mode_transition(result),
            self._check_decision_receipt_required_fields(result),
            self._check_evidence_bundle_validates(result),
        )
        return InvariantReport(
            scenario_id=result.scenario.scenario_id,
            passed=all(check.passed for check in checks),
            checks=checks,
            metadata={
                "derived_dominant_safety_posture": result.derived_dominant_safety_posture.value,
                "final_outcome": result.evidence_package.decision_receipt.get(
                    "final_outcome", "UNKNOWN"
                ),
            },
        )

    def _check_recovery_gate_blocks_before_authority(
        self,
        result: VerificationResult,
    ) -> InvariantCheckResult:
        trace = result.pipeline_trace
        gate_status = str(trace.get("recovery_gate_status", "NOT_APPLICABLE"))
        authority_present = bool(trace.get("authority_decision_present", False))
        guard_present = bool(trace.get("guard_decision_present", False))
        final_outcome = str(result.evidence_package.decision_receipt.get("final_outcome"))

        if gate_status not in {"FAILED", "DEFERRED"}:
            return InvariantCheckResult(
                invariant_id="IXS-INV-001",
                passed=True,
                summary="recovery gate did not block progression in this scenario",
            )

        expected_outcome = "REJECT" if gate_status == "FAILED" else "DEFER"
        failures: list[str] = []
        if authority_present:
            failures.append("authority evaluation should not proceed after blocked recovery")
        if guard_present:
            failures.append("guard evaluation should not proceed after blocked recovery")
        if final_outcome != expected_outcome:
            failures.append(
                f"expected final outcome {expected_outcome} when recovery gate is {gate_status}"
            )

        return InvariantCheckResult(
            invariant_id="IXS-INV-001",
            passed=not failures,
            summary=(
                "recovery gate blocked progression before authority and guard evaluation"
                if not failures
                else "recovery gate blocking invariant failed"
            ),
            details=tuple(failures),
        )

    def _check_authority_accepted_reaches_guard(
        self,
        result: VerificationResult,
    ) -> InvariantCheckResult:
        trace = result.pipeline_trace
        recovery_gate_status = str(trace.get("recovery_gate_status", "NOT_APPLICABLE"))
        authority_outcome = trace.get("authority_outcome")
        authority_present = bool(trace.get("authority_decision_present", False))
        guard_present = bool(trace.get("guard_decision_present", False))

        if recovery_gate_status in {"FAILED", "DEFERRED"}:
            return InvariantCheckResult(
                invariant_id="IXS-INV-002",
                passed=True,
                summary="authority-to-guard progression was not applicable after recovery gating",
            )

        if not authority_present:
            return InvariantCheckResult(
                invariant_id="IXS-INV-002",
                passed=False,
                summary="authority decision was expected but missing",
                details=("authority_decision_present is false",),
            )

        if authority_outcome != "ACCEPT":
            return InvariantCheckResult(
                invariant_id="IXS-INV-002",
                passed=True,
                summary="authority did not accept the candidate command, so guard progression was not required",
            )

        if not guard_present:
            return InvariantCheckResult(
                invariant_id="IXS-INV-002",
                passed=False,
                summary="authority accepted the candidate command but guard evaluation did not occur",
                details=("guard_decision_present is false",),
            )

        return InvariantCheckResult(
            invariant_id="IXS-INV-002",
            passed=True,
            summary="authority-accepted command reached guard evaluation",
        )

    def _check_recovery_actions_require_gate_evidence(
        self,
        result: VerificationResult,
    ) -> InvariantCheckResult:
        candidate = result.evidence_package.decision_receipt.get("candidate_action_summary", {})
        function_class = str(candidate.get("function_class", "UNKNOWN"))
        gate_result = str(result.evidence_package.decision_receipt.get("recovery_gate_result"))
        trace_gate_present = bool(result.pipeline_trace.get("recovery_decision_present", False))

        if function_class != "RECOVERY_ACTION":
            return InvariantCheckResult(
                invariant_id="IXS-INV-003",
                passed=True,
                summary="recovery-gate evidence requirement was not applicable to this command class",
            )

        failures: list[str] = []
        if gate_result == "NOT_APPLICABLE":
            failures.append("recovery-gate result must not be NOT_APPLICABLE for recovery actions")
        if not trace_gate_present:
            failures.append("recovery decision trace is missing for recovery action")

        return InvariantCheckResult(
            invariant_id="IXS-INV-003",
            passed=not failures,
            summary=(
                "recovery action carried explicit recovery-gate evidence"
                if not failures
                else "recovery action lacked required recovery-gate evidence"
            ),
            details=tuple(failures),
        )

    def _check_posture_changes_emit_mode_transition(
        self,
        result: VerificationResult,
    ) -> InvariantCheckResult:
        base_posture = result.scenario.safety_posture.value
        dominant_posture = result.derived_dominant_safety_posture.value
        mode_transition_count = len(result.evidence_package.mode_transitions)

        if base_posture == dominant_posture:
            return InvariantCheckResult(
                invariant_id="IXS-INV-004",
                passed=True,
                summary="dominant posture did not change, so no mode transition record was required",
            )

        if mode_transition_count < 1:
            return InvariantCheckResult(
                invariant_id="IXS-INV-004",
                passed=False,
                summary="dominant posture changed without a mode transition record",
                details=("mode_transition_count is 0",),
            )

        return InvariantCheckResult(
            invariant_id="IXS-INV-004",
            passed=True,
            summary="dominant posture change emitted at least one mode transition record",
        )

    def _check_decision_receipt_required_fields(
        self,
        result: VerificationResult,
    ) -> InvariantCheckResult:
        receipt = result.evidence_package.decision_receipt
        required = (
            "decision_id",
            "final_outcome",
            "rationale_summary",
            "recovery_gate_result",
            "candidate_action_summary",
        )
        missing = tuple(field_name for field_name in required if field_name not in receipt)

        if missing:
            return InvariantCheckResult(
                invariant_id="IXS-INV-005",
                passed=False,
                summary="decision receipt is missing required explanatory fields",
                details=missing,
            )

        if not str(receipt.get("rationale_summary", "")).strip():
            return InvariantCheckResult(
                invariant_id="IXS-INV-005",
                passed=False,
                summary="decision receipt rationale_summary is empty",
                details=("rationale_summary",),
            )

        return InvariantCheckResult(
            invariant_id="IXS-INV-005",
            passed=True,
            summary="decision receipt contains required explanatory fields",
        )

    def _check_evidence_bundle_validates(
        self,
        result: VerificationResult,
    ) -> InvariantCheckResult:
        bundle = result.evidence_package.evidence_bundle
        errors = self.bundle_builder.validate(bundle)

        if errors:
            return InvariantCheckResult(
                invariant_id="IXS-INV-006",
                passed=False,
                summary="evidence bundle failed validation",
                details=errors,
            )

        return InvariantCheckResult(
            invariant_id="IXS-INV-006",
            passed=True,
            summary="evidence bundle validated cleanly",
        )
