import unittest

from unittest.mock import Mock
from zuustand.zuustand import (
    ValueChange,
    compare_states,
    Vertex,
    TransitionBase,
    InTransition,
    OutTransition,
    VertexWithTransitions,
    generate_transition_graph,
)


class TestImport(unittest.TestCase):
    def test(self):
        import zuustand.zuustand


class TestValueChange(unittest.TestCase):
    def test___init__(self):
        c = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        self.assertEqual(c.var, "A")
        self.assertListEqual(c.from_value, [1])
        self.assertListEqual(c.to_value, [1, 2])

    def test___str__(self):
        c = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        c_str = str(c)
        self.assertEqual(c_str, "ValueChange(var=A from=[1] to=[1, 2])")

    def test___repr__(self):
        c = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        c_str = repr(c)
        self.assertEqual(c_str, "ValueChange(var=A from=[1] to=[1, 2])")

    def test___eq__(self):
        c1 = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        c2 = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        self.assertEqual(c1, c2)

    def test___eq__different_type(self):
        c1 = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        c2 = {"hello": "world"}
        self.assertNotEqual(c1, c2)

    def test___ne__(self):
        c1 = ValueChange(var="A", from_value=[1], to_value=[1, 2])
        c2 = ValueChange(var="A", from_value=[1], to_value=[1, 3])
        self.assertNotEqual(c1, c2)


class Test_compare_states(unittest.TestCase):
    def test_error_different_keys(self):
        state_from = {
            "A": 1,
            "B": 2,
        }
        state_to = {"A": 1, "B": 2, "C": 3}
        self.assertRaisesRegex(
            ValueError,
            ".* have different keys",
            compare_states,
            state_from=state_from,
            state_to=state_to,
        )

    def test_none_changed(self):
        state_from = {"A": 1, "B": 2, "C": 3}
        state_to = {"A": 1, "B": 2, "C": 3}
        changed, unchanged = compare_states(state_from=state_from, state_to=state_to)
        self.assertDictEqual(changed, {})
        self.assertDictEqual(unchanged, {"A": 1, "B": 2, "C": 3})

    def test_some_changed(self):
        state_from = {"A": 1, "B": 2, "C": 3}
        state_to = {"A": 1, "B": 20, "C": 3}
        changed, unchanged = compare_states(state_from=state_from, state_to=state_to)
        self.assertDictEqual(
            changed, {"B": ValueChange(var="B", from_value=2, to_value=20)}
        )
        self.assertDictEqual(unchanged, {"A": 1, "C": 3})

    def test_all_changed(self):
        state_from = {"A": 1, "B": 2, "C": 3}
        state_to = {"A": 10, "B": 20, "C": 30}
        changed, unchanged = compare_states(state_from=state_from, state_to=state_to)
        self.assertDictEqual(
            changed,
            {
                "A": ValueChange(var="A", from_value=1, to_value=10),
                "B": ValueChange(var="B", from_value=2, to_value=20),
                "C": ValueChange(var="C", from_value=3, to_value=30),
            },
        )
        self.assertDictEqual(unchanged, {})


class TestVertex(unittest.TestCase):
    def test___init__(self):
        v = Vertex(vid=19, state={"A": 1, "B": 2})
        self.assertEqual(v.vid, 19)
        self.assertDictEqual(v.state, {"A": 1, "B": 2})

    def test___eq__(self):
        v1 = Vertex(vid=19, state={"A": 1, "B": 2})
        v2 = Vertex(vid=19, state={"A": 1, "B": 2})
        self.assertEqual(v1, v2)

    def test___eq__different_type(self):
        v1 = Vertex(vid=19, state={"A": 1, "B": 2})
        v2 = 17
        self.assertNotEqual(v1, v2)

    def test___ne__(self):
        v1 = Vertex(vid=19, state={"A": 1, "B": 2})
        v2 = Vertex(vid=19, state={"A": 11, "B": 2})
        self.assertNotEqual(v1, v2)


class TestTransitionBase(unittest.TestCase):
    def test__init__(self):
        for changes in [None, 1, "a"]:
            b = TransitionBase(changes=changes)
            self.assertEqual(b.changes, changes)

    def test___str__(self):
        tb = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)}
        )
        self.assertEqual(
            str(tb), "TransitionBase(changes={'A': ValueChange(var=A from=2 to=1)})"
        )

    def test___repr__(self):
        tb = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)}
        )
        self.assertEqual(
            repr(tb), "TransitionBase(changes={'A': ValueChange(var=A from=2 to=1)})"
        )

    def test___eq__(self):
        tb1 = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)}
        )
        tb2 = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)}
        )
        self.assertEqual(tb1, tb2)

    def test___eq__different_type(self):
        tb1 = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)}
        )
        tb2 = 77
        self.assertNotEqual(tb1, tb2)

    def test___ne__(self):
        tb1 = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=12)}
        )
        tb2 = TransitionBase(
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)}
        )
        self.assertNotEqual(tb1, tb2)


