from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from ix_style.telemetry import MissionHealthBuilder
from ix_style.verification import (
    ScenarioRunner,
    build_power_fault_clamp_scenario,
)


def _serialize(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def main() -> None:
    scenario = build_power_fault_clamp_scenario()
    runner = ScenarioRunner()
    result = runner.run(scenario)
    snapshot = MissionHealthBuilder().build_from_verification(result)

    output = {
        "passed": result.passed,
        "failures": list(result.failures),
        "evidence_package": _serialize(asdict(result.evidence_package)),
        "mission_health_snapshot": snapshot,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
