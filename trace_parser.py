from tree import LinkedNode


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


def build_tree(traces: list, with_self_links: bool):
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


def build_from_names(names: list, with_self_links: bool):
    traces = []

    for name in names:
        traces += read_traces(name)

    return build_tree(traces, with_self_links)
