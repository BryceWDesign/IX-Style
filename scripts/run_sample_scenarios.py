from __future__ import annotations

import json
from typing import Any

from ix_style.messages import MISSION_HEALTH_SNAPSHOT_SCHEMA, SchemaValidator
from ix_style.telemetry import MissionHealthBuilder
from ix_style.verification import (
    ScenarioRunner,
    build_nav_spoof_transition_scenario,
    build_power_fault_clamp_scenario,
)


def _run_one(name: str, scenario: Any, validator: SchemaValidator) -> dict[str, Any]:
    runner = ScenarioRunner()
    snapshot_builder = MissionHealthBuilder()

    result = runner.run(scenario)
    snapshot = snapshot_builder.build_from_verification(result)
    schema_errors = validator.validate(MISSION_HEALTH_SNAPSHOT_SCHEMA, snapshot)

    return {
        "scenario_id": scenario.scenario_id,
        "name": name,
        "passed": result.passed and not schema_errors,
        "failures": list(result.failures),
        "schema_errors": list(schema_errors),
        "decision_outcome": result.evidence_package.decision_receipt["final_outcome"],
        "dominant_safety_posture": snapshot["dominant_safety_posture"],
        "review_significance": snapshot["review_significance"],
    }


def main() -> int:
    validator = SchemaValidator()
    scenarios = (
        ("power_fault_clamp", build_power_fault_clamp_scenario()),
        ("nav_spoof_transition", build_nav_spoof_transition_scenario()),
    )

    results = [_run_one(name, scenario, validator) for name, scenario in scenarios]
    overall_pass = all(item["passed"] for item in results)

    print(
        json.dumps(
            {
                "passed": overall_pass,
                "scenario_results": results,
            },
            indent=2,
        )
    )
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
