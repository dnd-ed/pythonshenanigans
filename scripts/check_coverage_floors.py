#!/usr/bin/env python3
"""Enforce a minimum coverage percentage per module.

``--cov-fail-under`` only guards the *total*, which one large, well-covered
module can mask: a module could drop to zero and the total would barely move.
This reads coverage's JSON report and applies a floor to every file.

Usage::

    pytest --cov=pythonshenanigans --cov-report=json:coverage.json
    python scripts/check_coverage_floors.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

#: Minimum percent covered (lines+branches) required of every module.
FLOOR = 95.0

#: Files exempt from the floor, by basename.
EXEMPT: frozenset[str] = frozenset()

DEFAULT_REPORT = "coverage.json"


def main(argv: list[str]) -> int:
    report_path = Path(argv[0] if argv else DEFAULT_REPORT)
    if not report_path.exists():
        print(f"error: {report_path} not found - run pytest with --cov-report=json")
        return 1

    data = json.loads(report_path.read_text(encoding="utf-8"))
    failures: list[tuple[str, float]] = []

    for filename, report in sorted(data.get("files", {}).items()):
        name = Path(filename).name
        if name in EXEMPT:
            print(f"skip  {name} (exempt)")
            continue
        percent = float(report["summary"]["percent_covered"])
        ok = percent >= FLOOR
        print(f"{'ok' if ok else 'FAIL':5} {percent:6.2f}%  {name}")
        if not ok:
            failures.append((name, percent))

    if not failures:
        print(f"\nevery file meets the {FLOOR:.0f}% floor")
        return 0

    print(f"\nbelow the {FLOOR:.0f}% per-file floor:")
    for name, percent in failures:
        print(f"  {name}: {percent:.2f}%")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
