#!/usr/bin/python3


from ytestit_common.constraints import ConstraintResult
from zuustand.zuustand import (
    generate_transition_graph,
    partition_and_find_shortest_paths,
    find_all_edge_paths,
)


POSSIBLE_STATES = [
    {"a": 1},
    {"a": 2},
    {"a": 3},
    {"a": 4},
    {"a": 5},
]


def cons(src_vertex, dest_vertex, changed_values, unchanged_values):
    if unchanged_values:
        # No self-pointing edges.
        return ConstraintResult.DISCARD

    keep_cases = [
        (1, 2),
        (2, 3),
        (2, 4),
        (3, 1),
        (3, 2),
        (5, 3),
        (5, 4),
    ]

    c = changed_values["a"]
    for case in keep_cases:
        if c.from_value == case[0] and c.to_value == case[1]:
            return ConstraintResult.KEEP

    return ConstraintResult.DISCARD


CONSTRAINTS = {
    "cons": cons,
}


graph = generate_transition_graph(
    possible_states=POSSIBLE_STATES,
    constraints=CONSTRAINTS,
)


for vid, v in graph.items():
    print(f"vertex #{vid}:")
    for vid_out, v_out in v.outs.items():
        print(f"    -> vertex {vid_out}")


subgraphs, shortest_paths = partition_and_find_shortest_paths(
    graph=graph,
    starting_candidates=[2],
)

for sg in subgraphs:
    print(sg.vertex_ids)

for vid, sp in shortest_paths.items():
    print(vid, sp)

all_paths = find_all_edge_paths(
    graph=graph,
    subgraphs=subgraphs,
    shortest_paths=shortest_paths,
)

for starting_vertex_id, paths in all_paths.items():
    print(starting_vertex_id, paths)
