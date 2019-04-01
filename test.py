from trace_parser import build_from_names
from tree import to_tree
from controller_build import sat

tree = to_tree(build_from_names(["1", "2"], False))

print(str(tree))

print(str(sat(7, tree.v_to_tuple(), tree.e_to_tuple(), tree.e_in(), tree.e_out(), tree.g(), tree.z())))
