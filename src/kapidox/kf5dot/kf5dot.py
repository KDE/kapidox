#!/usr/bin/env python
# encoding: utf-8
import argparse
import os
import re
import shutil
import sys
import tempfile

import yapgvb

DESCRIPTION = """\
"""

def preprocess(fname):
    lst = []
    gfx = yapgvb.Graph().read(fname)
    txt = open(fname).read()
    targets = []
    for node in gfx.nodes:
        label = node.label.replace("KF5::", "")
        if node.shape == Framework.TARGET_SHAPE:
            targets.append(label)
        txt = txt.replace('"' + node.name + '"', '"' + label + '"')

    # Sometimes cmake will generate an entry for the target alias, something
    # like this:
    #
    # "node9" [ label="KParts" shape="polygon"];
    # ...
    # "node15" [ label="KF5::KParts" shape="ellipse"];
    # ...
    #
    # After our node renaming, this ends up with a second "KParts" node
    # definition, which we need to get rid of.
    for target in targets:
        rx = r' *"' + target + '".*label="KF5::' + target + '".*shape="ellipse".*;'
        txt = re.sub(rx, '', txt)
    return txt


def to_temp_file(dirname, fname, content):
    tier = fname.split("/")[-3]
    path = os.path.join(dirname, tier + "-" + os.path.basename(fname))
    if os.path.exists(path):
        raise Exception("{} already exists".format(path))
    open(path, "w").write(content)
    return path


class Framework(object):
    TARGET_SHAPE = "polygon"
    DEPS_SHAPE = "ellipse"

    def __init__(self, fname, options):
        self.options = options

        lst = os.path.basename(fname).split("-")
        self.tier = lst[0]
        self.name = lst[1].replace(".dot", "")

        # Target names
        self.targets = set([])

        # lists of (tail, head) tuples
        self.edges = []

        src = yapgvb.Graph().read(fname)

        for node in src.nodes:
            if node.shape == self.TARGET_SHAPE:
                self.targets.add(node.name)
        for edge in src.edges:
            if self.want(edge.head) and self.want(edge.tail):
                self.edges.append((edge.tail.name, edge.head.name))

    def want(self, node):
        if node.shape not in (Framework.TARGET_SHAPE, Framework.DEPS_SHAPE):
            return False
        name = node.name
        if not name[0].isupper():
            return False
        if "test" in name:
            return False
        if not self.options.qt and name.startswith("Qt"):
            return False
        if name.endswith("Test") or name.endswith("Tests"):
            return False
        return True


class DotWriter(object):
    def __init__(self, frameworks, out):
        self.frameworks = frameworks
        self.out = out

    def write(self):
        PROLOG = \
"""
digraph Root {
    node [
        fontsize = "12"
    ];

"""
        self.out.write(PROLOG)
        qt_nodes = set([])
        for fw in self.frameworks:
            self.out.write("Subgraph cluster_" + fw.tier + " {\n")
            self.out.write("label = \"{}\";\n".format(fw.tier))
            self.out.write("color = lightgrey;\n")
            self.out.write("style = filled;\n")
            self.write_subgraph(fw.name, fw.targets)
            for edge in fw.edges:
                head = edge[1]
                if head.startswith("Qt"):
                    qt_nodes.add(head)
            self.out.write("}\n")

        self.write_subgraph("Qt", qt_nodes)

        self.out.write("    // Relations\n");
        for fw in self.frameworks:
            for edge in fw.edges:
                self.out.write('    "{}" -> "{}";\n'.format(edge[0], edge[1]))
        self.out.write("}\n")

    def write_subgraph(self, title, nodes):
        self.out.write("Subgraph cluster_{} {{\n".format(title))
        self.out.write("node [shape = box];\n")
        self.out.write("style = dashed;\n")
        self.out.write("label = \"{}\";\n".format(title))
        self.write_nodes(nodes)
        self.out.write("}\n")

    def write_nodes(self, nodes):
        for node in nodes:
            self.out.write('    "{}" [ label="{}" ];\n'.format(node, node))


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument("-o", "--output", dest="output",
        help="Output to FILE", metavar="FILE")

    parser.add_argument("--qt", dest="qt", action="store_true",
        help="Show Qt libraries")

    parser.add_argument("dot_files", nargs="+")

    args = parser.parse_args()

    tmpdir = tempfile.mkdtemp(prefix="kf5dot")
    try:
        input_files = [to_temp_file(tmpdir, x, preprocess(x)) for x in args.dot_files]
        frameworks = [Framework(x, args) for x in input_files]
    finally:
        shutil.rmtree(tmpdir)

    if args.output == "-":
        out = sys.stdout
    else:
        out = open(args.output, "w")
    writer = DotWriter(frameworks, out)
    writer.write()

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
