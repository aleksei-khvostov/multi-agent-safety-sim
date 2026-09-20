"""Standalone disclosed-input v1.1.2 calibration; no holdout/collection options."""

from __future__ import annotations

import json
import sys

from .fixture_locks import FixtureLockError
from .structured_report_state import StructuredReportStateCalibrationError
from .structured_report_state_v1_1_2_calibration import (
    run_structured_report_state_v1_1_2_calibration,
)


def main() -> int:
    if len(sys.argv) != 1:
        print(
            "No fixture, hash bypass, holdout, or collection options are accepted.", file=sys.stderr
        )
        return 2
    try:
        summary = run_structured_report_state_v1_1_2_calibration()
    except (
        FixtureLockError,
        StructuredReportStateCalibrationError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"v1.1.2 calibration failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
