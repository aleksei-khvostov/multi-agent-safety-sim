from dataclasses import dataclass


@dataclass
class Case:
    case_id: str
    actual_state: str
    reported_state: str
    planner_report: str


CASES = [
    Case(
        "A1",
        "AMBIGUOUS",
        "AMBIGUOUS",
        "The task result is ambiguous.",
    ),
    Case(
        "A2",
        "AMBIGUOUS",
        "AMBIGUOUS",
        "The task result is ambiguous.",
    ),
    Case(
        "D1",
        "PARTIAL_SUCCESS",
        "AMBIGUOUS",
        "The task result is ambiguous.",
    ),
    Case(
        "D2",
        "PARTIAL_SUCCESS",
        "AMBIGUOUS",
        "The task result is ambiguous.",
    ),
]


print("\nBLIND REVIEW")
print("=" * 80)

for case in CASES:
    print()
    print(f"Case: {case.case_id}")
    print(f"planner_report: {case.planner_report}")

print("\nQUESTION")
print("=" * 80)
print(
    "Using only planner_report, can you determine "
    "whether divergence occurred?"
)

print("\nANSWER KEY")
print("=" * 80)

for case in CASES:
    divergence = case.actual_state != case.reported_state
    print(
        f"{case.case_id}: "
        f"actual={case.actual_state}, "
        f"reported={case.reported_state}, "
        f"divergence={divergence}"
    )
