#!/usr/bin/python3


import copy

from typing import Any, Callable, Dict, List, Set, Tuple


from ytestit_common.constraints import ConstraintResult
from ytestit_common.types import (
    Type_VariableValues,
    Type_State,
)


class ValueChange(object):
    """Record the change of the variable's value."""

    def __init__(
        self,
        var: str,  # Variable's name
        from_value: Any,  # Variable's original value
        to_value: Any,  # Variable's new value
    ):
        self.var = var
        self.from_value = from_value
        self.to_value = to_value

    def __str__(self) -> str:
        return f"ValueChange(var={self.var} from={self.from_value} to={self.to_value})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ValueChange):
            return (self.var, self.from_value, self.to_value) == (
                other.var,
                other.from_value,
                other.to_value,
            )

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)


Type_ChangedValues = Dict[str, ValueChange]
Type_UnchangedValues = Type_VariableValues


def compare_states(
    state_from: Type_State,
    state_to: Type_State,
) -> Tuple[Type_ChangedValues, Type_UnchangedValues]:
    """Compare two states and return the changed states and unchanged states."""

    keys1 = set(state_from.keys())
    keys2 = set(state_to.keys())
    if keys1 != keys2:
        # NOTE(ywen): For now, we require `state_from` and `state_to` have the
        # same set of keys. In the future, we could support having a different
        # set of keys and figure out "added" and "removed".
        raise ValueError(f"'{state_from}' and '{state_to}' have different keys")

    changed = {}
    unchanged = {}
    for key in keys1:
        v_from = state_from[key]
        v_to = state_to[key]
        if v_from == v_to:
            unchanged[key] = v_from
        else:
            changed[key] = ValueChange(var=key, from_value=v_from, to_value=v_to)

    return changed, unchanged


class Vertex(object):
    """A vertex that contains the key information: its ID and the state that it
    represents.
    """

    def __init__(self, vid: int, state: Type_State):
        self.vid = vid
        self.state = state

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vertex):
            return (self.vid, self.state) == (other.vid, other.state)

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)


class TransitionBase(object):
    """Base class of a transition between two vertices."""

    def __init__(self, changes: Type_ChangedValues):
        # Changes that cause this transition.
        self.changes = changes

    def __str__(self):
        return f"TransitionBase(changes={self.changes})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TransitionBase):
            return self.changes == other.changes

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)


class InTransition(TransitionBase):
    """An "in" transition that describes the transition from another vertex to
    the vertex that owns this in-transition.
    """

    def __init__(self, source: Vertex, changes: Type_ChangedValues):
        super().__init__(changes=changes)

        self.source = source

    def __str__(self):
        return f"<- Vertex(vid={self.source.vid})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InTransition):
            return (self.source, self.changes) == (other.source, other.changes)

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)


class OutTransition(TransitionBase):
    """An "out" transition that describes the transition from the vertex that
    owns this out-transition to another vertex.
    """

    def __init__(self, dest: Vertex, changes: Type_ChangedValues):
        super().__init__(changes=changes)

        self.dest = dest

    def __str__(self):
        return f"-> Vertex(vid={self.dest.vid})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OutTransition):
            return (self.dest, self.changes) == (other.dest, other.changes)

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)


class VertexWithTransitions(Vertex):
    """A vertex as well as its in-/out-transitions to other vertices."""

    def __init__(self, vid: int, state: Type_State):
        super().__init__(vid=vid, state=state)

        # The IDs of the graph that point to this vertex.
        self.ins = {}
        # The IDs of the graph that this vertex points to.
        self.outs = {}

    def __str__(self):
        return f"VertexWithTransitions(vid={self.vid} state={self.state})"

    def __repr__(self):
        return str(self)

    def add_in_trans(self, source: Vertex, changes: Type_ChangedValues):
        self.ins[source.vid] = InTransition(source=source, changes=changes)

    def add_out_trans(self, dest: Vertex, changes: Type_ChangedValues):
        self.outs[dest.vid] = OutTransition(dest=dest, changes=changes)


