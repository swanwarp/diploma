from tree import LinkedNode, to_tree, Tree
from enum import Enum
from re import split


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


class EventType(Enum):
    IN = "in"
    OUT = "out"


class Event:
    name = ""
    variables = []
    t = None

    def __init__(self, s: str):
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


class Trace:
    __sequence = []
    __counter = 0
    __plant_root = None

    def __init__(self, trace: str, for_plant: bool):
        self.__counter = -1

        s = split(" +", trace)
        sequence = []

        if s[len(s) - 1] == "":
            s.pop(len(s) - 1)

        if not for_plant:
            last = s.pop(0)

            while len(s) != 0:
                event = s.pop(0)

                if event[0:3] == "out":
                    sequence.append((Event(last), Event(event)))

                last = event
        else:
            last = None

            while not s[0][0:3] == "out":
                last = s.pop(0)

            self.__plant_root = Event(last)

            while len(s) != 0:
                last = s.pop(0)

                if last[0:3] == "out":
                    event = None

                    while not s[0][0:3] == "out":
                        event = s.pop(0)
                        if len(s) == 0:
                            break

                    sequence.append((Event(last), Event(event)))

        self.__sequence = sequence

    def plant_root(self) -> Event:
        return self.__plant_root

    def new_counter(self):
        self.__counter = -1

    def next_event(self) -> (Event, Event):
        self.__counter += 1
        return self.__sequence[self.__counter]

    def check_counter(self) -> bool:
        return self.__counter < len(self.__sequence) - 1

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

    def __init__(self, files: list, location: str, for_plant: bool):
        traces = []
        self.__counter = -1

        for f in files:
            inp = open(location + "/" + f, "r")
            size = inp.readline()

            for s in inp.readlines():
                if s[-1] == "\n":
                    s = s[:-1]

                traces.append(Trace(s, for_plant))

        self.__traces = traces

    def __str__(self):
        s = ""

        for trace in self.__traces:
            s += trace.__str__() + "\n"

        return s

    def new_counter(self):
        self.__counter = -1

    def next_trace(self) -> Trace:
        self.__counter += 1
        return self.__traces[self.__counter]

    def check_counter(self) -> bool:
        return self.__counter < len(self.__traces) - 1

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

                next = tree.add_vertex(eo.name, eo.variables)
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

