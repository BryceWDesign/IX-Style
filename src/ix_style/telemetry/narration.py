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
            return self._sentence(
                f"Command change type is {change_type}. {rationale}".strip()
            )

        return self._sentence(
            rationale or "Decision outcome is available in the evidence record"
        )

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


@dataclass(slots=True)
class SafetySummaryNarrator:
    """Builds compact operator-facing summaries from snapshots and receipts."""

    snapshot_builder: MissionHealthBuilder = field(default_factory=MissionHealthBuilder)
    formatter: OperatorRationaleFormatter = field(
        default_factory=OperatorRationaleFormatter
    )

    def summarize(
        self,
        *,
        snapshot: dict[str, Any],
        decision_receipt: dict[str, Any],
    ) -> OperatorSafetySummary:
        """Return a concise operator-facing summary."""
        headline = self._headline(snapshot)
        decision_rationale = self.formatter.decision_rationale(decision_receipt)
        operational_why = self._operational_why(snapshot)
        authority_statement = self.formatter.authority_statement(snapshot)
        recovery_statement = self.formatter.recovery_statement(snapshot)
        operator_focus = self._operator_focus(snapshot)
        timeline_markers = self._timeline_markers(snapshot)

        concise_narrative = " ".join(
            [
                headline,
                decision_rationale,
                operational_why,
                authority_statement,
                recovery_statement,
                operator_focus,
            ]
        ).strip()

        return OperatorSafetySummary(
            headline=headline,
            decision_rationale=decision_rationale,
            operational_why=operational_why,
            authority_statement=authority_statement,
            recovery_statement=recovery_statement,
            operator_focus=operator_focus,
            concise_narrative=concise_narrative,
            timeline_markers=timeline_markers,
            review_significance=str(snapshot.get("review_significance", "ROUTINE")),
        )

    def summarize_verification(self, result: "VerificationResult") -> OperatorSafetySummary:
        """Convenience wrapper for building a summary from a verification result."""
        snapshot = self.snapshot_builder.build_from_verification(result)
        return self.summarize(
            snapshot=snapshot,
            decision_receipt=result.evidence_package.decision_receipt,
        )

    @staticmethod
    def _headline(snapshot: dict[str, Any]) -> str:
        posture = str(snapshot.get("dominant_safety_posture", "NOMINAL"))
        mapping = {
            "SAFE_HOLD": "SAFE HOLD ACTIVE",
            "ASSURANCE_DEGRADED": "ASSURANCE DEGRADED",
            "POWER_DEGRADED": "POWER DEGRADED",
            "ACTUATION_DEGRADED": "ACTUATION DEGRADED",
            "NAV_DEGRADED": "NAVIGATION DEGRADED",
            "SENSOR_DEGRADED": "SENSOR DEGRADED",
            "COMMS_DEGRADED": "COMMUNICATIONS DEGRADED",
            "NOMINAL": "NOMINAL BOUNDED OPERATION",
            "INITIALIZING": "INITIALIZING",
        }
        return mapping.get(posture, posture.replace("_", " "))

    @staticmethod
    def _operational_why(snapshot: dict[str, Any]) -> str:
        trust_summary = snapshot.get("trust_summary", {})
        fault_summary = snapshot.get("active_fault_summary", {})
        resource_summary = snapshot.get("resource_summary", {})
        recent_events = snapshot.get("recent_events", [])

        parts: list[str] = []
        posture_driver = trust_summary.get("posture_driving_trust_domain")
        highest_fault = fault_summary.get("highest_active_fault_priority", "NONE")

        if posture_driver:
            parts.append(f"Posture is being driven by {posture_driver}.")
        if highest_fault != "NONE":
            parts.append(f"Highest active fault priority is {highest_fault}.")
        if resource_summary.get("survivability_bias_active"):
            parts.append("Survivability bias is active.")
        if not parts and recent_events:
            latest = SafetySummaryNarrator._best_recent_event_summary(recent_events)
            if latest:
                parts.append(latest)

        if not parts:
            parts.append("No stronger degradation driver is currently being summarized.")

        return " ".join(parts)

    @staticmethod
    def _operator_focus(snapshot: dict[str, Any]) -> str:
        posture = str(snapshot.get("dominant_safety_posture", "NOMINAL"))
        mapping = {
            "SAFE_HOLD": (
                "Do not resume mission progress until containment exit is explicitly qualified."
            ),
            "ASSURANCE_DEGRADED": (
                "Treat high-risk control paths as suspect until assurance health is restored."
            ),
            "POWER_DEGRADED": (
                "Preserve essential functions before attempting broader recovery."
            ),
            "ACTUATION_DEGRADED": (
                "Reduce maneuver aggressiveness until commanded effect is trustworthy."
            ),
            "NAV_DEGRADED": (
                "Avoid nav-dependent authority expansion until independent trust is restored."
            ),
            "SENSOR_DEGRADED": (
                "Cross-check critical sensing before widening autonomy."
            ),
            "COMMS_DEGRADED": (
                "Do not rely on weak or stale remote intent."
            ),
            "NOMINAL": (
                "Continue bounded operation and monitor for new trust or fault transitions."
            ),
            "INITIALIZING": (
                "Complete readiness checks before enabling broader authority."
            ),
        }
        return mapping.get(
            posture,
            "Continue bounded operation while monitoring for new posture drivers.",
        )

    @staticmethod
    def _timeline_markers(snapshot: dict[str, Any]) -> tuple[str, ...]:
        recent_events = snapshot.get("recent_events", [])
        scored = sorted(
            recent_events,
            key=lambda item: (
                _SIGNIFICANCE_ORDER.get(str(item.get("review_significance", "ROUTINE")), 0),
                str(item.get("event_time", "")),
            ),
            reverse=True,
        )
        summaries: list[str] = []
        for item in scored:
            summary = " ".join(str(item.get("summary", "")).split())
            if summary and summary not in summaries:
                summaries.append(summary)
            if len(summaries) == 3:
                break
        return tuple(summaries)

    @staticmethod
    def _best_recent_event_summary(recent_events: list[dict[str, Any]]) -> str:
        scored = sorted(
            recent_events,
            key=lambda item: (
                _SIGNIFICANCE_ORDER.get(str(item.get("review_significance", "ROUTINE")), 0),
                str(item.get("event_time", "")),
            ),
            reverse=True,
        )
        for item in scored:
            summary = " ".join(str(item.get("summary", "")).split())
            if summary:
                return summary if summary.endswith(".") else f"{summary}."
        return ""
