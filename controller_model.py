from enum import Enum
from trace_parser import Trace


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
    __vars = ()
    __event = ""

    def check(self, variables: list, event: str) -> bool:
        return self.__event == event and self.__vars == variables

    def __init__(self, variables: list, event: str):
        self.__vars = variables
        self.__event = event

    def __str__(self):
        s = self.__event + "["

        if self.__vars[0] == 0:
            s += "-x0"
        else:
            s += "x0"

        for xi in range(1, len(self.__vars)):
            if self.__vars[xi] == 0:
                s += " /\\ -x" + str(xi)
            else:
                s += " /\\ x" + str(xi)

        s += "]"

        return s

    def to_str(self) -> str:
        s = self.__event + "["

        if self.__vars[0] == 0:
            s += "0"
        else:
            s += "1"

        for xi in range(1, len(self.__vars)):
            if self.__vars[xi] == 0:
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

    def add_edge(self, inp: str, guard: tuple, from_state: State, to_state: State) -> Edge:
        e = Edge(inp, guard, from_state, to_state)
        self.E.append(e)

        return e

    def __edges_from(self, v: State) -> list:
        ret = []

        for e in self.E:
            if e.from_state == v:
                ret.append(e)

        return ret

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

            s += " [label = \"" + v.output + str(v.color) + "[" + v.rules.to_str() + "]\"];\n"

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

    def __str__(self):
        sV = ""
        sE = ""

        for v in self.V:
            sV += str(v) + "\n"

        for e in self.E:
            sE += str(e) + "\n"

        return "V:\n" + sV + "\nE:\n" + sE

