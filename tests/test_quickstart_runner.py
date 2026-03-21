from __future__ import annotations

from pathlib import Path

from ix_style.verification import QuickstartRunner


def test_quickstart_runner_executes_and_exports_review_packages(tmp_path: Path) -> None:
    output_root = tmp_path / "quickstart_packages"
    summary = QuickstartRunner().run(output_root)

    assert summary.audit_passed is True
    assert summary.overall_passed is True
    assert len(summary.scenario_results) == 3

    exported_dirs = {Path(item.exported_review_dir).name for item in summary.scenario_results}
    assert exported_dirs == {
        "power_fault_clamp",
        "nav_spoof_transition",
        "recovery_deferred",
    }

    for item in summary.scenario_results:
        assert item.scenario_passed is True
        assert item.invariants_passed is True
        assert item.bundle_valid is True
        assert Path(item.exported_review_dir).is_dir()
