# KDE Doxygen Tools

## Introduction

This framework contains scripts and data for building API documentation (dox) in
a standard format and style.

The Doxygen tool is used to do the actual documentation extraction and
formatting, but this framework provides a wrapper script to make generating the
documentation more convenient (including reading settings from the target
framework or other module) and a standard template for the generated
documentation.

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

The tool for generating dox is `src/kgenapidox.py`.  Simply point it at the
folder you want to generate dox for (such as a framework checkout).

For example, if you have a checkout of KCoreAddons at
~/src/frameworks/kcoreaddons, you could run

    ~/src/frameworks/kapidox/src/kgenapidox.py ~/src/frameworks/kcoreaddons

and it would create a directory kcoreaddons-apidocs in the current directory.
Pass the --help argument to see options that control the behaviour of the
script.


### Frameworks documentation

`src/kgenframeworksapidocs.py` can be used to generate a combined set of
documentation for all the frameworks.  You want to do something like

    mkdir frameworks-apidocs
    cd frameworks-apidocs
    ~/src/frameworks/kapidox/src/kgenframeworksapidox.py ~/src/frameworks

And (after maybe 15-30 minutes) you will get a complete set of documentation in
the frameworks-apidocs directory.  This will be about 500Mb in size, so make
sure you have enough space!


## Links

- Mailing list: <https://mail.kde.org/mailman/listinfo/kde-frameworks-devel>
- IRC channel: #kde-devel on Freenode
- Git repository: <https://projects.kde.org/projects/frameworks/kapidox/repository>
