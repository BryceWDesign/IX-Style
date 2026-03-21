"""Executable onboarding and quickstart flow for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ix_style.messages import EvidenceBundleBuilder

from .invariants import InvariantChecker
from .reports import JsonArtifactIO, ReviewArtifactBuilder
from .repository_audit import RepositorySelfAuditor
from .runner import ScenarioRunner
from .sample_scenarios import (
    build_nav_spoof_transition_scenario,
    build_power_fault_clamp_scenario,
    build_recovery_deferred_scenario,
)


@dataclass(slots=True, frozen=True)
class QuickstartScenarioSummary:
    """Summary of one quickstart scenario execution."""

    name: str
    scenario_id: str
    scenario_passed: bool
    invariants_passed: bool
    bundle_valid: bool
    final_outcome: str
    dominant_safety_posture: str
    operator_headline: str
    exported_review_dir: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return {
            "name": self.name,
            "scenario_id": self.scenario_id,
            "scenario_passed": self.scenario_passed,
            "invariants_passed": self.invariants_passed,
            "bundle_valid": self.bundle_valid,
            "final_outcome": self.final_outcome,
            "dominant_safety_posture": self.dominant_safety_posture,
            "operator_headline": self.operator_headline,
            "exported_review_dir": self.exported_review_dir,
        }


@dataclass(slots=True, frozen=True)
class QuickstartRunSummary:
    """Aggregated quickstart execution summary."""

    overall_passed: bool
    audit_passed: bool
    audit_report: dict[str, Any]
    scenario_results: tuple[QuickstartScenarioSummary, ...]
    exported_root: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return {
            "overall_passed": self.overall_passed,
            "audit_passed": self.audit_passed,
            "audit_report": self.audit_report,
            "scenario_results": [item.as_dict() for item in self.scenario_results],
            "exported_root": self.exported_root,
        }


@dataclass(slots=True)
class QuickstartRunner:
    """Runs the baseline onboarding flow end-to-end."""

    self_auditor: RepositorySelfAuditor = field(default_factory=RepositorySelfAuditor)
    scenario_runner: ScenarioRunner = field(default_factory=ScenarioRunner)
    invariant_checker: InvariantChecker = field(default_factory=InvariantChecker)
    review_builder: ReviewArtifactBuilder = field(default_factory=ReviewArtifactBuilder)
    artifact_io: JsonArtifactIO = field(default_factory=JsonArtifactIO)
    bundle_builder: EvidenceBundleBuilder = field(default_factory=EvidenceBundleBuilder)

    def run(self, output_root: str | Path) -> QuickstartRunSummary:
        """Run the baseline onboarding flow and export review artifacts."""
        output_dir = Path(output_root)
        output_dir.mkdir(parents=True, exist_ok=True)

        audit_report = self.self_auditor.run()
        scenario_results: list[QuickstartScenarioSummary] = []

        scenarios = (
            ("power_fault_clamp", build_power_fault_clamp_scenario()),
            ("nav_spoof_transition", build_nav_spoof_transition_scenario()),
            ("recovery_deferred", build_recovery_deferred_scenario()),
        )

        for name, scenario in scenarios:
            result = self.scenario_runner.run(scenario)
            invariant_report = self.invariant_checker.evaluate(result)
            review_package = self.review_builder.build(result)

            export_dir = output_dir / name
            self.artifact_io.export_package(review_package, export_dir)

            bundle_errors = self.bundle_builder.validate(review_package.evidence_bundle)
            scenario_results.append(
                QuickstartScenarioSummary(
                    name=name,
                    scenario_id=scenario.scenario_id,
                    scenario_passed=result.passed,
                    invariants_passed=invariant_report.passed,
                    bundle_valid=not bundle_errors,
                    final_outcome=str(
                        review_package.decision_receipt["final_outcome"]
                    ),
                    dominant_safety_posture=str(
                        review_package.mission_health_snapshot["dominant_safety_posture"]
                    ),
                    operator_headline=str(
                        review_package.operator_safety_summary["headline"]
                    ),
                    exported_review_dir=str(export_dir),
                )
            )

        overall_passed = audit_report.passed and all(
            item.scenario_passed and item.invariants_passed and item.bundle_valid
            for item in scenario_results
        )

        return QuickstartRunSummary(
            overall_passed=overall_passed,
            audit_passed=audit_report.passed,
            audit_report=audit_report.as_dict(),
            scenario_results=tuple(scenario_results),
            exported_root=str(output_dir),
        )
