from subprocess import run
from tree import Tree
from trace_parser import Trace


def sat(E_in, E_out, Z, V, E, C, G):
    lE_in = len(E_in)
    lE_out = len(E_out)
    lE = len(E)
    lV = len(V)
    lG = len(G)

    E_to_num = {}
    G_to_num = {}
    E_in_to_num = {}
    E_out_to_num = {}
    V_to_num = {}

    i = 0
    for e in E:
        E_to_num.setdefault((e.u, e.v), i)
        i += 1

    for e in E:
        G_to_num.setdefault((e.u, e.v), G.index(e.x))

    i = 0
    for (u, v) in E_in.keys():
        E_in_to_num.setdefault((u, v), i)
        i += 1

    i = 0
    for v in V:
        V_to_num.setdefault(v, i)
        i += 1

    i = 0
    for v in E_out.keys():
        E_out_to_num.setdefault(v, i)
        i += 1

    length = C * C * lE_in * lG + C * lV
    cs = 0 * length + 1
    ys = 1 * length + 1
    d0s = 2 * length + 1
    d1s = 3 * length + 1
    os = 4 * length + 1

    c = {}
    d0 = {}
    d1 = {}
    o = {}
    y = {}

    for v in range(0, lV):
        c.setdefault(v, {})

        for i in range(0, C):
            c[v].setdefault(i, cs + i + v * C)

    for n in range(0, C):
        d0.setdefault(n, {})
        d1.setdefault(n, {})

        for i in range(0, Z):
            d0[n].setdefault(i, d0s + i + n * Z)
            d1[n].setdefault(i, d1s + i + n * Z)

    for n in range(0, C):
        o.setdefault(n, {})

        for i in range(0, lE_out):
            o[n].setdefault(i, os + i + n * lE_out)

    for n1 in range(0, C):
        y.setdefault(n1, {})
        for e in range(0, lE_in):
            y[n1].setdefault(e, {})
            for g in range(0, lG):
                y[n1][e].setdefault(g, {})
                for n2 in range(0, C):
                    y[n1][e][g].setdefault(n2, ys + n2 + g * C + e * lG * C + n1 * lE_in * lG * C)

    clauses = list()

    # section 1 --------------------------------------------------------------------------------------------------------

    # 1.1
    clauses.append([c[V_to_num[V[0]]][0]])

    # 1.2
    for i in range(0, Z):
        clauses.append([-d0[0][i]])
        clauses.append([-d1[0][i]])

    # 1.3
    for j in range(0, lE_out):
        clauses.append([-o[0][j]])

    # section 2 --------------------------------------------------------------------------------------------------------

    # 2.1
    for v in range(0, lV):
        temp = list()

        for i in range(0, C):
            temp.append(c[v][i])

        clauses.append(temp)

    # 2.2
    for v in range(0, lV):
        for n1 in range(0, C - 1):
            for n2 in range(n1 + 1, C):
                clauses.append([-c[v][n1], -c[v][n2]])

    # section 3 --------------------------------------------------------------------------------------------------------

    # 3.1
    for e in E:
        u = e.u
        v = e.v
        for n1 in range(0, C):
            for n2 in range(0, C):
                clauses.append([-c[V_to_num[u]][n1], -c[V_to_num[v]][n2], y[n1][E_in_to_num[(u, v)]][G_to_num[(u, v)]][n2]])

    # 3.2
    for n1 in range(0, C):
        for n2 in range(n1, C):
            for n3 in range(n2 + 1, C):
                for e in range(0, lE_in):
                    for g in range(0, lG):
                        clauses.append([-y[n1][e][g][n2], -y[n1][e][g][n3]])

    # section 4 --------------------------------------------------------------------------------------------------------

    # 4.1
    for v in V:
        if v.e_out is None:
            continue

        for n in range(0, C):
            clauses.append([-c[V_to_num[v]][n], o[n][E_out_to_num[v]]])

    # 4.2
    for n in range(0, C):
        temp = list()

        for e in range(0, lE_out):
            temp.append(o[n][e])

        clauses.append(temp)

    # 4.3
    for n in range(0, C):
        for j1 in range(0, lE_out - 1):
            for j2 in range(j1 + 1, lE_out):
                clauses.append([-o[n][j1], -o[n][j2]])

    # section 5 --------------------------------------------------------------------------------------------------------

    # 5.1
    for e in E:
        u = e.u
        v = e.v
        for n in range(0, C):
            for i in range(0, Z):
                if V[V_to_num[u]].z[i] == 1 and V[V_to_num[v]].z[i] == 1:
                    clauses.append([-c[V_to_num[v]][n], -d0[n][i]])

                if V[V_to_num[u]].z[i] == 1 and V[V_to_num[v]].z[i] == 0:
                    clauses.append([-c[V_to_num[v]][n], d0[n][i]])

                if V[V_to_num[u]].z[i] == 0 and V[V_to_num[v]].z[i] == 1:
                    clauses.append([-c[V_to_num[v]][n], -d1[n][i]])

                if V[V_to_num[u]].z[i] == 0 and V[V_to_num[v]].z[i] == 0:
                    clauses.append([-c[V_to_num[v]][n], d1[n][i]])

    # run sat-solver ---------------------------------------------------------------------------------------------------

    inp = open("example.in", "w")

    inp.write("p cnf ")
    inp.write(str(length * 5))
    inp.write(" " + str(len(clauses)) + "\n")

    for css in clauses:
        for l in css:
            inp.write(str(l) + " ")

        inp.write("0\n")

    inp.close()

    inp = open("example.out", "w")
    compl = run(".\cms.exe --verb 0 example.in", shell=True, stdout=inp)
    inp.close()

    inp = open("example.out", "r")
    res = inp.readline()

    print(res)
    print(inp.readlines())


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


