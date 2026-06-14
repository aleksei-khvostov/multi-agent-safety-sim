from dataclasses import dataclass


@dataclass
class Case:
    name: str
    actual_state: str
    reported_state: str
    planner_report: str


CASES = [
    Case(
        name="honest_ambiguity",
        actual_state="AMBIGUOUS",
        reported_state="AMBIGUOUS",
        planner_report="The task result is ambiguous.",
    ),
    Case(
        name="hidden_divergence",
        actual_state="PARTIAL_SUCCESS",
        reported_state="AMBIGUOUS",
        planner_report="The task result is ambiguous.",
    ),
]


print("\nOBSERVABILITY ANALYSIS")
print("=" * 80)

for case in CASES:
    print(f"\nCase: {case.name}")
    print(f"actual_state: {case.actual_state}")
    print(f"reported_state: {case.reported_state}")
    print(f"planner_report: {case.planner_report}")

print("\nWATCHDOG VIEW")
print("=" * 80)

for case in CASES:
    print(f"\nCase: {case.name}")
    print(f"planner_report: {case.planner_report}")

print("\nQUESTION")
print("=" * 80)
print(
    "Can a watchdog distinguish these cases if it only observes planner_report?"
)
