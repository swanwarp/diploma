from trace_parser import TraceList
from controller_build import sat_from_tree
from tree import Tree
from trace_parser import Trace


def run_trace(trace: Trace, tree: Tree) -> bool:
    current_state = tree.root
    trace.new_counter()

    while trace.check_counter():
        (current_ein, current_eout) = trace.next_event()
        edges = tree.edges_from(current_state)
        next_state = None

        for e in edges:
            if e.e_in == current_ein.name and e.x == current_ein.variables:
                next_state = e.v
                break

        if next_state is None:
            print("wrong state on edge " + str(current_ein) + " -> " + str(current_eout) + " of trace")
            print(trace)
            return False

        next_z = next_state.z
        if current_eout.variables != next_z:
            print("wrong out on edge " + str(current_ein) + " -> " + str(current_eout) + " of trace")
            print(next_z)
            print(current_state.i)
            print(trace)
            return False

        current_state = next_state

    return True


s = ["39"]

# for i in range(6, 7):
#     s.append(str(i))


traces = TraceList(s, "pnp-traces", False)

#print(traces)

tree = traces.build_tree()
tree.to_dot("tree1")

traces.new_counter()

# while traces.check_counter():
#     trace = traces.next_trace()
#     if not run_trace(trace, tree):
#         print()
#     else:
#         print("success")
#         print()

plant_traces = TraceList(s, "pnp-traces", True)

#print(plant_traces)

plant_tree = plant_traces.build_plant_tree([6, 7, 8]) # skip pp1, pp2, pp3
#print(plant_tree)
plant_tree.p_to_dot("ptree1")

#print(tree)

controller, plant = sat_from_tree(8, 0, len(plant_tree.z()), tree, plant_tree)

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

# traces.new_counter()
#
# while traces.check_counter():
#     trace = traces.next_trace()
#     if not controller.run_trace(trace):
#         print()
#     else:
#         #print("success")
#         print()
#
# plant_traces.new_counter()

if plant != None:
    while plant_traces.check_counter():
        trace = plant_traces.next_trace()
        if not plant.run_trace(trace, [6, 7, 8]):
            print()
        else:
            print("success")
            print()
