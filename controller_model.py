from enum import Enum
from trace_parser import Trace, Event
from tree import Tree
from predicate import Predicate
from util import colors


class RuleType(Enum):
    ZERO = "(0->0, 1->0)"
    ONE = "(0->1, 1->1)"
    SELF = "(0->0, 1->1)"
    NEGATE = "(0->1, 1->0)"


class Rule:
    __types = ()

    def __init__(self, types: tuple):
        self.__types = types

    @staticmethod
    def __0110(var):
        if var == 1:
            return 0
        else:
            return 1

    @staticmethod
    def __0011(var):
        return var

    @staticmethod
    def __0010(var):
        return 0

    @staticmethod
    def __0111(var):
        return 1

    @staticmethod
    def __apply_to_one(var, t):
        if t == RuleType.ZERO:
            return Rule.__0010(var)
        elif t == RuleType.ONE:
            return Rule.__0111(var)
        elif t == RuleType.NEGATE:
            return Rule.__0110(var)
        elif t == RuleType.SELF:
            return Rule.__0011(var)

        return -1

    def apply(self, variables: list) -> list:
        ret = []

        for i in range(0, len(self.__types)):
            ret.append(Rule.__apply_to_one(variables[i], self.__types[i]))

        return ret

    def __str__(self):
        s = ""

        for zi in range(0, len(self.__types)):
            s += "z" + str(zi) + ": " + self.__types[zi].value + "\n"

        return s

    def to_str(self) -> str:
        s = ""

        for zi in range(0, len(self.__types)):
            s += self.__types[zi].name[0] + ","

        return s[:-1]


class Guard:
    vars = ()
    event = ""

    def check(self, variables: list, event: str) -> bool:
        return self.event == event and self.vars == variables

    def __init__(self, variables: list, event: str):
        self.vars = variables
        self.event = event

    def __str__(self):
        s = self.event + "["

        if self.vars[0] == 0:
            s += "-x0"
        else:
            s += "x0"

        for xi in range(1, len(self.vars)):
            if self.vars[xi] == 0:
                s += " /\\ -x" + str(xi)
            else:
                s += " /\\ x" + str(xi)

        s += "]"

        return s

    def to_str(self) -> str:
        s = self.event + "["

        if self.vars[0] == 0:
            s += "0"
        else:
            s += "1"

        for xi in range(1, len(self.vars)):
            if self.vars[xi] == 0:
                s += "0"
            else:
                s += "1"

        s += "]"

        return s


class State:
    output = None
    rules = None
    color = None

    def apply_rules(self, variables: list) -> list:
        return self.rules.apply(variables)

    def __init__(self, output: str, rules: Rule, color: int):
        self.output = output
        self.rules = rules
        self.color = color

    def __eq__(self, other):
        return self.color == other.color

    def __hash__(self):
        return self.color.__hash__()

    def __str__(self):
        return "Vertex " + str(self.color) + "\noutput: " + self.output + "\n" + self.rules.__str__()


class Edge:
    guard = None
    from_state = None
    to_state = None

    def can_go(self, variables: list, event: str) -> bool:
        return self.guard.check(variables, event)

    def __init__(self, inp: str, guard: list, from_state: State, to_state: State):
        self.guard = Guard(guard, inp)
        self.from_state = from_state
        self.to_state = to_state

    def __str__(self):
        return "Edge " + str(self.from_state.color) + " -> " + str(self.to_state.color) + " | " + str(self.guard)


