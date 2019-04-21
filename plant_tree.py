from tree import Node, Edge, Tree


class PlantEdge(Edge):
    controller_node = None

    def __init__(self, e_in: str, x: list, u: Node, v: Node, c_node: Node):
        super().__init__(e_in, x, u, v)
        self.controller_node = c_node


class PlantTree(Tree):
    def __init__(self):
        super().__init__()
        self.V = list()
        self.root = list()

    def add_edge(self, u: Node, v: Node, e_in: str, x: list, c_node=Node("", [], 0)) -> PlantEdge:
        new = PlantEdge(e_in, x, u, v, c_node)

        for e in self.E:
            if e.e_in == e_in and e.x == x and u == e.u and v == e.v and c_node == e.controller_node:
                return e

        self.E.append(new)
        return new

    def add_vertex(self, e_out: str, z: list, last=False) -> Node:
        new = Node(e_out, z, len(self.V), last=last)
        self.V.append(new)
        return new

    def __str__(self):
        sR = ""
        sV = ""
        sE = ""

        for r in self.root:
            sR += str(r) + "\n"

        for v in self.V:
            sV += str(v) + "\n"

        for e in self.E:
            sE += str(e) + "\n"

        return "roots:\n" + sR + "V:\n" + sV + "\nE:\n" + sE
