"""Standalone calibration-only v1.1.1 gate; the historical CLI is unchanged."""

from __future__ import annotations

import json
import sys

from .fixture_locks import FixtureLockError
from .structured_report_state import StructuredReportStateCalibrationError
from .structured_report_state_v1_1_1_calibration import (
    run_structured_report_state_v1_1_1_calibration,
)


def main() -> int:
    """Emit a complete summary only after every gate passes; fail closed otherwise."""
    if len(sys.argv) != 1:
        print("No fixture, hash bypass, or collection options are accepted.", file=sys.stderr)
        return 2
    try:
        summary = run_structured_report_state_v1_1_1_calibration()
    except (FixtureLockError, StructuredReportStateCalibrationError, OSError) as exc:
        print(f"v1.1.1 calibration failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