class ControllerFiniteStateModel:
    root = None
    V = list()
    E = list()
    Z_size = 0
    X_size = 0

    def __init__(self, Z: int, X: int):
        self.V = list()
        self.E = list()
        self.Z_size = Z
        self.X_size = X

    def add_state(self, output: str, rules: {}, color: int) -> State:
        s = State(output, rules, color)

        if color == 0:
            self.root = s

        self.V.append(s)

        return s

    def add_edge(self, inp: str, guard: list, from_state: State, to_state: State) -> Edge:
        e = Edge(inp, guard, from_state, to_state)
        self.E.append(e)

        return e

    def __edges_from(self, v: State) -> list:
        ret = []

        for e in self.E:
            if e.from_state == v:
                ret.append(e)

        return ret

    def bfs_check(self, p: Predicate[State]) -> bool:
        visited = list(map(lambda x: False, range(0, len(self.V))))
        to_visit = [self.root]

        while not all(visited):
            next = []

            for v in to_visit:
                visited[v.color] = True

                if not p.apply_to(v):
                    return False

                for e in self.__edges_from(v):
                    if not visited[e.to_state.color] and e.to_state not in next:
                        next.append(e.to_state)

            to_visit = next

        return True

    def bfs(self, p: Predicate[State]) -> State:
        visited = list(map(lambda x: False, range(0, len(self.V))))
        to_visit = [self.root]

        while not all(visited):
            next = []

            for v in to_visit:
                visited[v.color] = True

                if p.apply_to(v):
                    return v

                for e in self.__edges_from(v):
                    if not visited[e.to_state.color] and e.to_state not in next:
                        next.append(e.to_state)

            to_visit = next

        return None

    def run_trace(self, trace: Trace) -> bool:
        current_state = self.root
        current_z = tuple(map(lambda x: 0, range(0, self.Z_size)))
        trace.new_counter()

        while trace.check_counter():
            (current_ein, current_eout) = trace.next_event()
            edges = self.__edges_from(current_state)
            next_state = None

            for e in edges:
                if e.can_go(current_ein.variables, current_ein.name):
                    next_state = e.to_state
                    break

            if next_state is None or next_state.output != current_eout.name:
                print("wrong state on edge " + str(current_ein) + " -> " + str(current_eout) + " of trace")
                print(trace)
                return False

            next_z = next_state.apply_rules(current_z)
            if current_eout.variables != next_z:
                print("wrong out on edge " + str(current_ein) + " -> " + str(current_eout) + " of trace")
                print(next_z)
                print(current_state.color)
                print(trace)
                return False

            current_z = next_z
            current_state = next_state

        return True

    def to_dot(self, name: str):
        inp = open(name + ".gv", "w")
        inp.write("digraph g {\n")

        for v in self.V:
            s = ""

            if v == self.root:
                s += "root"
            else:
                s += v.output + str(v.color)

            s += " [label = \"" + v.output + str(v.color) + "[" + v.rules.to_str() + "\", color = \"" + colors[v.color] + "\"];\n"

            inp.write(s)

        for e in self.E:
            u = e.from_state
            v = e.to_state

            if u == self.root:
                s = "root -> "
            else:
                s = u.output + str(u.color) + " -> "

            s += v.output + str(v.color) + " [label = \"" + e.guard.to_str() + "\"];\n"
            inp.write(s)

        inp.write("}")
        inp.close()

    def generate_trace_tree(self, n: int) -> Tree:
        tree = Tree()
        to_walk = [(self.root, tuple(map(lambda x: 0, range(0, self.Z_size))), tree.root)]

        for i in range(0, n):
            next_walk = []

            for (current_state, current_z, current_node) in to_walk:
                edges = self.__edges_from(current_state)

                for e in edges:
                    next_state = e.to_state
                    next_z = next_state.apply_rules(current_z)
                    next_node = tree.add_vertex(next_state.output, next_z)

                    tree.add_edge(current_node, next_node, e.guard.event, e.guard.vars)

                    next_walk.append((next_state, next_z, next_node))

            to_walk = next_walk

        return tree

    def continue_trace(self, trace: Trace, n: int) -> [Trace]:
        ret_trace = Trace("", False, seq=trace)

        current_state = self.root
        current_z = tuple(map(lambda x: 0, range(0, self.Z_size)))
        trace.new_counter()

        while trace.check_counter():
            (current_ein, current_eout) = trace.next_event()
            edges = self.__edges_from(current_state)
            next_state = None

            for e in edges:
                if e.can_go(current_ein.variables, current_ein.name):
                    next_state = e.to_state
                    break

            next_z = next_state.apply_rules(current_z)

            current_z = next_z
            current_state = next_state

        to_visit = [(current_state, current_z, ret_trace)]

        for _ in range(0, n):
            next_visit = []

            for (state, z, t) in to_visit:
                edges = self.__edges_from(state)

                for e in edges:
                    next_state = e.to_state
                    next_z = next_state.apply_rules(z)
                    next_trace = Trace("", False, seq=t)

                    e_name = e.guard.event
                    e_vars = e.guard.vars

                    e_in = Event("", name=e_name, v=e_vars, t="in")

                    e_name = next_state.output

                    e_out = Event("", name=e_name, v=next_z, t="out")

                    next_trace.append(e_in, e_out)

                    next_visit.append((next_state, next_z, next_trace))

            to_visit = next_visit

        result = []

        for (_, _, t) in to_visit:
            result.append(t)

        return result

    def __str__(self):
        sV = ""
        sE = ""

        for v in self.V:
            sV += str(v) + "\n"

        for e in self.E:
            sE += str(e) + "\n"

        return "V:\n" + sV + "\nE:\n" + sE


