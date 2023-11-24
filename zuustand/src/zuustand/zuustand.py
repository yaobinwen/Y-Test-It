#!/usr/bin/python3


import copy

from typing import List


from ytestit_common.constraints import ConstraintResult
from ytestit_common.types import (
    Type_PossibleValues,
    Type_VariableValues,
    Type_ConstraintFunction,
    Type_Constraints,
)


class TransitionBase(object):
    def __init__(self, changes):
        # Changes that cause this transition.
        self.changes = changes


class InTransition(TransitionBase):
    def __init__(self, source, changes):
        super().__init__(changes=changes)

        self.source = source

    def __str__(self):
        return f"<- {self.source.state}"

    def __repr__(self):
        return str(self)


class OutTransition(TransitionBase):
    def __init__(self, dest, changes):
        super().__init__(changes=changes)

        self.dest = dest

    def __str__(self):
        return f"-> {self.dest.state}"

    def __repr__(self):
        return str(self)


class Vertex(object):
    def __init__(self, vid: int, state):
        self.vid = vid
        self.state = state
        # The IDs of the graph that point to this vertex.
        self.ins = {}
        # The IDs of the graph that this vertex points to.
        self.outs = {}

    def add_in_trans(self, source, changes):
        self.ins[source.vid] = InTransition(source=source, changes=changes)

    def add_out_trans(self, dest, changes):
        self.outs[dest.vid] = OutTransition(dest=dest, changes=changes)


class ValueChange(object):
    def __init__(self, var, from_value, to_value):
        self.var = var
        self.from_value = from_value
        self.to_value = to_value


def compare_states(state_from, state_to):
    keys1 = set(state_from.keys())
    keys2 = set(state_to.keys())
    if keys1 != keys2:
        raise ValueError(f"'{state1}' and '{state2}' have different keys")

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


def zuustand(
    possible_states,
    constraints,
):
    next_vid = 1
    graph = {}

    for state in possible_states:
        v = Vertex(vid=next_vid, state=state)
        graph[v.vid] = v

        next_vid += 1

    vid_set = set(graph.keys())
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
                ret = cons_func(changed, unchanged)
                if ret == ConstraintResult.DISCARD:
                    discard = True
                    break
                else:
                    if ret != ConstraintResult.KEEP:
                        raise ValueError(f"constraint must return DISCARD or KEEP")

            if discard:
                continue

            # Keep the transition.
            src_v.add_out_trans(dest=dst_v, changes=changed)
            dst_v.add_in_trans(source=src_v, changes=changed)

    return graph


class SubGraph(object):
    def __init__(self, starting_vertex_id):
        self.starting_vertex_id = starting_vertex_id
        self.vertex_ids = set()


def _select_starting_vertex_id(candidates, unvisited):
    while candidates:
        cand = candidates.pop(0)
        if cand in unvisited:
            return cand
        else:
            # If `cand` has been visited, then we don't need to use as a
            # starting vertex anymore so we can just drop it.
            pass

    if unvisited:
        return unvisited.pop()

    raise ValueError(
        "no starting vertex candidate available "
        "(both 'candidates' and 'unvisited' are empty)"
    )


def partition_and_find_shortest_paths(
    graph,
    # List of vertex IDs. It should be a list so the order of the elements
    # can mean the precedence of consideration (i.e., the first element should
    # be considered as the first starting vertex).
    starting_candidates: List[int],
):
    unvisited_vertices = set(graph.keys())
    subgraphs = []

    # Shortest paths from starting vertices to all the other vertices in the
    # same subgraph.
    # structure:
    # starting_vertex_id -> {
    # Other vertex id: shortest path from starting vertex to this vertex
    # }
    shortest_paths = {}

    while unvisited_vertices:
        starting_vertex_id = _select_starting_vertex_id(
            candidates=starting_candidates,
            unvisited=unvisited_vertices,
        )

        g = SubGraph(starting_vertex_id=starting_vertex_id)

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
                unvisited_vertices -= set([curr_vid])

                curr_v = graph[curr_vid]
                for out_vid, out_v in curr_v.outs.items():
                    if out_vid not in unvisited_vertices:
                        # If the out vertex has been visited, skip it.
                        continue

                    next_vertex_id = out_vid
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
