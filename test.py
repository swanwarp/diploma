from trace_parser import TraceList
from controller_build import sat_from_tree
from tree import Tree
from trace_parser import Trace
from predicate import Predicate

s = ["1"]

traces = TraceList(s, "pnp-traces")

tree, plant_tree = traces.build_trees([6, 7, 8])

#print(traces)

#tree = traces.build_tree()

tree.to_dot("tree1")

traces.new_counter()

plant_tree.p_to_dot("ptree1")

#print(tree)

controller, plant = sat_from_tree(10, 0, len(plant_tree.z()), tree, plant_tree)

# for C in range(6, 11):
#     controller, plant = sat_from_tree(C, 0, 0, tree, plant_tree)
#
#     if controller is not None:
#         for K in range(1, C + 1):
#             controller, plant = sat_from_tree(C, K, 0, tree, plant_tree)
#
#             if controller is not None:
#                 break
#
#         break

controller.to_dot("controller1")
plant.to_dot("plant1")

traces.new_counter()

while traces.check_counter():
    trace = traces.next_trace()
    if controller.run_trace(trace):
        print("success")

print()

traces.transform_all()

# plant_traces.new_counter()

if plant is not None:
    while traces.check_counter():
        trace = traces.next_trace()
        if plant.run_trace(trace, [6, 7, 8]):
            print("success")
