# -*- coding: utf-8 -*-
#
# Copyright 2014  Aurélien Gâteau <agateau@kde.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Python 2/3 compatibility (NB: we require at least 2.7)
from __future__ import division, absolute_import, print_function, unicode_literals

import argparse
import logging
import os
import sys


def normalized_path(inputpath):
    return os.path.normpath(inputpath)

def parse_args(depdiagram_available):
    import textwrap
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''Generate API documentations of complex projects.

>> This function must be run from an empty directory (where the documentation will be build).''')
        )
    group = add_sources_group(parser)
    group.add_argument('sourcesdir', type=normalized_path,
            help='Location of the sources.')
    group.add_argument('--depdiagram-dot-dir', type=normalized_path,
            help='Generate dependency diagrams, using the .dot files from DIR.',
            metavar="DIR")
    add_output_group(parser)
    add_qt_doc_group(parser)
    add_paths_group(parser)
    add_misc_group(parser)
    args = parser.parse_args()
    check_common_args(args)

    if args.depdiagram_dot_dir and not depdiagram_available:
        logging.error('You need to install the Graphviz Python bindings to '
                      'generate dependency diagrams.\n'
                      'See <https://www.graphviz.org/download/>.')
        exit(1)

    if not os.path.isdir(args.sourcesdir):
        logging.error(args.sourcesdir + " is not a directory")
        exit(2)

    return args


def add_sources_group(parser):
    return parser.add_argument_group('sources')


def add_output_group(parser):
    group = parser.add_argument_group('output options')
    group.add_argument('--title', default='API Documentation',
            help='String to use for page titles.')
    group.add_argument('--man-pages', action='store_true',
            help='Generate man page documentation.')
    group.add_argument('--qhp', action='store_true',
            help='Generate Qt Compressed Help documentation.')
    return group


def add_qt_doc_group(parser):
    group = parser.add_argument_group('Qt documentation')
    group.add_argument('--qtdoc-dir', type=normalized_path,
            help='Location of (local) Qt documentation; this is searched ' +
                 'for tag files to create links to Qt classes.')
    group.add_argument('--qtdoc-link',
            help='Override Qt documentation location for the links in the ' +
                 'html files.  May be a path or URL.')
    group.add_argument('--qtdoc-flatten-links', action='store_true',
            help='Whether to assume all Qt documentation html files ' +
                 'are immediately under QTDOC_LINK (useful if you set ' +
                 'QTDOC_LINK to the online Qt documentation).  Ignored ' +
                 'if QTDOC_LINK is not set.')
    return group


def add_paths_group(parser):
    group = parser.add_argument_group('paths')
    group.add_argument('--doxygen', default='doxygen', type=normalized_path,
            help='(Path to) the doxygen executable.')
    group.add_argument('--qhelpgenerator', default='qhelpgenerator', type=normalized_path,
            help='(Path to) the qhelpgenerator executable.')
    return group


def add_misc_group(parser):
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    doxdatadir = os.path.join(scriptdir, 'data')

    group = parser.add_argument_group('misc')
    group.add_argument('--doxdatadir', default=doxdatadir, type=normalized_path,
            help='Location of the HTML header files and support graphics.')
    group.add_argument('--keep-temp-dirs', action='store_true',
            help='Do not delete temporary dirs, useful for debugging.')
    return parser


def check_common_args(args):
    if not _is_doxdatadir(args.doxdatadir):
        logging.error("{} is not a valid doxdatadir".format(args.doxdatadir))
        sys.exit(1)


def _is_doxdatadir(directory):
    for name in ['header.html', 'footer.html', 'htmlresource']:
        if not os.path.exists(os.path.join(directory, name)):
            return False
    return True
