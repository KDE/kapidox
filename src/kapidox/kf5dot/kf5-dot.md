# Goal

Generate a dependency graph of all frameworks, grouped by tier

Exclude low level libs like X11

Exclude secondary targets like tests

Do not duplicate KF5::Foo and Foo

Group targets within a framework (KConfig contains KConfigCore and KConfigGui,
KDED contains kded5, kdeinit_kde5)

Group by tier

# Libs

## pygraphviz

AGraph.nodes() => array of strings

## pydot

Not tried, need manual fix when used with pyparsing 2.0.1

http://stackoverflow.com/a/18547813

## yapgvb

Graph.layout() => segfault :(

# Steps

## Generate dot from cmake

    for tier in ~/src/kf5/kdelibs/tier? ; do
        for fw in $tier/*/ ; do
            echo $fw
            bfw=$PWD/$(basename $fw)
            mkdir $bfw
            ( cd $bfw ; cmake $fw --graphviz=$(basename $tier)-$(basename $fw).dot > /dev/null )
        done
    done

## Preprocess .dot files

'KF5::' => ''

replace "nodeXXX" with their label

## Remove clutter

tests

libs

dst = Graph()

for src in fw_graphs:
    for node in src.nodes:
        if not node in dst and want(node):
            dst.add_node(node.name)

    for edge in src.edges:
        if want(edge[0]) and want(edge[1]):
            dst.add_edge(*edge)
