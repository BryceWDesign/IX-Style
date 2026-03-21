from __future__ import annotations

import json
from pathlib import Path

from ix_style.verification import QuickstartRunner


def main() -> int:
    output_root = Path("artifacts") / "quickstart_review_packages"
    summary = QuickstartRunner().run(output_root)
    print(json.dumps(summary.as_dict(), indent=2))
    return 0 if summary.overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
