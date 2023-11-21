import unittest

from kombii.kombii import (
    Node,
    ConstraintResult,
    full_combinatorial,
    _grow_kombii_tree,
    _traverse_kombii_tree,
    conditional_combinatorial,
)
from unittest.mock import Mock, patch


class TestImport(unittest.TestCase):
    def test(self):
        import kombii.kombii


class TestNode(unittest.TestCase):
    def test___init__(self):
        n = Node(value=None, state=None)
        self.assertIsNone(n.value)
        self.assertIsNone(n.state)

        n = Node(value="a", state={"a": 1, "b": 2})
        self.assertEqual(n.value, "a")
        self.assertDictEqual(n.state, {"a": 1, "b": 2})


class Test_full_combinatorial(unittest.TestCase):
    def test_0_var(self):
        results = full_combinatorial(possible_values={})
        self.assertListEqual(results, [])

    def test_1_var_1_value(self):
        results = full_combinatorial(possible_values={"v1": [1]})
        self.assertListEqual(results, [{"v1": 1}])

    def test_1_var_2_values(self):
        results = full_combinatorial(possible_values={"v1": [2, 3]})
        self.assertListEqual(results, [{"v1": 2}, {"v1": 3}])

    def test_2_vars_1_value(self):
        results = full_combinatorial(possible_values={"v1": [4], "v2": [5]})
        self.assertListEqual(results, [{"v1": 4, "v2": 5}])

    def test_2_vars_2_values(self):
        results = full_combinatorial(possible_values={"v1": [6, 7], "v2": [8, 9]})
        self.assertListEqual(
            results,
            [
                {"v1": 6, "v2": 8},
                {"v1": 6, "v2": 9},
                {"v1": 7, "v2": 8},
                {"v1": 7, "v2": 9},
            ],
        )


def _grow_kombii_tree_0_var_0_value_0_cons():
    possible_values = {}
    var_precedence = []
    constraints = {}
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_1_var_1_value_0_cons():
    possible_values = {
        "v1": [1],
    }
    var_precedence = ["v1"]
    constraints = {}
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_1_var_2_values_0_cons():
    possible_values = {"v1": [2, 3]}
    var_precedence = ["v1"]
    constraints = {}
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_2_vars_1_value_0_cons():
    possible_values = {
        "v1": [4],
        "v2": [5],
    }
    var_precedence = ["v1", "v2"]
    constraints = {}
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_2_vars_2_values_0_cons_default_precedence():
    possible_values = {
        "v1": [6, 7],
        "v2": [8, 9],
    }
    var_precedence = ["v1", "v2"]
    constraints = {}
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_2_vars_2_values_0_cons_reverse_precedence():
    possible_values = {
        "v1": [6, 7],
        "v2": [8, 9],
    }
    var_precedence = ["v2", "v1"]
    constraints = {}
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_2_vars_1_cons_partial_branch():
    possible_values = {
        "v1": [10, 100],
        "v2": [12],
    }
    var_precedence = ["v1", "v2"]

    def cons_v2(var, value, state):
        if var != "v2":
            return ConstraintResult.KEEP

        if "v1" not in state:
            return ConstraintResult.KEEP

        v1_value = state["v1"]

        return ConstraintResult.DISCARD if v1_value >= 100 else ConstraintResult.KEEP

    constraints = {
        "cons_v2": cons_v2,
    }
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


def _grow_kombii_tree_2_vars_3_values_2_cons():
    possible_values = {
        "v1": [10, 11, 100],
        "v2": [12, 13, 14],
    }
    var_precedence = ["v2", "v1"]

    def cons_v1_lt_100(var, value, state):
        return (
            ConstraintResult.DISCARD
            if var == "v1" and value >= 100
            else ConstraintResult.KEEP
        )

    def cons_v2_ne_13_14(var, value, state):
        return (
            ConstraintResult.DISCARD
            if var == "v2" and (value == 13 or value == 14)
            else ConstraintResult.KEEP
        )

    constraints = {
        # Constraint #1: "v1"'s value must be < 100.
        "v1_lt_100": cons_v1_lt_100,
        # Constraint #2: "v2"'s value must not be 13 or 14.
        "v2_ne_13_14": cons_v2_ne_13_14,
    }
    root = _grow_kombii_tree(
        possible_values=possible_values,
        var_precedence=var_precedence,
        constraints=constraints,
    )
    return root