def from_str(arr: str) -> tuple:
    ret = []

    for s in arr:
        ret.append(int(s))

    return tuple(ret)


def build_controller_tree(traces: list, with_self_links: bool) -> LinkedNode:
    root = LinkedNode("", tuple())
    current = root

    for trace in traces:
        for t in trace:
            if with_self_links:
                for i in t["inp"][:-1]:
                    current.add_link(i["name"], from_str(i["x"]), current)

            if t["out"] is not None:
                if current.links.get((t["inp"][-1]["name"], t["inp"][-1]["x"])) is None:
                    current = current.new_link(t["inp"][-1]["name"], from_str(t["inp"][-1]["x"]),
                                               t["out"]["name"], from_str(t["out"]["z"]))

                    current.set_root(root)
                else:
                    current = current.links[(t["inp"][-1]["name"], t["inp"][-1]["x"])]
            elif with_self_links:
                current.add_link(t["inp"][-1]["name"], from_str(t["inp"][-1]["x"]), current)

        current = root

    return root


def build_controller_from_names(names: list, with_self_links: bool) -> Tree:
    traces = []

    for name in names:
        traces += read_traces(name)

    return to_tree(build_controller_tree(traces, with_self_links))


def read_traces(name: str):
    inp = open("pnp-traces/" + name, "r")
    res = []

    for s in inp.readlines():
        temp = s.split(" ")

        if len(temp) == 1:
            continue

        trace = []

        while len(temp) != 0:
            obj = {
                "inp": [],
                "out": None,
            }

            t = temp.pop(0)

            while t[0:3] != "out":
                if t[0:2] == "in":
                    t = t[3:]
                    t = t.split("[")
                    obj["inp"].append({"name": t[0], "x": t[1][0:-2]})

                if len(temp) == 0:
                    break

                t = temp.pop(0)

            if t[0:3] == "out":
                t = t[4:]
                t = t.split("[")

                obj["out"] = {"name": t[0], "z": t[1].split("]")[0]}

            trace.append(obj)

        res.append(trace)

    return res


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

