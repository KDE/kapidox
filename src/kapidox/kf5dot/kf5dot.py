#!/usr/bin/env python
# encoding: utf-8
import argparse
from contextlib import contextmanager
import itertools
import os
import re
import shutil
import sys
import tempfile

import yapgvb

DESCRIPTION = """\
"""


TIER_ATTRS = dict(style="dashed")
OTHER_ATTRS = TIER_ATTRS
FW_ATTRS = dict(style="filled", color="lightgrey")


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
        if name.startswith("Phonon"):
            return False
        if name.startswith("LibAttica"):
            return False
        return True


@contextmanager
def block(opener, closer, writer, **attrs):
    writer.writeln(opener)
    writer.indent()
    writer.write_attrs(**attrs)
    yield
    writer.unindent()
    writer.writeln(closer)

def square_block(prefix, writer, **attrs):
    return block(prefix + " [", "]", writer, **attrs)

def curly_block(prefix, writer, **attrs):
    return block(prefix + " {", "}", writer, **attrs)

def cluster_block(title, writer, **attrs):
    return curly_block("subgraph cluster_" + title, writer, label=title, **attrs)


def find_not_target_nodes(frameworks):
    nodes = set([])
    targets = set([])
    for fw in frameworks:
        targets.update(fw.targets)
        nodes.update([x[1] for x in fw.edges])
    return nodes.difference(targets)


class DotWriter(object):
    INDENT_SIZE = 4
    def __init__(self, frameworks, out):
        self.frameworks = frameworks
        self.out = out
        self.depth = 0

    def writeln(self, text):
        self.out.write(self.depth * DotWriter.INDENT_SIZE * " " + text + "\n")

    def indent(self):
        self.depth += 1

    def unindent(self):
        self.depth -= 1

    def write(self):
        with curly_block("digraph Root", self):
            with square_block("node", self):
                self.writeln("fontsize = 12")
                self.writeln("shape = box")

            other_nodes = find_not_target_nodes(self.frameworks)
            qt_nodes = set([x for x in other_nodes if x.startswith("Qt")])
            other_nodes.difference_update(qt_nodes)

            if qt_nodes:
                with cluster_block("Qt", self, **OTHER_ATTRS):
                    self.write_nodes(qt_nodes)

            if other_nodes:
                with cluster_block("Others", self, **OTHER_ATTRS):
                    self.write_nodes(other_nodes)

            for tier, frameworks in itertools.groupby(self.frameworks, lambda x: x.tier):
                with cluster_block(tier, self, **TIER_ATTRS):
                    for fw in frameworks:
                        with cluster_block(fw.name, self, **FW_ATTRS):
                            self.write_nodes(fw.targets)
                            for edge in sorted(fw.edges, key=lambda x:x[1]):
                                self.writeln('"{}" -> "{}";'.format(edge[0], edge[1]))


    def write_attrs(self, **attrs):
        for key, value in attrs.items():
            self.writeln("{} = {};".format(key, value))

    def close_block(self):
        self.out.write("}\n")

    def write_nodes(self, nodes):
        for node in sorted(nodes):
            self.writeln('"{}" [ label="{}" ];'.format(node, node))


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument("-o", "--output", dest="output", default="-",
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