class TestInTransition(unittest.TestCase):
    def test___init__(self):
        t = InTransition(source=Mock(state=1), changes={})
        self.assertEqual(t.source.state, 1)
        self.assertDictEqual(t.changes, {})

    def test___str__(self):
        t = InTransition(source=Mock(vid=10), changes={})
        self.assertEqual(str(t), "<- Vertex(vid=10)")

    def test___repr__(self):
        t = InTransition(source=Mock(vid=10), changes={})
        self.assertEqual(repr(t), "<- Vertex(vid=10)")

    def test___eq__(self):
        t1 = InTransition(
            source=Vertex(vid=3, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        t2 = InTransition(
            source=Vertex(vid=3, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        self.assertEqual(t1, t2)

    def test___eq__different_type(self):
        t1 = InTransition(
            source=Vertex(vid=3, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        t2 = 29
        self.assertNotEqual(t1, t2)

    def test___ne__(self):
        t1 = InTransition(
            source=Vertex(vid=4, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        t2 = InTransition(
            source=Vertex(vid=5, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        self.assertNotEqual(t1, t2)


class TestOutTransition(unittest.TestCase):
    def test___init__(self):
        t = OutTransition(dest=Mock(state=3), changes={})
        self.assertEqual(t.dest.state, 3)
        self.assertDictEqual(t.changes, {})

    def test___str__(self):
        t = OutTransition(dest=Mock(vid=19), changes={})
        self.assertEqual(str(t), "-> Vertex(vid=19)")

    def test___repr__(self):
        t = OutTransition(dest=Mock(vid=19), changes={})
        self.assertEqual(repr(t), "-> Vertex(vid=19)")

    def test___eq__(self):
        t1 = OutTransition(
            dest=Vertex(vid=4, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        t2 = OutTransition(
            dest=Vertex(vid=4, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        self.assertEqual(t1, t2)

    def test___eq__different_type(self):
        t1 = OutTransition(
            dest=Vertex(vid=4, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        t2 = 21
        self.assertNotEqual(t1, t2)

    def test___ne__(self):
        t1 = OutTransition(
            dest=Vertex(vid=5, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        t2 = OutTransition(
            dest=Vertex(vid=6, state={}),
            changes={"A": ValueChange(var="A", from_value=2, to_value=1)},
        )
        self.assertNotEqual(t1, t2)


class TestVertexWithTransitions(unittest.TestCase):
    def test___init__(self):
        vt = VertexWithTransitions(vid=23, state={"A": 1})
        self.assertEqual(vt.vid, 23)
        self.assertDictEqual(vt.state, {"A": 1})
        self.assertDictEqual(vt.ins, {})
        self.assertDictEqual(vt.outs, {})

    def test___str__(self):
        vt = VertexWithTransitions(vid=24, state={"A": 1})
        self.assertEqual(str(vt), "VertexWithTransitions(vid=24 state={'A': 1})")

    def test___repr__(self):
        vt = VertexWithTransitions(vid=24, state={"A": 1})
        self.assertEqual(repr(vt), "VertexWithTransitions(vid=24 state={'A': 1})")

    def test_add_in_trans(self):
        vt = VertexWithTransitions(vid=23, state={"A": 1})

        source = Vertex(vid=12, state={"A": 2})
        changed, _ = compare_states(state_from=source.state, state_to=vt.state)
        vt.add_in_trans(source=source, changes=changed)

        in_trans = InTransition(source=source, changes=changed)
        self.assertDictEqual(vt.ins, {source.vid: in_trans})

    def test_add_out_trans(self):
        vt = VertexWithTransitions(vid=8, state={"B": 2})

        dest = Vertex(vid=9, state={"B": 1})
        changed, _ = compare_states(state_from=vt.state, state_to=dest.state)
        vt.add_out_trans(dest=dest, changes=changed)

        out_trans = OutTransition(dest=dest, changes=changed)
        self.assertDictEqual(vt.outs, {dest.vid: out_trans})


class Test_generate_transition_graph_0_constraints(unittest.TestCase):
    def test_0_state(self):
        g = generate_transition_graph(
            possible_states=[],
            constraints={},
        )
        self.assertDictEqual(g, {})

    def test_1_state(self):
        g = generate_transition_graph(
            possible_states=[{"A": 10}],
            constraints={},
        )

        vid1 = 1
        self.assertDictEqual(g, {vid1: VertexWithTransitions(vid=1, state={"A": 10})})

        vt1 = g[vid1]

        # Vertex 1 has only one in-transition.
        self.assertEqual(len(vt1.ins), 1)
        # This only in-transition is from itself to itself.
        self.assertIn(vid1, vt1.ins)

        # Similarly, vertex 1 has only one out-transition.
        self.assertEqual(len(vt1.outs), 1)
        # This only out-transition is from itself to itself.
        self.assertIn(vid1, vt1.outs)

    def test_2_states(self):
        g = generate_transition_graph(
            possible_states=[{"A": 10}, {"A": 20}],
            constraints={},
        )

        vid1 = 1
        vid2 = 2
        self.assertDictEqual(
            g,
            {
                vid1: VertexWithTransitions(vid=1, state={"A": 10}),
                vid2: VertexWithTransitions(vid=2, state={"A": 20}),
            },
        )

        # "vt" means "vertex with transitions"
        vt1 = g[vid1]

        # Vertex 1 has two in-transition.
        self.assertEqual(len(vt1.ins), 2)
        # The first in-transition is from itself to itself.
        self.assertIn(vid1, vt1.ins)
        # The second in-transition is from vertex 2 to vertex 1.
        self.assertIn(vid2, vt1.ins)

        # Similarly, vertex 2 has two out-transition.
        self.assertEqual(len(vt1.outs), 2)
        # The first out-transition is from itself to itself.
        self.assertIn(vid1, vt1.outs)
        # The second out-transition is from vertex 1 to vertex 2.
        self.assertIn(vid2, vt1.outs)


if __name__ == "__main__":
    unittest.main()
