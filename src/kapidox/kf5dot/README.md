# Goal

Generate a dependency graph of all frameworks, grouped by tier

Exclude low level libs like X11

Exclude secondary targets like tests

Do not duplicate KF5::Foo and Foo

Group targets within a framework (KConfig contains KConfigCore and KConfigGui,
KDED contains kded5, kdeinit_kde5)

# Dependencies

- Python
- dot tool from Graphviz <http:://graphviz.org>
- cmake
- yapgvb: Python bindings for Graphviz <https://code.google.com/p/yapgvb/>

# Usage

1. Prepare dot files

    kf5dot-prepare path/to/kdelibs dst/path/to/dot-files

2. Generate graphs

    kf5dot-generate dst/path/to/dot-files/tier*/*/*.dot | tred | dot -Tpng > kf5.png

There are many ways to generate graphs:

- Generate a graph for kcrash:

    kf5dot-generate dst/path/to/dot-files/tier*/*/*.dot --framework kcrash | tred | dot -Tpng > kcrash.png

- Including Qt libs:

    kf5dot-generate dst/path/to/dot-files/tier*/*/*.dot --framework kcrash --qt | tred | dot -Tpng > kcrash.png

# Useful tools

`tred`, mentioned in Usage, reduces clutter in dot files.

`xdot`, can be used instead of `dot` to display the graph:

    kf5dot-generate dst/path/to/dot-files/tier*/*/*.dot --framework kcrash --qt | tred | xdot
