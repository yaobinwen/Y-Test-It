from typing import Any, Callable, Dict, List
from ytestit_common.constraints import ConstraintResult


Type_PossibleValues = Dict[
    str,  # variable name
    List[Any],  # variable's all possible values
]


Type_VariableValues = Dict[
    str,  # variable name
    Any,  # variable value
]


Type_ConstraintFunction = Callable[
    # Constraint function input parameters
    [
        str,  # variable name
        Any,  # variable value
        Type_VariableValues,  # current values of the other variables.
    ],
    # Constraint function return type
    ConstraintResult,
]

Type_Constraints = Dict[
    str,  # constraint name
    Type_ConstraintFunction,  # constraint function
]
