from __future__ import annotations

from ix_style.messages import EvidenceBundleBuilder
from ix_style.verification import ScenarioRunner, build_power_fault_clamp_scenario


def test_runner_emits_valid_tamper_evident_evidence_bundle() -> None:
    runner = ScenarioRunner()
    result = runner.run(build_power_fault_clamp_scenario())

    bundle = result.evidence_package.evidence_bundle
    errors = EvidenceBundleBuilder().validate(bundle)

    assert result.passed is True
    assert bundle["scenario_id"] == "EXAMPLE-POWER-CLAMP-001"
    assert errors == ()
    assert bundle["integrity"]["item_count"] >= 2
