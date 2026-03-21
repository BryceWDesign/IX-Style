from __future__ import annotations

from ix_style.verification import RepositorySelfAuditor


def test_repository_self_audit_passes() -> None:
    report = RepositorySelfAuditor().run()

    assert report.passed is True
    assert len(report.checks) >= 4
    assert all(check.passed for check in report.checks)
