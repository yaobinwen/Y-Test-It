import enum


class ConstraintResult(enum.IntEnum):
    # Discard the current test case because it doesn't meet the constraint.
    DISCARD = 1
    # Keep the current test case.
    KEEP = 2
