from plant_tree import PlantTree
from tree import Tree
from enum import Enum
from re import split


class EventType(Enum):
    IN = "in"
    OUT = "out"


class Event:
    name = ""
    variables = []
    t = None

    def __init__(self, s: str, name="", v=list(), t=""):
        if name != "" and v != [] and t != "":
            self.name = name
            self.variables = v
            if t == "in":
                self.t = EventType.IN
            else:
                self.t = EventType.OUT
            return

        temp = s

        if temp[0:3] == "out":
            self.t = EventType.OUT
            temp = temp[4:].split("[")
        else:
            self.t = EventType.IN
            temp = temp[3:].split("[")

        self.name = temp[0]

        temp = temp[1][0:-2]
        variables = []

        for v in temp:
            if v == "1" or v == "0":
                variables.append(int(v))

        self.variables = variables

    def __str__(self):
        return str(self.t.name) + " " + self.name + str(self.variables)

    def __eq__(self, other):
        return self.variables == other.variables and self.name == other.name and self.t == other.t


class Trace:
    __sequence = []
    __counter = 0
    __plant_root = None
    __controller_last = None

    def __init__(self, trace: str, seq=None):
        self.__counter = -1

        if seq is not None:
            self.__plant_root = seq.__plant_root
            self.__sequence = list(seq.__sequence)
            return

        s = split(" +", trace)
        sequence = []

        if s[len(s) - 1] == "":
            s.pop(len(s) - 1)

        last = s.pop(0)

        while len(s) != 0:
            event = s.pop(0)

            if event[0:3] == "out":
                sequence.append((Event(last), Event(event)))

            last = event

            if len(s) == 0:
                self.__controller_last = Event(last)

        self.__sequence = sequence

    def transform(self):
        self.__counter = -1

        if self.__plant_root is not None:
            new_seq = []
            current_last = self.__plant_root

            for (ei, eo) in self.__sequence:
                new_seq.append((current_last, ei))
                current_last = eo

            self.__plant_root = None
            self.__controller_last = current_last
            self.__sequence = new_seq
        elif self.__controller_last is not None:
            new_seq = []
            self.__plant_root = self.__sequence[0][0]
            current_last = self.__sequence[0][1]

            for (ei, eo) in self.__sequence[1:]:
                new_seq.append((current_last, ei))
                current_last = eo

            new_seq.append((current_last, self.__controller_last))
            self.__controller_last = None
            self.__sequence = new_seq

    def plant_root(self) -> Event:
        return self.__plant_root

    def controller_last(self) -> Event:
        return self.__controller_last

    def new_counter(self):
        self.__counter = -1

    def next_event(self) -> (Event, Event):
        self.__counter += 1
        return self.__sequence[self.__counter]

    def check_counter(self) -> bool:
        return self.__counter < len(self.__sequence) - 1

    def append(self, ein: Event, eout: Event):
        self.__sequence.append((ein, eout))

    def __str__(self):
        s = ""

        if self.__plant_root is not None:
            s += "root: " + self.__plant_root.__str__() + "\n"

        for e in self.__sequence:
            s += e[0].__str__() + " -> " + e[1].__str__() + "\n"

        return s