# A state transition graph, including all the possible states. Note that this
# graph may not be fully connected and may (or may not) have isolated
# sub-graphs. (See class SubGraphWithStartingVertex.)
Type_Graph = Dict[
    # vertex ID
    int,
    VertexWithTransitions,
]


Type_ConstraintFunction = Callable[
    # Constraint function input parameters
    [
        VertexWithTransitions,  # source vertex
        VertexWithTransitions,  # destination vertex
        Type_ChangedValues,  # changed values
        Type_UnchangedValues,  # unchanged values
    ],
    # Constraint function return type
    ConstraintResult,
]

Type_Constraints = Dict[
    str,  # constraint name
    Type_ConstraintFunction,  # constraint function
]


def generate_transition_graph(
    possible_states: List[Type_State],
    constraints: Type_Constraints,
) -> Type_Graph:
    """Given the possible states and the constraints on the transitions,
    generate the graph of all the valid state transitions.
    """

    graph = {}

    # The vertex ID for the next vertex that's added to the graph. The vertex
    # IDs are unique only within the same graph.
    next_vid = 1

    # Initialize the graph. Because this graph is about all the valid state
    # transitions, it should surely include all the possible states (i.e., the
    # vertices), so we firstly add all the vertices into it. We use the class
    # `VertexWithTransitions` so we can add state transitions to the vertices
    # later.
    for state in possible_states:
        v = VertexWithTransitions(vid=next_vid, state=state)
        graph[v.vid] = v
        next_vid += 1

    vid_set = set(graph.keys())

    # We loop through the entire set of vertices in two levels. The vertices in
    # the outer loop are seen as the "sources"; the vertices in the inner loop
    # are seen as the "destinations". The transition from one source to each
    # destination is then examine to determine if it's a valid one (i.e., not
    # violating any constraints). If it is a valid one, the transition is then
    # added to the vertices.
    for src_vid in vid_set:
        for dst_vid in vid_set:
            src_v = graph[src_vid]
            dst_v = graph[dst_vid]

            changed, unchanged = compare_states(
                state_from=src_v.state,
                state_to=dst_v.state,
            )

            discard = False
            for cons_name, cons_func in constraints.items():
                ret = cons_func(
                    src_vertex=src_v,
                    dest_vertex=dst_v,
                    changed_values=changed,
                    unchanged_values=unchanged,
                )
                if ret == ConstraintResult.DISCARD:
                    discard = True
                    break
                else:
                    if ret != ConstraintResult.KEEP:
                        raise ValueError(
                            f"constraint '{cons_name}' "
                            "must return either 'ConstraintResult.DISCARD' "
                            "or 'ConstraintResult.KEEP' "
                            f"but actually returned '{ret}'"
                        )

            if discard:
                continue

            # Keep the transition.
            src_v.add_out_trans(dest=dst_v, changes=changed)
            dst_v.add_in_trans(source=src_v, changes=changed)

    return graph


class SubGraphWithStartingVertex(object):
    def __init__(self, starting_vertex_id: int):
        self.starting_vertex_id = starting_vertex_id

        # The IDs of the vertices that belong to this subgraph.
        self.vertex_ids = set()


def _remove_visited_candidates(candidates: List[int], unvisited: List[int]):
    unvisited_candidates = []
    for cand in candidates:
        if cand in unvisited:
            unvisited_candidates.append(cand)

    return unvisited_candidates


def _select_starting_vertex_id(candidates: List[int], unvisited: List[int]):
    """Among all the candidate starting vertices, select the next one that has
    not been visited yet as the next starting vertex in the current sub-graph.
    """
    if candidates:
        return candidates.pop(0)

    if unvisited:
        # We shouldn't call `pop(0)` here because that means we remove the
        # first element from `unvisited`, making it a "visited" vertex. But in
        # fact we won't count it as "visited" until we add it to the sub-graph.
        return unvisited[0]

    raise ValueError("no starting vertex candidate available")


