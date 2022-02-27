# KDE Doxygen Tools

## Introduction

This framework contains scripts and data for building API documentation (dox) in
a standard format and style.
https://api.kde.org holds the result.

The [Doxygen](https://www.doxygen.nl) tool performs the actual documentation extraction and
formatting. This framework provides a wrapper script to make generating the
documentation more convenient (including reading settings from the target
framework or other module) and a standard template for the generated
documentation.


## Dependencies

## Installation
Python 3 is required to run the scripts. Additionally you
need to have the jinja2 and yaml (or pyyaml) modules.

The following command creates a venv and installs the tool:

    $ ./bootstrap-devenv.sh

### Optional
Doxyqml and doxypypy might be needed to let doxygen document qml
and python sources respectively.

To generate the dependency diagrams, you need the Graphviz Python bindings.
They are currently not available from pip, but most distributions provide them.
You can get binaries and source archives from
<https://www.graphviz.org/download/>.

## Usage

Although it should be possible to use kapidox directly it is recommended to run the tool in the docker container.

You can build the docker image like this:

    docker build . -t kapidox_generate:latest

To run `kapidox-generate` with a project that you want to generate the docs from you need an empty folder for the results (`/path/to/build/folder`). The build directory inside the container is set as `BUILD_DIR` in `Dockerfile`, and must stay in sync with what is used as `CONTAINER_BUILD_DIR` in the volume mapping.

For this example we use `libksane` checked out to `/path/to/libksane`:

```bash
export HOST_PROJECT_SRC=/path/to/libksane
export HOST_BUILD_DIR=/path/to/build/folder
export CONTAINER_PROJECT_SRC=/home/kapidox/libksane
export CONTAINER_BUILD_DIR=/home/kapidox/apidox-build
mkdir $HOST_BUILD_DIR
docker run \
    --volume $HOST_PROJECT_SRC:$CONTAINER_PROJECT_SRC \
    --volume $HOST_BUILD_DIR:$CONTAINER_BUILD_DIR \
    kapidox_generate:latest \
    kapidox-generate $CONTAINER_PROJECT_SRC
```

## Writing documentation

Writing dox is beyond the scope of this documentation -- see the notes at
<https://community.kde.org/Frameworks/Frameworks_Documentation_Policy> and the [doxygen
manual](https://doxygen.nl/manual/docblocks.html).

To allow code to handle the case of being processed by kapidox a C/C++ preprocessor macro
is set as defined when run: `K_DOXYGEN` (since v5.67.0).
For backward-compatibility the definition `DOXYGEN_SHOULD_SKIP_THIS` is also set, but
its usage is deprecated.

The kapidox scripts expects certain things to be present in the directory it is
run on:

### README.md
Most importantly, there should be a `README.md` file, like this page (backward
compatibility also authorize `Mainpage.dox` files).  The first line of this file
is particularly important, as it will be used as the title of the documentation.

### metainfo.yaml
A `metainfo.yaml` file is needed for the library to be generated. It should
contain some meta information about the library itself, its maintainers, where
the sources are, etc.

A very simple example can be:

```yaml
# metainfo.yaml
description: Library doing X
maintainer: gwashington
public_lib: true
logo: libX.png
```

A comprehensive list of the available keys can be found on
[this page](@ref metainfo_syntax).

By default, the source of the public library must be in `src`, if the
documentation refers to any dot files, these should be in `docs/dot`.
Images should be in `docs/pics`, and snippets of example code should be in
`examples`.  See the doxygen documentation for help on how to refer to these
files from the dox comments in the source files.

If you need to override any doxygen settings, put them in a `docs/Doxyfile.local` in your project.
Global settings are defined in `src/kapidox/data/Doxyfile.global`.

## Generating the documentation

The tool for generating dox is `src/kapidox_generate`.
Change to an empty directory, then simply point it at the
folder you want to generate dox for (such as a frameworks checkout).

For example, if you have a checkout of KCoreAddons at
~/kde/src/frameworks/kcoreaddons, you could run

    ~/kde/src/frameworks/kapidox/src/kapidox_generate ~/kde/src/frameworks/kcoreaddons

and it would create a documentation in the current directory, which needs to be empty before executing the command.

kapidox recursively walks through folders, so you can also run it on
`~/kde/src/frameworks` or `~/src`. For a lot of libraries, the generation can last
15-30 minutes and use several hundreds of MB, so be prepared!

Pass the --help argument to see options that control the behaviour of the
script.

Note that on Windows, you will need to run something like

    c:\python\python.exe c:\frameworks\kapidox\src\kapidox_generate c:\frameworks\kcoreaddons

## Specific to frameworks (for now)

You can ask `kgenframeworksapidox` to generate dependency diagrams for all the
frameworks.  To do so, you must first generate Graphviz .dot files for all
frameworks with the `depdiagram-prepare` tool, like this:

    mkdir dot
    ~/kde/src/frameworks/kapidox/src/depdiagram-prepare --all ~/kde/src/frameworks dot

Then call `kgenframeworksapidox` with the `--depdiagram-dot-dir` option, like
this:

    mkdir frameworks-apidocs
    cd frameworks-apidocs
    ~/kde/src/frameworks/kapidox/src/kapidox_generate --depdiagram-dot-dir ../dot ~/kde/src/frameworks

More fine-grained tools are available for dependency diagrams. You can learn
about them in [depdiagrams](@ref depdiagrams).


## Examples of generated pages:

- KDE API documentation: <https://api.kde.org/>

## Licensing

This project is licensed under BSD-2-Clause. But the specific theme used inside KDE
is licensed under AGPL-3.0-or-later. If you find the AGPL to restrictive you can
alternatively use the theme from [Docsy](https://github.com/google/docsy) (APACHE-2.0).
For that you need to replace the style and js script present in `src/kapidox/data/templates/base.html`.

If you need support or licensing clarification, feel free to contact the maintainers.
