# KDE Doxygen Tools

## Introduction

This framework contains scripts and data for building API documentation (dox) in
a standard format and style.

The Doxygen tool is used to do the actual documentation extraction and
formatting, but this framework provides a wrapper script to make generating the
documentation more convenient (including reading settings from the target
framework or other module) and a standard template for the generated
documentation.


## Dependencies

Python 2 or 3 is required to run the scripts.  Whichever version of python you
use needs to have the pystache and yaml (or pyyaml) modules.  To generate the
dependency diagrams, you need the yapgvb module.

The following command should install them for the current user:

    pip install --user PyYAML pystache yapgvb


## Installation

Unlike almost every other KDE module, kapidox does not use CMake.  This is
because it is purely written in Python, and so uses distutils.  While it does
not need to be installed to be used (see below), you can install kapidox with

    python setup.py install

Note: For consistency, kapidox provides a CMakeLists.txt file, but this is just
a wrapper around the setup.py script.


## Writing documentation

Writing dox is beyond the scope of this documentation -- see the notes at
<http://techbase.kde.org/Policies/Library_Documentation_Policy> and the [doxygen
manual](http://www.stack.nl/~dimitri/doxygen/manual/).
However, the script expects certain things to be present in the directory it is
run on.

Most importantly, there should be a README.md file (much like this file).  The
first line of this file is particularly important, as it will be used as the
title of the documentation.

If the documentation refers to any dot files, these should be in docs/api/dot.
Images should be in docs/api/pics (or docs/pics), and snippets of example code
should be in docs/api/examples or docs/examples.  See the doxygen documentation
for help on how to refer to these files from the dox comments in the source
files.

If you need to override any doxygen settings, put them in
docs/api/Doxyfile.local.


## Generating the documentation

The tool for generating dox is `src/kgenapidox`.  Simply point it at the
folder you want to generate dox for (such as a framework checkout).

For example, if you have a checkout of KCoreAddons at
~/src/frameworks/kcoreaddons, you could run

    ~/src/frameworks/kapidox/src/kgenapidox ~/src/frameworks/kcoreaddons

and it would create a directory kcoreaddons-apidocs in the current directory.
Pass the --help argument to see options that control the behaviour of the
script.

Note that on Windows, you will need to run something like

    c:\python\python.exe c:\frameworks\kapidox\src\kgenapidox c:\frameworks\kcoreaddons


### Frameworks documentation

`src/kgenframeworksapidocs` can be used to generate a combined set of
documentation for all the frameworks.  You want to do something like

    mkdir frameworks-apidocs
    cd frameworks-apidocs
    ~/src/frameworks/kapidox/src/kgenframeworksapidox ~/src/frameworks

And (after maybe 15-30 minutes) you will get a complete set of documentation in
the frameworks-apidocs directory.  This will be about 500Mb in size, so make
sure you have enough space!


### Dependency diagrams

Kapidox can also generate dependency diagrams for the frameworks.  This is done
using two tools: `src/kf5dot-prepare` and `src/kf5dot-generate`.  The way you
use it is as follow.

First you need to prepare Graphviz dot files for all frameworks with
`src/kf5dot-prepare`:

    kf5dot-prepare ~/src/frameworks ~/dots

This will generate many .dot files in ~/dots.

Then you can generate the dependency diagrams with `src/kf5dot-generate`.  This
tool accepts a list of dot files and output a combined dot file to stdout.

Here is how to generate a dependency diagram for all the frameworks:

    kf5dot-generate ~/dots/tier*/*/*.dot | dot -Tpng > kf5.png

The diagram might be very hard to read though, so for complex diagrams, you may
want to pipe the output through the `tred` tool:

    kf5dot-generate ~/dots/tier*/*/*.dot | tred | dot -Tpng > kf5.png

You can also generate the diagram for one particular framework using the
"--framework" option:

    kf5dot-generate ~/dots/tier*/*/*.dot --framework kcrash | tred | dot -Tpng > kcrash.png

To include Qt libs, use the "--qt" option:

    kf5dot-generate ~/dots/tier*/*/*.dot --framework kcrash --qt | tred | dot -Tpng > kcrash.png

And to include targets within the framework, use the "--detailed" option:

    kf5dot-generate ~/dots/tier*/*/*.dot --framework kcrash --detailed | tred | dot -Tpng > kcrash.png


#### Useful tools

`tred`, mentioned in Usage, reduces clutter in dot files.

`xdot`, can be used instead of `dot` to display the graph:

    kf5dot-generate ~/dots/tier*/*/*.dot --framework kcrash --qt | tred | xdot


#### Generating all diagrams at once

You can use the kf5dot-generate-all tool to generate diagrams for all frameworks at once:

    kf5dot-generate-all ~/dots ~/pngs

This command creates two pngs for each framework: "$framework.png" and
"$framework-simplified.png" (same diagram, ran through tred). It also creates a
diagram for all of the frameworks, named "kf5.png".


#### Integration with kgenapidox

Once you have generated dependency diagrams, you can run kgenapidox with the
"--dependency-diagram-dir" option pointing to the dir containing the diagrams.
When this option is set, kgenapidox creates a "Dependencies" page, accessible
from the documentation sidebar. This page includes the framework diagram.


## Links

- Home page: <https://projects.kde.org/projects/frameworks/kapidox>
- Mailing list: <https://mail.kde.org/mailman/listinfo/kde-frameworks-devel>
- IRC channel: #kde-devel on Freenode
- Git repository: <https://projects.kde.org/projects/frameworks/kapidox/repository>
- KDE API documentation: <http://api.kde.org/>
