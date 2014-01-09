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

        self._with_qt = with_qt

        lst = os.path.basename(fname).split("-", 1)
        self.tier = lst[0]
        self.name = lst[1].replace(".dot", "")

        # A dict of target => set([targets])
        self._target_dict = {}

        src = yapgvb.Graph().read(fname)

        for node in src.nodes:
            if node.shape in TARGET_SHAPES and self._want(node):
                self._target_dict[target_from_node(node)] = set()

        for edge in src.edges:
            target = target_from_node(edge.tail)
            if target in self._target_dict and self._want(edge.head):
                dep_target = target_from_node(edge.head)
                self._target_dict[target].add(dep_target)

    def get_targets(self):
        return self._target_dict.keys()

    def has_target(self, target):
        return target in self._target_dict

    def get_all_target_dependencies(self):
        deps = self._target_dict.values()
        if not deps:
            return set()
        return reduce(lambda x,y: x.union(y), deps)

    def get_dependencies_for_target(self, target):
        return self._target_dict[target]

    def _want(self, node):
        if node.shape not in TARGET_SHAPES and node.shape != DEPS_SHAPE:
            return False
        name = node.name

        for pattern in DEPS_BLACKLIST:
            if fnmatch.fnmatchcase(node.name, pattern):
                return False
        if not self._with_qt and name.startswith("Qt"):
            return False
        return True

    def __repr__(self):
        return self.name
