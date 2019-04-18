from subprocess import run
from tree import Tree
from controller_model import ControllerFiniteStateModel, Rule, RuleType
from plant_model import PlantFiniteStateModel


class VariableCounter:
    count = 0

    def __init__(self):
        self.count = 0

    def add_variable(self) -> int:
        self.count += 1
        return self.count


def sat_from_tree(C: int, K: int, S: int, controller_tree: Tree, plant_tree: Tree):
    return sat(C, controller_tree.v_to_tuple(), controller_tree.e_to_tuple(), controller_tree.e_in(),
               controller_tree.e_out(), controller_tree.g(), controller_tree.z(), K,
               S, plant_tree.v_to_tuple(), plant_tree.e_to_tuple(), plant_tree.e_in(), plant_tree.g(), plant_tree.z(), plant_tree.root)


def sat(C, V: tuple, E: tuple, E_in: tuple, E_out: tuple, G: tuple, Z: tuple, K: int,  # controller
        S: int, V_plant: tuple, E_plant: tuple, E_in_plant: tuple, G_plant: tuple, O: tuple, p_roots: list):  # plant

    lE_in = len(E_in)
    lE_out = len(E_out)
    lV = len(V)
    lG = len(G)
    lZ = 0

    for z in Z:
        lZ = max(lZ, len(z))

    c = []
    d0 = []
    d1 = []
    o = []
    y = []

    counter = VariableCounter()

    for v in range(0, lV):
        c.append([])

        for i in range(0, C):
            c[v].append(counter.add_variable())

    for n in range(0, C):
        d0.append([])
        d1.append([])

        for i in range(0, lZ):
            d0[n].append(counter.add_variable())
            d1[n].append(counter.add_variable())

    for n in range(0, C):
        o.append([])

        for i in range(0, lE_out):
            o[n].append(counter.add_variable())

    for n1 in range(0, C):
        y.append([])
        for e in range(0, lE_in):
            y[n1].append([])
            for g in range(0, lG):
                y[n1][e].append([])
                for n2 in range(0, C):
                    y[n1][e][g].append(counter.add_variable())

    clauses = list()

    # section 1 --------------------------------------------------------------------------------------------------------

    # 1.1
    clauses.append([c[0][0]])

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
        for n1 in range(0, C):
            for n2 in range(0, C):
                if n1 == n2:
                    continue

                clauses.append([-c[v][n1], -c[v][n2]])

    # section 3 --------------------------------------------------------------------------------------------------------

    # 3.1
    for e in E:
        u = e.u.i
        v = e.v.i
        e_in = E_in.index(e.e_in)
        g = G.index(e.x)

        # print(e)
        # print((u, v, e_in, g))

        for n1 in range(0, C):
            for n2 in range(0, C):
                clauses.append([-c[u][n1], -c[v][n2], y[n1][e_in][g][n2]])

    # 3.2
    for n1 in range(0, C):
        for n2 in range(0, C):
            for n3 in range(0, C):
                if n2 == n3:
                    continue

                for e in range(0, lE_in):
                    for g in range(0, lG):
                        clauses.append([-y[n1][e][g][n2], -y[n1][e][g][n3]])

    # each state has at least one from-edge

    # for n1 in range(1, C):
    #     temp = []
    #
    #     for e in range(0, lE_in):
    #         for g in range(0, lG):
    #             for n2 in range(1, C):
    #                 if n1 == n2:
    #                     continue
    #
    #                 temp.append(y[n1][e][g][n2])
    #
    #     clauses.append(temp)

    # section 4 --------------------------------------------------------------------------------------------------------

    # 4.1
    for v in V:
        if v == V[0]:
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
        for j1 in range(0, lE_out):
            for j2 in range(0, lE_out):
                if j1 == j2:
                    continue

                clauses.append([-o[n][j1], -o[n][j2]])

    # section 5 --------------------------------------------------------------------------------------------------------

    # 5.1
    for e in E:
        u = e.u
        v = e.v
        v_i = V.index(v)

        for n in range(0, C):
            for i in range(0, lZ):
                if u.z[i] == 0 and v.z[i] == 0:
                    clauses.append([-c[v_i][n], -d0[n][i]])

                if u.z[i] == 0 and v.z[i] == 1:
                    clauses.append([-c[v_i][n], d0[n][i]])

                if u.z[i] == 1 and v.z[i] == 0:
                    clauses.append([-c[v_i][n], -d1[n][i]])

                if u.z[i] == 1 and v.z[i] == 1:
                    clauses.append([-c[v_i][n], d1[n][i]])

    # добавил, чтобы исключить One и Zero из правил

    # for n in range(1, C):
    #     for i in range(0, lZ):
    #         clauses.append([-d0[n][i], -d1[n][i]])
    #         clauses.append([d0[n][i], d1[n][i]])

    # section 6 --------------------------------------------------------------------------------------------------------

    if K != 0:
        gamma = {}
        dzetha = {}

        for n1 in range(0, C):
            dzetha.setdefault(n1, {})

            for n2 in range(0, C):
                index = counter.add_variable()
                dzetha[n1].setdefault(n2, index)

        for n1 in range(0, C):
            gamma.setdefault(n1, {})

            for n2 in range(0, C):
                gamma[n1].setdefault(n2, {})

                for k in range(0, C):
                    index = counter.add_variable()
                    gamma[n1][n2].setdefault(k, index)

        # 6.1
        for n1 in range(0, C):
            for n2 in range(0, C):
                temp = [dzetha[n1][n2]]

                for e in range(0, lE_in):
                    for g in range(0, lG):
                        clauses.append([-dzetha[n1][n2], y[n1][e][g][n2]])
                        temp.append(-y[n1][e][g][n2])

                clauses.append(temp)

        # 6.2
        temp = []

        for n in range(0, C):
            temp.append(gamma[n][1][0])

        clauses.append(temp)

        # 6.3
        for n1 in range(0, C):
            for n2 in range(1, C):
                for k in range(0, C - 1):
                    clauses.append([-gamma[n1][n2 - 1][k], -dzetha[n1][n2], gamma[n1][n2][k + 1]])

        # 6.4
        for n1 in range(0, C):
            for n2 in range(1, C):
                for k in range(0, C):
                    clauses.append([-gamma[n1][n2 - 1][k], dzetha[n1][n2], gamma[n1][n2][k]])

        # 6.5
        for n in range(0, C):
            for k in range(K + 1, C):
                clauses.append([gamma[n][C - 1][k]])

    # plant section ----------------------------------------------------------------------------------------------------

    if S != 0:

        # for v in V_plant:
        #     print(v)

        x = []
        yp = []
        zp = []

        for v in range(0, len(V_plant)):
            x.append([])

            for s in range(0, S):
                x[v].append(counter.add_variable())

        for s1 in range(0, S):
            yp.append([])

            for i in range(0, len(E_in_plant)):
                yp[s1].append([])

                for g in range(0, len(G_plant)):
                    yp[s1][i].append([])

                    for s2 in range(0, S):
                        yp[s1][i][g].append(counter.add_variable())

        for s in range(0, S):
            zp.append([])

            for eo in range(0, len(O)):
                zp[s].append(counter.add_variable())

        # root has color 0

        # clauses.append([x[0][0]])

        # section 1 ----------------------------------------------------------------------------------------------------

        for v in range(0, len(V_plant)):
            temp = []

            for s in range(0, S):
                temp.append(x[v][s])

            clauses.append(temp)

        for v in range(0, len(V_plant)):
            for s1 in range(0, S):
                for s2 in range(0, S):
                    if s1 == s2:
                        continue

                    clauses.append([-x[v][s1], -x[v][s2]])

        # section 2 ----------------------------------------------------------------------------------------------------

        for e in E_plant:
            u = e.u
            v = e.v
            ei = E_in_plant.index(e.e_in)
            gi = G_plant.index(e.x)

            for s1 in range(0, S):
                for s2 in range(0, S):
                    clauses.append([-x[u.i][s1], -x[v.i][s2], yp[s1][ei][gi][s2]])

        # for s1 in range(0, S):
        #     for s2 in range(0, S):
        #         for s3 in range(0, S):
        #             if s2 == s3:
        #                 continue
        #
        #             for ei in range(0, len(E_in_plant)):
        #                 for gi in range(0, len(G_plant)):
        #                     clauses.append([-yp[s1][ei][gi][s2], -yp[s1][ei][gi][s3]])

        # section 3 ----------------------------------------------------------------------------------------------------

        for v in V_plant:
            vi = V_plant.index(v)

            oi = O.index(v.z)

            for s in range(0, S):
                clauses.append([-x[vi][s], zp[s][oi]])

                for eo in range(0, len(O)):
                    if eo == oi:
                        continue

                    clauses.append([-x[vi][s], -zp[s][eo]])

        # section 4 ----------------------------------------------------------------------------------------------------

        for s1 in range(0, S):
            temp = []

            for ei in range(0, len(E_in_plant)):
                for gi in range(0, len(G_plant)):
                    for s2 in range(0, S):
                        if s1 == s2:
                            continue

                        temp.append(yp[s1][ei][gi][s2])

            clauses.append(temp)

    # run sat-solver ---------------------------------------------------------------------------------------------------

    inp = open("example.in", "w")

    inp.write("p cnf ")
    inp.write(str(counter.count + 1))
    inp.write(" " + str(len(clauses)) + "\n")

    for css in clauses:
        for l in css:
            inp.write(str(l) + " ")

        inp.write("0\n")

    inp.close()

    inp = open("example.out", "w")
    compl = run(".\cms.exe --verb 0 example.in", shell=True, stdout=inp)
    #compl = run("./cms-linux --verb 0 example.in", shell=True, stdout=inp)
    inp.close()

    inp = open("example.out", "r")
    res = inp.readline()

    if res != "s SATISFIABLE\n":
        return [None, None]

    lines = inp.readlines()

    result = []

    for line in lines:
        temp = line.split(" ")[1:]

        if temp[len(temp) - 1][-1] == "\n":
            temp.pop()

        result += list(map(lambda x: int(x), temp))

    # building controller automaton ------------------------------------------------------------------------------------

    colors = []

    for v in range(0, lV):
        for i in range(0, C):
            if result[c[v][i] - 1] > 0:
                colors.append((v, i))

    #print(colors)

    output = []

    for n in range(1, C):
        for i in range(0, lE_out):
            if result[o[n][i] - 1] > 0:
                output.append(i)

    #print(output)

    y_out = []

    for n1 in range(0, C):
        for e in range(0, lE_in):
            for g in range(0, lG):
                for n2 in range(0, C):
                    if result[y[n1][e][g][n2] - 1] > 0:
                        y_out.append((n1, e, g, n2))

    #print(y_out)

    model = ControllerFiniteStateModel(lZ, lG)

    # building rules for each state
    rules = {}

    for n in range(0, C):
        types = []

        for i in range(0, lZ):
            if result[d0[n][i] - 1] > 0 and result[d1[n][i] - 1] > 0:
                rule = RuleType.ONE
            elif result[d0[n][i] - 1] < 0 and result[d1[n][i] - 1] > 0:
                rule = RuleType.SELF
            elif result[d0[n][i] - 1] > 0 and result[d1[n][i] - 1] < 0:
                rule = RuleType.NEGATE
            else:
                rule = RuleType.ZERO

            types.append(rule)

        rules.setdefault(n, Rule(tuple(types)))

    # building states
    states = {0: model.add_state("", rules[0], 0)}

    for i in range(1, C):
        states.setdefault(i, model.add_state(E_out[output[i - 1]], rules[i], i))

    # building edges
    for (n1, e, g, n2) in y_out:
        model.add_edge(E_in[e], G[g], states[n1], states[n2])

    # building plant automaton -----------------------------------------------------------------------------------------
    if S != 0:
        p_colors = []

        for v in range(0, len(V_plant)):
            for i in range(0, S):
                if result[x[v][i] - 1] > 0:
                    p_colors.append((v, i))

        # for i in x_to_ind.keys():
        #     if result[i - 1] > 0:
        #         p_colors.append(x_to_ind[result[i - 1]])

        p_output = []

        for n in range(0, S):
            for i in range(0, len(O)):
                if result[zp[n][i] - 1] > 0:
                    p_output.append(i)

        # for i in zp_to_ind.keys():
        #     if result[i - 1] > 0:
        #         col, ev = zp_to_ind[result[i - 1]]
        #         p_output.setdefault(col, ev)

        p_y_out = []

        for n1 in range(0, S):
            for e in range(0, len(E_in_plant)):
                for g in range(0, len(G_plant)):
                    for n2 in range(0, S):
                        if result[yp[n1][e][g][n2] - 1] > 0:
                            p_y_out.append((n1, e, g, n2))

        pZ = 0

        for e in O:
            pZ = max(len(e), pZ)

        pX = 0

        for g in G_plant:
            pX = max(len(g), pX)

        plant = PlantFiniteStateModel(pZ, pX)

        #building states
        states = []

        for i in range(0, S):
            if any(r.z == O[p_output[i]] for r in p_roots):
                states.append(plant.add_root(O[p_output[i]], i)) # adding verticle in roots if it was root in tree
            else:
                states.append(plant.add_state(O[p_output[i]], i))

        # building edges
        for n1, e, g, n2 in p_y_out:
            plant.add_edge(E_in_plant[e], G_plant[g], states[n1], states[n2])
    else:
        plant = None

    return [model, plant]
