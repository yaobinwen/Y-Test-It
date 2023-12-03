import copy
import enum

from itertools import product
from typing import List
from ytestit_common.types import (
    Type_PossibleValues,
    Type_VariableValues,
    Type_Constraints,
)


class Node(object):
    def __init__(self, value, state):
        self.value = value
        self.state = state
        self.children = []


class ConstraintResult(enum.IntEnum):
    # Discard the current test case because it doesn't meet the constraint.
    DISCARD = 1
    # Keep the current test case.
    KEEP = 2


def full_combinatorial(
    possible_values: Type_PossibleValues,
) -> List[Type_VariableValues]:
    if not possible_values:
        return []

    keys = possible_values.keys()
    values = possible_values.values()

    # Use itertools.product to generate all combinations
    all_combinations = list(product(*values))

    # Combine keys with corresponding values in each combination
    result = [dict(zip(keys, combination)) for combination in all_combinations]

    return result


def _grow_kombii_tree(
    possible_values: Type_PossibleValues,
    var_precedence: List[str],
    constraints: Type_Constraints,
) -> Node:
    ROOT = Node(value=None, state={})

    curr_queue = [ROOT]
    next_queue = []

    for v in var_precedence:
        for pv in possible_values[v]:
            for node in curr_queue:
                skip = False
                for name, cons in constraints.items():
                    ret = cons(var=v, value=pv, state=node.state)
                    if ret == ConstraintResult.DISCARD:
                        skip = True
                        break
                    else:
                        if ret != ConstraintResult.KEEP:
                            raise ValueError(
                                f"constraint '{name}' "
                                "must return 'ConstraintResult.DISCARD' "
                                "or 'ConstraintResult.KEEP' "
                                f"but actually returned '{ret}'"
                            )

                if skip:
                    continue

                child_state = copy.deepcopy(node.state)
                child_state.update({v: pv})
                child = Node(value=pv, state=child_state)
                node.children.append(child)
                next_queue.append(child)

        curr_queue = next_queue
        next_queue = []

    return ROOT


def _traverse_kombii_tree_recursive(
    node: Node, results: List[Type_VariableValues], var_num: int
) -> None:
    if node.children:
        for child in node.children:
            _traverse_kombii_tree_recursive(child, results, var_num)
    else:
        # This is a leaf node.

        if var_num == 0:
            # If the number of variables is zero, that means the inputs of
            # `_grow_kombii_tree` are all empty, so there won't be any valid
            # combinations of the variables, so we just return.
            return

        if len(node.state.keys()) != var_num:
            # If a leaf node doesn't include all the variables, that means
            # there are no valid test cases on this branch at all, and we
            # should skip this test case.
            # This could happen when the first few variables in the precedence
            # list can form a valid partial combination but the later variables
            # don't meet the constraints.
            return

        results.append(node.state)


def _traverse_kombii_tree(node: Node, var_num: int) -> List[Type_VariableValues]:
    if not isinstance(node, Node):
        raise TypeError(f"node must be 'Node' but is '{node.__class__.__name__}'")

    if var_num < 0:
        raise ValueError(f"number of variables must be >= 0 (actual: {var_num})")

    results = []
    _traverse_kombii_tree_recursive(node=node, results=results, var_num=var_num)

    return results


def conditional_combinatorial(
    possible_values: Type_PossibleValues,
    var_precedence: List[str],
    constraints: Type_Constraints,
) -> List[Type_VariableValues]:
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )

    results = _traverse_kombii_tree(node=root, var_num=len(var_precedence))

    return results
