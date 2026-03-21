from __future__ import annotations

import json
from pathlib import Path

from ix_style.messages import EvidenceBundleBuilder
from ix_style.verification import (
    JsonArtifactIO,
    ReviewArtifactBuilder,
    ScenarioRunner,
    build_nav_spoof_transition_scenario,
    build_power_fault_clamp_scenario,
)


def _export_one(name: str, scenario_id: str, output_root: Path) -> dict[str, str]:
    runner = ScenarioRunner()
    scenario = (
        build_power_fault_clamp_scenario()
        if scenario_id == "power_fault_clamp"
        else build_nav_spoof_transition_scenario()
    )
    result = runner.run(scenario)

    package = ReviewArtifactBuilder().build(result)
    output_dir = output_root / name
    JsonArtifactIO().export_package(package, output_dir)

    bundle_errors = EvidenceBundleBuilder().validate(package.evidence_bundle)

    return {
        "name": name,
        "output_dir": str(output_dir),
        "passed": str(result.passed),
        "bundle_valid": str(not bundle_errors),
    }


def main() -> int:
    output_root = Path("artifacts") / "review_packages"
    output_root.mkdir(parents=True, exist_ok=True)

    exports = [
        _export_one("power_fault_clamp", "power_fault_clamp", output_root),
        _export_one("nav_spoof_transition", "nav_spoof_transition", output_root),
    ]

    print(json.dumps({"exports": exports}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