class TraceList:
    __traces = []
    __counter = -1

    def __init__(self, files: list, location: str, old=None):
        if old is not None:
            self.__traces = list(old.__traces)
            self.__counter = -1
            return

        traces = []
        self.__counter = -1

        for f in files:
            inp = open(location + "/" + f, "r")
            size = inp.readline()

            for s in inp.readlines():
                if s[-1] == "\n":
                    s = s[:-1]

                traces.append(Trace(s))

        self.__traces = traces

    def __str__(self):
        s = ""

        for trace in self.__traces:
            s += trace.__str__() + "\n"

        return s

    def append(self, traces: [Trace]):
        self.__traces += traces

    def new_counter(self):
        self.__counter = -1

    def next_trace(self) -> Trace:
        self.__counter += 1
        return self.__traces[self.__counter]

    def check_counter(self) -> bool:
        return self.__counter < len(self.__traces) - 1

    def transform_all(self):
        self.__counter = -1

        for trace in self.__traces:
            trace.transform()

    def build_trees(self, skip_list: list) -> (Tree, PlantTree):
        controller_tree = Tree()
        plant_tree = PlantTree()

        vertex_event = []

        for trace in self.__traces:
            trace.new_counter()

            current = controller_tree.root

            while trace.check_counter():
                (ei, eo) = trace.next_event()

                next = None

                for e in controller_tree.E:
                    if e.u == current and e.e_in == ei.name and e.x == ei.variables:
                        next = e.v
                        break

                if next is not None:
                    vertex_event.append((next, eo))
                    current = next
                    continue

                next = controller_tree.add_vertex(eo.name, eo.variables, last=not trace.check_counter())

                vertex_event.append((next, eo))

                controller_tree.add_edge(current, next, ei.name, ei.variables)

                current = next

            trace.transform()

            trace.new_counter()

            current = None
            p_root = trace.plant_root()

            for root in plant_tree.root:
                if root.z == p_root.variables and root.e_out == p_root.name:
                    current = root
                    break

            if current is None:
                root_vars = []

                for i in range(0, len(p_root.variables)):
                    if i not in skip_list:
                        root_vars.append(p_root.variables[i])

                current = plant_tree.add_vertex(p_root.name, root_vars)
                plant_tree.root.append(current)

            while trace.check_counter():
                (ei, eo) = trace.next_event()

                eo_vars = []

                for i in range(0, len(eo.variables)):
                    if i not in skip_list:
                        eo_vars.append(eo.variables[i])

                next = None

                for e in plant_tree.E:
                    if e.u == current and e.e_in == ei.name and e.x == ei.variables and eo_vars == e.v.z:
                        next = e.v
                        break

                if next is not None:
                    current = next
                    continue

                next = plant_tree.add_vertex(eo.name, eo_vars)

                vert = None

                for (v, e) in vertex_event:
                    if ei == e:
                        vert = v
                        break

                plant_tree.add_edge(current, next, ei.name, ei.variables, vert)

                current = next

            trace.transform()

        return controller_tree, plant_tree

    def build_tree(self) -> Tree:
        tree = Tree()

        for trace in self.__traces:
            trace.new_counter()

            current = tree.root

            while trace.check_counter():
                (ei, eo) = trace.next_event()

                # print(ei)
                # print(eo)

                next = None

                for e in tree.E:
                    if e.u == current and e.e_in == ei.name and e.x == ei.variables:
                        next = e.v
                        break

                if next is not None:
                    current = next
                    continue

                next = tree.add_vertex(eo.name, eo.variables, last=not trace.check_counter())
                tree.add_edge(current, next, ei.name, ei.variables)

                current = next

        return tree

    def build_plant_tree(self, skip_list: list) -> Tree:
        tree = Tree()
        roots = []

        for trace in self.__traces:
            trace.new_counter()

            current = None
            p_root = trace.plant_root()

            for root in roots:
                if root.z == p_root.variables and root.e_out == p_root.name:
                    current = root
                    break

            if current is None:
                root_vars = []

                for i in range(0, len(p_root.variables)):
                    if i not in skip_list:
                        root_vars.append(p_root.variables[i])

                current = tree.add_vertex(p_root.name, root_vars)
                roots.append(current)

            while trace.check_counter():
                (ei, eo) = trace.next_event()

                eo_vars = []

                for i in range(0, len(eo.variables)):
                    if i not in skip_list:
                        eo_vars.append(eo.variables[i])

                next = None

                for e in tree.E:
                    if e.u == current and e.e_in == ei.name and e.x == ei.variables and eo_vars == e.v.z:
                        next = e.v
                        break

                if next is not None:
                    current = next
                    continue

                next = tree.add_vertex(eo.name, eo_vars)

                tree.add_edge(current, next, ei.name, ei.variables)

                current = next

        root_has_edges = False

        for e in tree.E:
            if e.u == tree.root:
                roots.append(tree.root)
                root_has_edges = True

        if not root_has_edges:
            tree.V.pop(0)

            for v in tree.V:
                v.i -= 1

        tree.root = roots

        return tree