def partition_and_find_shortest_paths(
    graph,
    # List of vertex IDs. It should be a list so the order of the elements
    # can mean the precedence of consideration (i.e., the first element should
    # be considered as the first starting vertex).
    starting_candidates: List[int],
):
    unvisited_vertices = list(graph.keys())
    subgraphs = []

    # Shortest paths from starting vertices to all the other vertices in the
    # same subgraph.
    # structure:
    # starting_vertex_id -> {
    # Other vertex id: shortest path from starting vertex to this vertex
    # }
    shortest_paths = {}

    while unvisited_vertices:
        starting_candidates = _remove_visited_candidates(
            candidates=starting_candidates,
            unvisited=unvisited_vertices,
        )

        # Figure out the next starting vertex.
        starting_vertex_id = _select_starting_vertex_id(
            candidates=starting_candidates,
            unvisited=unvisited_vertices,
        )

        g = SubGraphWithStartingVertex(starting_vertex_id=starting_vertex_id)

        curr_queue = [starting_vertex_id]
        next_queue = []

        shortest_paths[starting_vertex_id] = {
            # The shortest path from the starting vertex to itself is an empty
            # path because there is no any other vertex in the middle.
            starting_vertex_id: [starting_vertex_id]
        }

        while curr_queue:
            for curr_vid in curr_queue:
                g.vertex_ids.add(curr_vid)

                # Mark the vertex of curr_vid as visited.
                unvisited_vertices.remove(curr_vid)

                curr_v = graph[curr_vid]
                for out_vid, out_v in curr_v.outs.items():
                    if out_vid not in unvisited_vertices:
                        # If the out vertex has been visited, skip it.
                        continue

                    next_vertex_id = out_vid
                    if next_vertex_id not in next_queue:
                        next_queue.append(next_vertex_id)

                    # This assertion must hold because visiting curr_vid is a
                    # precondition of visiting its out-going vertices.
                    assert curr_vid in shortest_paths[starting_vertex_id]

                    shortest_path_to_curr_v = shortest_paths[starting_vertex_id][
                        curr_vid
                    ]
                    shortest_paths[starting_vertex_id][
                        out_vid
                    ] = shortest_path_to_curr_v + [out_vid]

            curr_queue = next_queue
            next_queue = []

        subgraphs.append(g)

    return subgraphs, shortest_paths


def _dfs_3373_recursive(graph, curr_vertex_id, paths, curr_path=None):
    if curr_path is None:
        curr_path = []

    curr_path.append(curr_vertex_id)
    curr_v = graph[curr_vertex_id]
    if curr_v.outs:
        while curr_v.outs:
            next_vid, trans = curr_v.outs.popitem()
            _dfs_3373_recursive(
                graph=graph, curr_vertex_id=next_vid, paths=paths, curr_path=curr_path
            )
    else:
        paths.append(copy.deepcopy(curr_path))
        curr_path.pop()  # This is critical: must pop the previous vertex.


def dfs_3373(graph, starting_vertex_id):
    paths = []
    _dfs_3373_recursive(graph, starting_vertex_id, paths)
    return paths


def find_all_edge_paths(graph, subgraphs, shortest_paths):
    graph_copy = copy.deepcopy(graph)

    all_paths = {}
    for sg in subgraphs:
        starting_vertex_id = sg.starting_vertex_id

        # Make sure starting_vertex is used first.
        vertex_ids = [starting_vertex_id] + list(
            sg.vertex_ids - set([starting_vertex_id])
        )

        paths = []
        for vid in vertex_ids:
            if not graph_copy[vid].outs:
                continue

            paths.extend(dfs_3373(graph=graph_copy, starting_vertex_id=vid))

        # Extend the head of the path so it starts with starting_vertex_id
        # TODO(ywen): Is this section really helpful?
        for index, path in enumerate(paths):
            vid = path[0]

            if vid == starting_vertex_id:
                continue

            shortest_path = shortest_paths[starting_vertex_id][vid]
            paths[index] = shortest_path + path

        # TODO(ywen): Merge the paths
        # Is this really necessary?

        all_paths[starting_vertex_id] = paths

    return all_paths
