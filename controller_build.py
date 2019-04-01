from subprocess import run


def sat(C, V: tuple, E: tuple, E_in: tuple, E_out: tuple, G: tuple, Z: tuple):
    lE_in = len(E_in)
    lE_out = len(E_out)
    lE = len(E)
    lV = len(V)
    lG = len(G)
    lZ = 0

    for z in Z:
        lZ = max(lZ, len(z))

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

    c_to_ind = {}
    o_to_ind = {}
    y_to_ind = {}
    d0_to_ind = {}
    d1_to_ind = {}

    for v in range(0, lV):
        c.setdefault(v, {})

        for i in range(0, C):
            c[v].setdefault(i, cs + i + v * C)
            c_to_ind.setdefault(cs + i + v * C, (v, i))

    for n in range(0, C):
        d0.setdefault(n, {})
        d1.setdefault(n, {})

        for i in range(0, lZ):
            d0[n].setdefault(i, d0s + i + n * lZ)
            d0_to_ind.setdefault(d0s + i + n * lZ, (n, i))

            d1[n].setdefault(i, d1s + i + n * lZ)
            d1_to_ind.setdefault(d1s + i + n * lZ, (n, i))

    for n in range(0, C):
        o.setdefault(n, {})

        for i in range(0, lE_out):
            o[n].setdefault(i, os + i + n * lE_out)
            o_to_ind.setdefault(os + i + n * lE_out, (n, i))

    for n1 in range(0, C):
        y.setdefault(n1, {})
        for e in range(0, lE_in):
            y[n1].setdefault(e, {})
            for g in range(0, lG):
                y[n1][e].setdefault(g, {})
                for n2 in range(0, C):
                    y[n1][e][g].setdefault(n2, ys + n2 + g * C + e * lG * C + n1 * lE_in * lG * C)
                    y_to_ind.setdefault(ys + n2 + g * C + e * lG * C + n1 * lE_in * lG * C, (n1, e, g, n2))

    clauses = list()

    # section 1 --------------------------------------------------------------------------------------------------------

    root_node = -1

    # search root's index
    for i in range(0, lV):
        if V[i].e_out == "":
            root_node = i
            break

    V[root_node].z = tuple(map(lambda _: 0, range(0, lZ)))

    # 1.1
    clauses.append([c[root_node][0]])

    # 1.2
    for i in range(0, lZ):
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
                clauses.append([-c[V.index(u)][n1], -c[V.index(v)][n2], y[n1][E_in.index(e.e_in)][G.index(e.x)][n2]])

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
        if v.e_out is "":
            continue

        for n in range(0, C):
            clauses.append([-c[V.index(v)][n], o[n][E_out.index(v.e_out)]])

    # 4.2
    for n in range(1, C):
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
        u_i = V.index(u)
        v_i = V.index(v)

        for n in range(0, C):
            for i in range(0, lZ):
                if V[u_i].z[i] == 1 and V[v_i].z[i] == 1:
                    clauses.append([-c[v_i][n], -d0[n][i]])

                if V[u_i].z[i] == 1 and V[v_i].z[i] == 0:
                    clauses.append([-c[v_i][n], d0[n][i]])

                if V[u_i].z[i] == 0 and V[v_i].z[i] == 1:
                    clauses.append([-c[v_i][n], -d1[n][i]])

                if V[u_i].z[i] == 0 and V[v_i].z[i] == 0:
                    clauses.append([-c[v_i][n], d1[n][i]])

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

    if res != "s SATISFIABLE\n":
        return None

    lines = inp.readlines()

    result = []

    for line in lines:
        temp = line.split(" ")[1:]

        if temp[len(temp) - 1][-1] == "\n":
            temp.pop()

        result += list(map(lambda x: int(x), temp))

    colors = []

    for i in range(0, length):
        if result[i] > 0:
            colors.append(c_to_ind[result[i]])

    output = {}

    for i in range(os - 1, len(result)):
        if result[i] > 0:
            col, ev = o_to_ind[result[i]]
            output.setdefault(col, ev)

    y_out = {}

    for i in range(ys - 1, d0s - 1):
        if result[i] > 0:
            n1, e, g, n2 = y_to_ind[result[i]]
            y_out.setdefault((n1, n2), (E_in[e], G[g]))

    model = FiniteStateModel()

    # building rules for each state
    rules = {}

    for n in range(0, C):
        rules.setdefault(n, {})

        for i in range(0, lZ):
            if result[d0s + i + n * lZ - 1] > 0:
                rule0 = "0 -> 1"
            else:
                rule0 = "0 -> 0"

            if result[d1s + i + n * lZ - 1] > 0:
                rule1 = "1 -> 1"
            else:
                rule1 = "1 -> 0"

            rules[n].setdefault(i, "(" + rule0 + ", " + rule1 + ")")

    # building states
    states = {0: model.add_state("", rules[0], 0)}

    for i in range(1, C):
        states.setdefault(i, model.add_state(E_out[output[i]], rules[i], i))

    # building edges
    for n1, n2 in y_out.keys():
        (e, g) = y_out.get((n1, n2))

        model.add_edge(e, g, states[n1], states[n2])

    return model


class State:
    output = None
    rules = {}
    color = None

    def __init__(self, output: str, rules: {}, color: int):
        self.output = output
        self.rules = rules
        self.color = color

    def __eq__(self, other):
        return self.color == other.color

    def __hash__(self):
        return self.color.__hash__()

    def __str__(self):
        s = "Vertex " + str(self.color) + "\noutput: " + self.output + "\n"

        for zi in self.rules.keys():
            s += "z" + str(zi) + ": " + self.rules[zi] + "\n"

        return s


class Edge:
    input = None
    guard = None
    from_state = None
    to_state = None

    def __init__(self, inp: str, guard: tuple, from_state: State, to_state: State):
        self.input = inp
        self.guard = guard
        self.from_state = from_state
        self.to_state = to_state

    def __str__(self):
        return "Edge " + str(self.from_state.color) + " -> " + str(self.to_state.color) + " | " + self.input + str(self.guard)


class FiniteStateModel:
    V = set()
    E = set()

    def __init__(self):
        self.V = set()
        self.E = set()

    def add_state(self, output: str, rules: {}, color: int) -> State:
        s = State(output, rules, color)
        self.V.add(s)

        return s

    def add_edge(self, inp: str, guard: tuple, from_state: State, to_state: State) -> Edge:
        e = Edge(inp, guard, from_state, to_state)
        self.E.add(e)

        return e

    def __str__(self):
        sV = ""
        sE = ""

        for v in self.V:
            sV += str(v) + "\n"

        for e in self.E:
            sE += str(e) + "\n"

        return "V:\n" + sV + "\nE:\n" + sE
