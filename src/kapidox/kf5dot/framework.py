import fnmatch
import os

import yapgvb


TARGET_SHAPES = [
    "polygon", # lib
    "house",   # executable
    "octagon", # module (aka plugin)
    "diamond", # static lib
    ]


DEPS_SHAPE = "ellipse"


DEPS_BLACKLIST = [
    "-l*", "-W*", # link flags
    "/*", # absolute dirs
    "m", "pthread", "util", "nsl", "resolv", # generic libs
    "*example*", "*demo*", "*test*", "*Test*", "*debug*" # helper targets
    ]


class Framework(object):
    def __init__(self, fname, with_qt=False):
        def target_from_node(node):
            return node.name.replace("KF5", "")

        self.with_qt = with_qt

        lst = os.path.basename(fname).split("-", 1)
        self.tier = lst[0]
        self.name = lst[1].replace(".dot", "")

        # A dict of target => set([targets])
        self.target_dict = {}

        src = yapgvb.Graph().read(fname)

        for node in src.nodes:
            if node.shape in TARGET_SHAPES and self.want(node):
                self.target_dict[target_from_node(node)] = set()

        for edge in src.edges:
            target = target_from_node(edge.tail)
            if target in self.target_dict and self.want(edge.head):
                dep_target = target_from_node(edge.head)
                self.target_dict[target].add(dep_target)

    def get_all_dependencies(self):
        deps = self.target_dict.values()
        if not deps:
            return set()
        return reduce(lambda x,y: x.union(y), deps)

    def want(self, node):
        if node.shape not in TARGET_SHAPES and node.shape != DEPS_SHAPE:
            return False
        name = node.name

        for pattern in DEPS_BLACKLIST:
            if fnmatch.fnmatchcase(node.name, pattern):
                return False
        if not self.with_qt and name.startswith("Qt"):
            return False
        return True

    def __repr__(self):
        return self.name
