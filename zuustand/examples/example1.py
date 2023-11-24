#!/usr/bin/python3


from ytestit_common.constraints import ConstraintResult
from zuustand.zuustand import zuustand, partition_and_find_shortest_paths


POSSIBLE_STATES = [
    {"a": True, "b": 1},
    {"a": True, "b": 2},
    {"a": False, "b": 1},
    {"a": False, "b": 2},
]


def cons_change_only_one_var(changed, unchanged):
    return ConstraintResult.DISCARD if len(changed) != 1 else ConstraintResult.KEEP


CONSTRAINTS = {
    "cons_change_only_one_var": cons_change_only_one_var,
}


graph = zuustand(
    possible_states=POSSIBLE_STATES,
    constraints=CONSTRAINTS,
)


for vid, v in graph.items():
    print(f"vertex #{vid}:")
    for vid_out, v_out in v.outs.items():
        print(f"    -> vertex {vid_out}")


subgraphs, shortest_paths = partition_and_find_shortest_paths(
    graph=graph,
    starting_candidates=[1],
)

for sg in subgraphs:
    print(sg.vertex_ids)

for vid, sp in shortest_paths.items():
    print(vid, sp)
