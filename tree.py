class Node:
    i = None
    e_out = None
    z = None

    def __init__(self, e_out: str, z: tuple, i: int):
        self.e_out = e_out
        self.z = z
        self.i = i

    def __hash__(self):
        return (self.e_out, self.z, self.i).__hash__()

    def __eq__(self, other):
        return self.e_out == other.e_out and self.z == other.z and other.i == self.i

    def __str__(self):
        return "out: " + self.e_out + " || z: " + str(self.z) + " || i: " + str(self.i)


class Edge:
    e_in = None
    x = None
    u = None
    v = None

    def __init__(self, e_in: str, x: tuple, u: Node, v: Node):
        self.e_in = e_in
        self.x = x
        self.u = u
        self.v = v

    def __hash__(self):
        return (self.e_in, self.x, self.u, self.v).__hash__()

    def __eq__(self, other):
        return self.e_in == other.e_in and self.x == other.x and self.u == other.u and self.v == other.v

    def __str__(self):
        return "in: " + self.e_in + " || x: " + str(self.x) + " || from: {" + str(self.u) + "} || to: {" + str(self.v) + "}"


class Tree:
    V = list()
    E = set()

    def __init__(self):
        E = set()
        V = list()

    def add_edge(self, u: Node, v: Node, e_in: str, x: tuple) -> Edge:
        new = Edge(e_in, x, u, v)
        self.E.add(new)
        return new

    def add_vertex(self, e_out: str, z: tuple) -> Node:
        new = Node(e_out, z, len(self.V))
        self.V.append(new)
        return new

    def e_to_tuple(self) -> tuple:
        return tuple(self.E)

    def v_to_tuple(self) -> tuple:
        return tuple(self.V)

    def z(self) -> tuple:
        Z = set()

        for v in self.V:
            if v.e_out == "":
                continue

            Z.add(v.z)

        Z = tuple(Z)

        Z_map = {}

        for v in self.V:
            if v.e_out == "":
                continue

            Z_map.setdefault(v, Z.index(v.z))

        return Z

    def g(self) -> tuple:
        G = set()

        for e in self.E:
            G.add(e.x)

        G = tuple(G)

        G_map = {}

        for e in self.E:
            G_map.setdefault((e.u, e.v), G.index(e.x))

        return G

    def e_in(self) -> tuple:
        E_in = set()

        for e in self.E:
            E_in.add(e.e_in)

        E_in = tuple(E_in)

        E_map = {}

        for e in self.E:
            E_map.setdefault((e.u, e.v), E_in.index(e.e_in))

        return E_in

    def e_out(self) -> tuple:
        E_out = set()

        for v in self.V:
            if v.e_out == "":
                continue

            E_out.add(v.e_out)

        E_out = tuple(E_out)

        E_map = {}

        for v in self.V:
            if v.e_out == "":
                continue

            E_map.setdefault(v, E_out.index(v.e_out))

        return E_out

    def __str__(self):
        sV = ""
        sE = ""

        for v in self.V:
            sV += str(v) + "\n"

        for e in self.E:
            sE += str(e) + "\n"

        return "V:\n" + sV + "\nE:\n" + sE


class LinkedNode:
    root = None
    links = None
    e_out = None
    z = None

    def __init__(self, e_out: str, z: tuple):
        self.e_out = e_out
        self.z = z
        self.links = {}

    def set_root(self, v):
        self.root = v

    def add_link(self, e_in: str, x: [], v):
        self.links.setdefault((e_in, str(x)), v)

    def new_link(self, e_in: str, x: [], e_out: str, z: tuple):
        new = LinkedNode(e_out, z)

        self.add_link(e_in, x, new)

        return new


def from_str_to_arr(s: str) -> tuple:
    ret = []

    for i in s[1:-1].split(", "):
        ret.append(int(i))

    return tuple(ret)


def to_tree(tree: LinkedNode) -> Tree:
    ret = Tree()
    current = [tree]
    added = set()
    m = {}

    while len(current) != 0:
        new_current = []

        for node in current:
            if node not in added:
                added.add(node)
                u = ret.add_vertex(node.e_out, node.z)
                m.setdefault(node, u.i)
            else:
                u = ret.V[m[node]]

            for (e_in, x) in node.links.keys():
                to_node = node.links[(e_in, x)]

                if node != to_node:
                    new_current.append(to_node)

                if to_node not in added:
                    added.add(to_node)
                    v = ret.add_vertex(to_node.e_out, to_node.z)
                    m.setdefault(to_node, v.i)
                else:
                    v = ret.V[m[to_node]]

                xa = from_str_to_arr(x)

                ret.add_edge(u, v, e_in, xa)

        current = new_current

    return ret
