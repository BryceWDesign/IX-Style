from __future__ import annotations

from pathlib import Path

from ix_style.messages import EvidenceBundleBuilder
from ix_style.verification import (
    JsonArtifactIO,
    ReviewArtifactBuilder,
    ScenarioRunner,
    build_power_fault_clamp_scenario,
)


def test_review_artifact_package_exports_and_imports_cleanly(tmp_path: Path) -> None:
    result = ScenarioRunner().run(build_power_fault_clamp_scenario())
    package = ReviewArtifactBuilder().build(result)

    output_dir = tmp_path / "review_package"
    JsonArtifactIO().export_package(package, output_dir)

    imported = JsonArtifactIO().import_package(output_dir)

    assert imported.manifest["scenario_id"] == "EXAMPLE-POWER-CLAMP-001"
    assert imported.manifest["final_outcome"] == "CLAMP"
    assert imported.mission_health_snapshot["dominant_safety_posture"] == "POWER_DEGRADED"
    assert imported.operator_safety_summary["headline"] == "POWER DEGRADED"
    assert EvidenceBundleBuilder().validate(imported.evidence_bundle) == ()


def test_review_artifact_package_writes_required_files(tmp_path: Path) -> None:
    result = ScenarioRunner().run(build_power_fault_clamp_scenario())
    package = ReviewArtifactBuilder().build(result)

    output_dir = tmp_path / "review_package_files"
    JsonArtifactIO().export_package(package, output_dir)

    required = {
        "manifest.json",
        "verification_result.json",
        "evidence_package.json",
        "decision_receipt.json",
        "mission_health_snapshot.json",
        "operator_safety_summary.json",
        "evidence_bundle.json",
    }

    present = {path.name for path in output_dir.iterdir() if path.is_file()}
    assert required.issubset(present)