class Test_grow_kombii_tree(unittest.TestCase):
    def test_0_var_0_value_0_cons(self):
        """
        Test input:
        - 0 variable.
        - 0 possible value for each variable.
        - 0 constraint.
        """
        root = _grow_kombii_tree_0_var_0_value_0_cons()

        # `root` must not have any children.
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertListEqual(root.children, [])

    def test_1_var_1_value_0_cons(self):
        """
        Test input:
        - 1 variable.
        - 1 possible value for each variable.
        - 0 constraint.
        """
        root = _grow_kombii_tree_1_var_1_value_0_cons()

        # `root` must have exactly one child.
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 1)

        # The only child.
        child = root.children[0]
        self.assertEqual(child.value, 1)
        self.assertDictEqual(child.state, {"v1": 1})
        self.assertListEqual(child.children, [])

    def test_1_var_2_values_0_cons(self):
        """
        Test input:
        - 1 variable.
        - 2 possible values for each variable.
        - 0 constraint.
        """
        root = _grow_kombii_tree_1_var_2_values_0_cons()

        # `root` must have exactly two children.
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 2)

        # 1st child.
        c1 = root.children[0]
        self.assertEqual(c1.value, 2)
        self.assertDictEqual(c1.state, {"v1": 2})
        self.assertListEqual(c1.children, [])

        # 2nd child.
        c2 = root.children[1]
        self.assertEqual(c2.value, 3)
        self.assertDictEqual(c2.state, {"v1": 3})
        self.assertListEqual(c2.children, [])

    def test_2_vars_1_value_0_cons(self):
        """
        Test input:
        - 2 variables.
        - 1 possible value for each variable.
        - 0 constraint.
        """
        root = _grow_kombii_tree_2_vars_1_value_0_cons()

        # `root` must have exactly one child.
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 1)

        # root's only child.
        c1 = root.children[0]
        self.assertEqual(c1.value, 4)
        self.assertDictEqual(c1.state, {"v1": 4})
        self.assertEqual(len(c1.children), 1)

        # root's only child's child.
        c2 = c1.children[0]
        self.assertEqual(c2.value, 5)
        self.assertDictEqual(c2.state, {"v1": 4, "v2": 5})
        self.assertListEqual(c2.children, [])

    def test_2_vars_2_values_0_cons_default_precedence(self):
        """
        Test input:
        - 2 variables.
        - 2 possible values for each variable.
        - 0 constraint.
        - Variable precedence is the same as the natural precedence.
        """
        root = _grow_kombii_tree_2_vars_2_values_0_cons_default_precedence()

        # root has two children. Each child is one of "v1"'s possible values.
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 2)

        # root's child 1, which has two children for "v2"'s possible values.
        c1 = root.children[0]
        self.assertEqual(c1.value, 6)
        self.assertDictEqual(c1.state, {"v1": 6})
        self.assertEqual(len(c1.children), 2)

        # root's child 2, which has two children for "v2"'s possible values.
        c2 = root.children[1]
        self.assertEqual(c2.value, 7)
        self.assertDictEqual(c2.state, {"v1": 7})
        self.assertEqual(len(c2.children), 2)

        # child 1's child 1.
        c1_1 = c1.children[0]
        self.assertEqual(c1_1.value, 8)
        self.assertDictEqual(c1_1.state, {"v1": 6, "v2": 8})
        self.assertListEqual(c1_1.children, [])

        # child 1's child 2.
        c1_2 = c1.children[1]
        self.assertEqual(c1_2.value, 9)
        self.assertDictEqual(c1_2.state, {"v1": 6, "v2": 9})
        self.assertListEqual(c1_2.children, [])

        # child 2's child 1.
        c2_1 = c2.children[0]
        self.assertEqual(c2_1.value, 8)
        self.assertDictEqual(c2_1.state, {"v1": 7, "v2": 8})
        self.assertListEqual(c2_1.children, [])

        # child 2's child 2.
        c2_2 = c2.children[1]
        self.assertEqual(c2_2.value, 9)
        self.assertDictEqual(c2_2.state, {"v1": 7, "v2": 9})
        self.assertListEqual(c2_2.children, [])

    def test_2_vars_2_values_0_cons_reverse_precedence(self):
        """
        Test input:
        - 2 variables.
        - 2 possible values for each variable.
        - 0 constraint.
        - Variable precedence is different than the natural precedence.
        """
        root = _grow_kombii_tree_2_vars_2_values_0_cons_reverse_precedence()

        # root has two children. Each child is one of "v2"'s possible values.
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 2)

        # root's child 1, which has two children for "v1"'s possible values.
        c1 = root.children[0]
        self.assertEqual(c1.value, 8)
        self.assertDictEqual(c1.state, {"v2": 8})
        self.assertEqual(len(c1.children), 2)

        # root's child 2, which has two children for "v1"'s possible values.
        c2 = root.children[1]
        self.assertEqual(c2.value, 9)
        self.assertDictEqual(c2.state, {"v2": 9})
        self.assertEqual(len(c2.children), 2)

        # child 1's child 1.
        c1_1 = c1.children[0]
        self.assertEqual(c1_1.value, 6)
        self.assertDictEqual(c1_1.state, {"v1": 6, "v2": 8})
        self.assertListEqual(c1_1.children, [])

        # child 1's child 2.
        c1_2 = c1.children[1]
        self.assertEqual(c1_2.value, 7)
        self.assertDictEqual(c1_2.state, {"v1": 7, "v2": 8})
        self.assertListEqual(c1_2.children, [])

        # child 2's child 1.
        c2_1 = c2.children[0]
        self.assertEqual(c2_1.value, 6)
        self.assertDictEqual(c2_1.state, {"v1": 6, "v2": 9})
        self.assertListEqual(c2_1.children, [])

        # child 2's child 2.
        c2_2 = c2.children[1]
        self.assertEqual(c2_2.value, 7)
        self.assertDictEqual(c2_2.state, {"v1": 7, "v2": 9})
        self.assertListEqual(c2_2.children, [])

    def test_2_vars_1_cons_partial_branch(self):
        """
        Test input:
        - 2 variables.
        - 1 constraint that results in a partial branch.
        - Variable precedence is the same as the natural precedence.
        """
        root = _grow_kombii_tree_2_vars_1_cons_partial_branch()

        # root has two children for "v1".
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 2)

        # root's child 1.
        c1 = root.children[0]
        self.assertEqual(c1.value, 10)
        self.assertDictEqual(c1.state, {"v1": 10})
        self.assertEqual(len(c1.children), 1)

        # root's child 2 is a partial branch so it doesn't have any children.
        c2 = root.children[1]
        self.assertEqual(c2.value, 100)
        self.assertDictEqual(c2.state, {"v1": 100})
        self.assertListEqual(c2.children, [])

        # root's child 1's only child.
        c1_1 = c1.children[0]
        self.assertEqual(c1_1.value, 12)
        self.assertDictEqual(c1_1.state, {"v1": 10, "v2": 12})
        self.assertListEqual(c1_1.children, [])

    def test_2_vars_3_values_2_cons(self):
        """
        Test input:
        - 2 variables.
        - 3 possible values for each variable.
        - 2 constraints.
        - Variable precedence is different than the natural precedence.
        """
        root = _grow_kombii_tree_2_vars_3_values_2_cons()

        # root has exactly one child for "v2".
        self.assertIsNone(root.value)
        self.assertDictEqual(root.state, {})
        self.assertEqual(len(root.children), 1)

        # root's only child.
        c1 = root.children[0]
        self.assertEqual(c1.value, 12)
        self.assertDictEqual(c1.state, {"v2": 12})
        self.assertEqual(len(c1.children), 2)

        # root's child's child 1.
        c1_1 = c1.children[0]
        self.assertEqual(c1_1.value, 10)
        self.assertDictEqual(c1_1.state, {"v1": 10, "v2": 12})
        self.assertListEqual(c1_1.children, [])

        # root's child's child 2.
        c1_2 = c1.children[1]
        self.assertEqual(c1_2.value, 11)
        self.assertDictEqual(c1_2.state, {"v1": 11, "v2": 12})
        self.assertListEqual(c1_2.children, [])

    def test_invalid_constraint(self):
        possible_values = {
            "v1": [20, 21],
            "v2": [22, 23],
        }
        var_precedence = ["v1", "v2"]
        constraints = {
            "cons_invalid": lambda var, value, state: 12,
        }
        self.assertRaisesRegex(
            ValueError,
            r"constraint 'cons_invalid' must return .+ but actually returned '12'",
            _grow_kombii_tree,
            possible_values=possible_values,
            var_precedence=var_precedence,
            constraints=constraints,
        )


