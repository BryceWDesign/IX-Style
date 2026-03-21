from __future__ import annotations

import json

from ix_style.verification import (
    InvariantChecker,
    ScenarioRunner,
    build_nav_spoof_transition_scenario,
    build_power_fault_clamp_scenario,
    build_recovery_deferred_scenario,
)


def _run_one(name: str, scenario) -> dict[str, object]:
    runner = ScenarioRunner()
    checker = InvariantChecker()

    result = runner.run(scenario)
    report = checker.evaluate(result)

    return {
        "name": name,
        "scenario_id": scenario.scenario_id,
        "scenario_passed": result.passed,
        "invariants_passed": report.passed,
        "final_outcome": result.evidence_package.decision_receipt["final_outcome"],
        "dominant_safety_posture": result.derived_dominant_safety_posture.value,
        "pipeline_trace": result.pipeline_trace,
        "invariant_report": report.as_dict(),
    }


def main() -> int:
    scenarios = (
        ("power_fault_clamp", build_power_fault_clamp_scenario()),
        ("nav_spoof_transition", build_nav_spoof_transition_scenario()),
        ("recovery_deferred", build_recovery_deferred_scenario()),
    )

    results = [_run_one(name, scenario) for name, scenario in scenarios]
    overall_pass = all(
        item["scenario_passed"] and item["invariants_passed"] for item in results
    )

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
