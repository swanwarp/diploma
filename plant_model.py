from controller_model import Guard
from trace_parser import Trace


class State:
    output = None
    color = None

    def __init__(self, output: tuple(), color: int):
        self.output = output
        self.color = color

    def __eq__(self, other):
        return self.color == other.color

    def __hash__(self):
        return self.color.__hash__()

    def __str__(self):
        return "Vertex " + str(self.color) + "\noutput: " + self.output


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


class PlantFiniteStateModel:
    root = None
    V = set()
    E = set()
    Z_size = 0
    X_size = 0

    def __init__(self, Z: int, X: int):
        self.V = set()
        self.E = set()
        self.Z_size = Z
        self.X_size = X

    def add_state(self, output: str, color: int) -> State:
        s = State(output, color)

        if color == 0:
            self.root = s

        self.V.add(s)

        return s

    def add_edge(self, inp: str, guard: list, from_state: State, to_state: State) -> Edge:
        e = Edge(inp, guard, from_state, to_state)
        self.E.add(e)

        return e

    def __edges_from(self, v: State) -> list:
        ret = []

        for e in self.E:
            if e.from_state == v:
                ret.append(e)

        return ret

    def run_trace(self, trace: Trace) -> bool:
        current_state = self.root
        trace.new_counter()

        while trace.check_counter():
            (current_ein, current_eout) = trace.next_event()
            edges = self.__edges_from(current_state)
            next_state = None

            for e in edges:
                if e.can_go(current_ein.variables, current_ein.name):
                    next_state = e.to_state
                    break

            if next_state is None or next_state.output != current_eout.variables:
                print("wrong state on edge " + str(current_ein) + " -> " + str(current_eout) + " of trace")
                print(current_state.color)
                print(next_state.output)
                print(current_eout.variables)
                print(trace)
                return False

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
                s += str(v.color)

            s += " [label = \"" + str(v.color) + str(v.output) + "\"];\n"

            inp.write(s)

        for e in self.E:
            u = e.from_state
            v = e.to_state

            if u == self.root:
                s = "root -> "
            else:
                s = str(u.color) + " -> "

            if v == self.root:
                s += "root [label = \"" + e.guard.to_str() + "\"];\n"
            else:
                s += str(v.color) + " [label = \"" + e.guard.to_str() + "\"];\n"
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


