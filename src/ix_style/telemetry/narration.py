"""Operator-facing rationale formatting and concise safety-summary narration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

from .mission_health import MissionHealthBuilder

if TYPE_CHECKING:
    from ix_style.verification.models import VerificationResult


_SIGNIFICANCE_ORDER: dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "IMPORTANT": 2,
    "ROUTINE": 1,
}


@dataclass(slots=True, frozen=True)
class OperatorSafetySummary:
    """Compact operator-facing summary derived from structured IX-Style state."""

    headline: str
    decision_rationale: str
    operational_why: str
    authority_statement: str
    recovery_statement: str
    operator_focus: str
    concise_narrative: str
    timeline_markers: tuple[str, ...] = ()
    review_significance: str = "ROUTINE"

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return asdict(self)


@dataclass(slots=True)
class OperatorRationaleFormatter:
    """Formats concise operator-facing rationale strings from structured data."""

    def decision_rationale(self, decision_receipt: dict[str, Any]) -> str:
        """Return a compact explanation of what happened to the candidate action."""
        outcome = str(decision_receipt.get("final_outcome", "UNKNOWN"))
        rationale = self._sentence(str(decision_receipt.get("rationale_summary", "")))
        gate_result = str(decision_receipt.get("recovery_gate_result", "NOT_APPLICABLE"))
        change_type = str(
            decision_receipt.get("command_delta", {}).get("change_type", "NONE")
        )

        if gate_result == "FAILED":
            return self._sentence(
                f"Recovery expansion was blocked. {rationale}".strip()
            )
        if gate_result == "DEFERRED":
            return self._sentence(
                f"Recovery expansion was deferred. {rationale}".strip()
            )

        if outcome == "ACCEPT":
            return self._sentence(f"Command was accepted. {rationale}".strip())
        if outcome == "CLAMP":
            return self._sentence(f"Command was clamped. {rationale}".strip())
        if outcome == "SUBSTITUTE":
            return self._sentence(f"Command was substituted. {rationale}".strip())
        if outcome == "VETO":
            return self._sentence(f"Command was vetoed. {rationale}".strip())
        if outcome == "FREEZE":
            return self._sentence(f"Command path was frozen. {rationale}".strip())
        if outcome == "DEFER":
            return self._sentence(f"Command was deferred. {rationale}".strip())
        if outcome == "REJECT":
            return self._sentence(f"Command was rejected. {rationale}".strip())

        if change_type != "NONE":
            return self._sentence(f"Command change type is {change_type}. {rationale}".strip())

        return self._sentence(rationale or "Decision outcome is available in the evidence record")

    def authority_statement(self, snapshot: dict[str, Any]) -> str:
        """Return a compact authority statement for an operator."""
        authority = snapshot.get("authority_summary", {})
        dominant_source = str(authority.get("dominant_authoritative_source", "UNKNOWN"))
        supervisor_bias = str(authority.get("safety_supervisor_bias", "UNKNOWN"))
        remote_status = str(authority.get("remote_operator_command_status", "UNKNOWN"))

        return self._sentence(
            "Authority currently rests with "
            f"{dominant_source}; supervisor bias is {supervisor_bias}; "
            f"remote operator status is {remote_status}"
        )

    def recovery_statement(self, snapshot: dict[str, Any]) -> str:
        """Return a compact recovery-status statement for an operator."""
        recovery = snapshot.get("recovery_summary", {})
        recovery_state = str(recovery.get("recovery_state", "RECOVERY_NOT_APPLICABLE"))
        blocking_reason = str(recovery.get("blocking_reason_summary", "")).strip()

        mapping = {
            "RECOVERY_NOT_APPLICABLE": "Recovery expansion is not currently under review",
            "RECOVERY_BLOCKED": "Recovery expansion is blocked",
            "RECOVERY_PENDING_EVIDENCE": "Recovery expansion is waiting on more evidence",
            "RECOVERY_UNDER_REVIEW": "Recovery qualification is under review",
            "RECOVERY_QUALIFIED": "Recovery qualification has passed but may still await execution",
            "RECOVERY_EXECUTED": "Recovery has been executed",
        }
        base = mapping.get(recovery_state, f"Recovery state is {recovery_state}")
        if blocking_reason:
            base = f"{base}; {blocking_reason}"
        return self._sentence(base)

    @staticmethod
    def _sentence(text: str) -> str:
        """Normalize text into one clean sentence."""
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            return "No concise rationale is available."
        if cleaned.endswith((".", "!", "?")):
            return cleaned
        return f"{cleaned}."