class Test_traverse_kombii_tree(unittest.TestCase):
    def test_0_var_0_value_0_cons(self):
        root = _grow_kombii_tree_0_var_0_value_0_cons()
        results = _traverse_kombii_tree(node=root, var_num=0)
        self.assertListEqual(results, [])

    def test_1_var_1_value_0_cons(self):
        root = _grow_kombii_tree_1_var_1_value_0_cons()
        results = _traverse_kombii_tree(node=root, var_num=1)
        self.assertListEqual(results, [{"v1": 1}])

    def test_1_var_2_values_0_cons(self):
        root = _grow_kombii_tree_1_var_2_values_0_cons()
        results = _traverse_kombii_tree(node=root, var_num=1)
        self.assertListEqual(results, [{"v1": 2}, {"v1": 3}])

    def test_2_vars_1_value_0_cons(self):
        root = _grow_kombii_tree_2_vars_1_value_0_cons()
        results = _traverse_kombii_tree(node=root, var_num=2)
        self.assertListEqual(results, [{"v1": 4, "v2": 5}])

    def test_2_vars_2_values_0_cons_default_precedence(self):
        root = _grow_kombii_tree_2_vars_2_values_0_cons_default_precedence()
        results = _traverse_kombii_tree(node=root, var_num=2)
        self.assertListEqual(
            results,
            [
                {"v1": 6, "v2": 8},
                {"v1": 6, "v2": 9},
                {"v1": 7, "v2": 8},
                {"v1": 7, "v2": 9},
            ],
        )

    def test_2_vars_2_values_0_cons_reverse_precedence(self):
        root = _grow_kombii_tree_2_vars_2_values_0_cons_reverse_precedence()
        results = _traverse_kombii_tree(node=root, var_num=2)
        self.assertListEqual(
            results,
            [
                {"v1": 6, "v2": 8},
                {"v1": 7, "v2": 8},
                {"v1": 6, "v2": 9},
                {"v1": 7, "v2": 9},
            ],
        )

    def test_2_vars_1_cons_partial_branch(self):
        root = _grow_kombii_tree_2_vars_1_cons_partial_branch()
        results = _traverse_kombii_tree(node=root, var_num=2)
        self.assertListEqual(results, [{"v1": 10, "v2": 12}])

    def test_2_vars_3_values_2_cons(self):
        root = _grow_kombii_tree_2_vars_3_values_2_cons()
        results = _traverse_kombii_tree(node=root, var_num=2)
        self.assertListEqual(results, [{"v1": 10, "v2": 12}, {"v1": 11, "v2": 12}])

    def test_invalid_node_type(self):
        self.assertRaisesRegex(
            TypeError,
            "node must be 'Node' but is 'NoneType'",
            _traverse_kombii_tree,
            node=None,
            var_num=1,
        )

        self.assertRaisesRegex(
            TypeError,
            "node must be 'Node' but is 'int'",
            _traverse_kombii_tree,
            node=12,
            var_num=1,
        )

    def test_invalid_var_num(self):
        self.assertRaisesRegex(
            ValueError,
            "number of variables must be >= 0 \(actual: -1\)",
            _traverse_kombii_tree,
            node=Node(value=None, state={}),
            var_num=-1,
        )


class Test_conditional_combinatorial(unittest.TestCase):
    @patch(target="kombii.kombii._grow_kombii_tree")
    @patch(target="kombii.kombii._traverse_kombii_tree")
    def test_valid_args(self, mock_traverse_kombii_tree, mock_grow_kombii_tree):
        conditional_combinatorial(
            possible_values={},
            var_precedence=[],
            constraints={},
        )

        mock_grow_kombii_tree.assert_called_once_with(
            possible_values={},
            var_precedence=[],
            constraints={},
        )

        mock_traverse_kombii_tree.assert_called_once_with(
            node=mock_grow_kombii_tree.return_value,
            var_num=len([]),
        )


if __name__ == "__main__":
    unittest.main()
