class Node:
    i = None
    e_out = None
    z = None

    def __init__(self, e_out: str, z: list, i: int):
        self.e_out = e_out
        self.z = z
        self.i = i

    def __eq__(self, other):
        return self.e_out == other.e_out and self.z == other.z and other.i == self.i

    def __str__(self):
        return "out: " + self.e_out + " || z: " + str(self.z) + " || i: " + str(self.i)


class Edge:
    e_in = None
    x = None
    u = None
    v = None

    def __init__(self, e_in: str, x: list, u: Node, v: Node):
        self.e_in = e_in
        self.x = x
        self.u = u
        self.v = v

    def __eq__(self, other):
        return self.e_in == other.e_in and self.x == other.x and self.u == other.u and self.v == other.v

    def __str__(self):
        return "in: " + self.e_in + " || x: " + str(self.x) + " || from: {" + str(self.u) + "} || to: {" + str(self.v) + "}"


class Tree:
    root = None
    V = list()
    E = list()

    def __init__(self):
        self.E = list()
        self.V = list()
        self.root = Node("", list(), 0)
        self.V.append(self.root)

    def add_edge(self, u: Node, v: Node, e_in: str, x: list) -> Edge:
        new = Edge(e_in, x, u, v)

        for e in self.E:
            if e.e_in == e_in and e.x == x and u == e.u and v == e.v:
                return e

        self.E.append(new)
        return new

    def add_vertex(self, e_out: str, z: list) -> Node:
        if len(self.root.z) < len(z):
            self.root.z = list(map(lambda _: 0, range(0, len(z))))

        new = Node(e_out, z, len(self.V))
        self.V.append(new)
        return new

    def e_to_tuple(self) -> tuple:
        E_ = list(self.E)
        E_.sort(key=lambda x: x.u.i)

        return tuple(E_)

    def v_to_tuple(self) -> tuple:
        V_ = list(self.V)
        V_.sort(key=lambda x: x.i)

        return tuple(V_)

    def z(self) -> tuple:
        Z = list()

        for v in self.V:
            flag = False

            for z in Z:
                if v.z == z:
                    flag = True
                    break

            if not flag:
                Z.append(v.z)

        # print(Z)

        Z.sort()

        return tuple(Z)

    def e_g(self) -> tuple:
        EG = list()

        for e in self.E:
            flag = False

            for (e_in, g) in EG:
                if e.x == g and e.e_in == e_in:
                    flag = True
                    break

            if not flag:
                EG.append((e.e_in, e.x))

        return tuple(EG)

    def g(self) -> tuple:
        G = list()

        for e in self.E:
            flag = False

            for g in G:
                if e.x == g:
                    flag = True
                    break

            if not flag:
                G.append(e.x)

        G.sort()

        #print(G)

        return tuple(G)

    def e_in(self) -> tuple:
        E_in = set()

        for e in self.E:
            E_in.add(e.e_in)

        E_in = tuple(E_in)

        return E_in

    def e_out(self) -> tuple:
        E_out = set()

        for v in self.V:
            E_out.add(v.e_out)

        E_out = tuple(E_out)

        return E_out

    def __str__(self):
        sV = ""
        sE = ""

        for v in self.V:
            sV += str(v) + "\n"

        for e in self.E:
            sE += str(e) + "\n"

        return "V:\n" + sV + "\nE:\n" + sE

    def to_dot(self, name: str):
        inp = open(name + ".gv", "w")
        inp.write("digraph t {\n")

        for v in self.V:
            s = ""

            if v == self.root:
                s += "root"
            else:
                s += v.e_out + str(v.i)

            s += " [label = \"" + v.e_out + str(v.i) + str(v.z) + "\"];\n"

            inp.write(s)

        for e in self.E:
            u = e.u
            v = e.v

            if u == self.root:
                s = "root -> "
            else:
                s = u.e_out + str(u.i) + " -> "

            s += v.e_out + str(v.i) + " [label = \"" + str(e.x) + "\"];\n"
            inp.write(s)

        inp.write("}")
        inp.close()

    def p_to_dot(self, name: str):
        inp = open(name + ".gv", "w")
        inp.write("digraph t {\n")

        for v in self.V:
            s = ""

            s += v.e_out + str(v.i)

            s += " [label = \"" + v.e_out + str(v.i) + str(v.z) + "\"];\n"

            inp.write(s)

        for e in self.E:
            u = e.u
            v = e.v

            s = u.e_out + str(u.i) + " -> "

            s += v.e_out + str(v.i) + " [label = \"" + str(e.x) + "\"];\n"
            inp.write(s)

        inp.write("}")
        inp.close()

    def edges_from(self, v: Node) -> list:
        ret = []

        for e in self.E:
            if e.u == v:
                ret.append(e)

        return ret


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
