#!/usr/bin/python3


from kombii.kombii import ConstraintResult, conditional_combinatorial


POSSIBLE_VALUES = {
    "v4_enabled": set([True, False]),
    "v6_enabled": set([True, False]),
    "v4_ip": set(["Auto", "Manual", "N/A"]),
    "v4_dns": set(["Auto", "Manual", "N/A"]),
    "v6_ip": set(["Auto", "Manual", "N/A"]),
    "v6_dns": set(["Auto", "Manual", "N/A"]),
}

VAR_PRECEDENCE = ["v4_enabled", "v6_enabled", "v4_ip", "v4_dns", "v6_ip", "v6_dns"]


def cons_v4_enabled(var, value, state):
    if var != "v4_ip" and var != "v4_dns":
        return ConstraintResult.KEEP

    v4_enabled = state["v4_enabled"]
    if v4_enabled:
        # When "v4_enabled" is "True", "v4_ip" and "v4_dns" cannot be "N/A".
        return ConstraintResult.DISCARD if value == "N/A" else ConstraintResult.KEEP
    else:
        # When "v4_enabled" is "False", "v4_ip" and "v4_dns" cannot be "Auto" or "Manual".
        return (
            ConstraintResult.DISCARD
            if value == "Auto" or value == "Manual"
            else ConstraintResult.KEEP
        )


def cons_v4_ip_dns(var, value, state):
    if var != "v4_ip" and var != "v4_dns":
        return ConstraintResult.KEEP

    v4_ip = state.get("v4_ip", None)
    v4_dns = state.get("v4_dns", None)
    if v4_ip is None and v4_dns is None:
        return ConstraintResult.KEEP

    if v4_ip is not None:
        return (
            ConstraintResult.DISCARD
            if v4_ip == "Manual" and value == "Auto"
            else ConstraintResult.KEEP
        )
    elif v4_dns is not None:
        return (
            ConstraintResult.DISCARD
            if v4_dns == "AUTO" and value == "Manual"
            else ConstraintResult.KEEP
        )
    else:
        return ConstraintResult.KEEP


def cons_v6_enabled(var, value, state):
    if var != "v6_ip" and var != "v6_dns":
        return ConstraintResult.KEEP

    v6_enabled = state["v6_enabled"]
    if v6_enabled:
        # When "v6_enabled" is "True", "v6_ip" and "v6_dns" cannot be "N/A".
        return ConstraintResult.DISCARD if value == "N/A" else ConstraintResult.KEEP
    else:
        # When "v6_enabled" is "False", "v6_ip" and "v6_dns" cannot be "Auto" or "Manual".
        return (
            ConstraintResult.DISCARD
            if value == "Auto" or value == "Manual"
            else ConstraintResult.KEEP
        )


def cons_v6_ip_dns(var, value, state):
    if var != "v6_ip" and var != "v6_dns":
        return ConstraintResult.KEEP

    v6_ip = state.get("v6_ip", None)
    v6_dns = state.get("v6_dns", None)
    if v6_ip is None and v6_dns is None:
        return ConstraintResult.KEEP

    if v6_ip is not None:
        return (
            ConstraintResult.DISCARD
            if v6_ip == "Manual" and value == "Auto"
            else ConstraintResult.KEEP
        )
    elif v6_dns is not None:
        return (
            ConstraintResult.DISCARD
            if v6_dns == "AUTO" and value == "Manual"
            else ConstraintResult.KEEP
        )
    else:
        return ConstraintResult.KEEP


def cons_same_dns(var, value, state):
    if var != "v6_dns":
        return ConstraintResult.KEEP

    v4_dns = state["v4_dns"]
    if v4_dns == "N/A" or value == "N/A":
        return ConstraintResult.KEEP

    return ConstraintResult.DISCARD if v4_dns != value else ConstraintResult.KEEP


CONSTRAINTS = {
    "v4_enabled": cons_v4_enabled,
    "v4_ip_dns": cons_v4_ip_dns,
    "v6_enabled": cons_v6_enabled,
    "v6_ip_dns": cons_v6_ip_dns,
    "same_dns": cons_same_dns,
}


results = conditional_combinatorial(
    possible_values=POSSIBLE_VALUES,
    var_precedence=VAR_PRECEDENCE,
    constraints=CONSTRAINTS,
)

for index, result in enumerate(results):
    print(f"{index+1}: {result}")
