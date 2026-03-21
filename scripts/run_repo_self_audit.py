from __future__ import annotations

import json
import sys

from ix_style.verification import RepositorySelfAuditor


def main() -> int:
    report = RepositorySelfAuditor().run()
    print(json.dumps(report.as_dict(), indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
