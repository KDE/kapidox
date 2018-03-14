# -*- coding: utf-8 -*-
#
# Copyright 2014  Alex Merry <alex.merry@kdemail.net>
# Copyright 2014  Aurélien Gâteau <agateau@kde.org>
# Copyright 2014  Alex Turbov <i.zaufi@gmail.com>
# Copyright 2016  Olivier Churlaud <olivier@churlaud.com>
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

import logging
import os
import shutil
import sys
import tempfile

if sys.version_info.major < 3:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve

from . import generator, utils, argparserutils, preprocessing

try:
    from kapidox import depdiagram
    DEPDIAGRAM_AVAILABLE = True
except ImportError:
    DEPDIAGRAM_AVAILABLE = False


def do_it(maintainers_fct, copyright, searchpaths=None):
    utils.setup_logging()
    if searchpaths is None:
        searchpaths = searchpaths=['/usr/share/doc/qt5', '/usr/share/doc/qt']
    args = argparserutils.parse_args(DEPDIAGRAM_AVAILABLE)

    if len(os.listdir(os.getcwd())) > 0:
        logging.error("Run this command from an empty directory.")
        exit(2)

    if not DEPDIAGRAM_AVAILABLE:
        logging.warning("Missing Graphviz dependency: diagrams will not be generated.")

    tagfiles = generator.search_for_tagfiles(
        suggestion=args.qtdoc_dir,
        doclink=args.qtdoc_link,
        flattenlinks=args.qtdoc_flatten_links,
        searchpaths=searchpaths)

    rootdir = args.sourcesdir
    maintainers = maintainers_fct()

    metalist = preprocessing.parse_tree(rootdir)
    products, groups, libraries, available_platforms = preprocessing.sort_metainfo(metalist, maintainers)

    dirsrc = os.path.join(args.doxdatadir, 'htmlresource')
    dirdest = 'resources'
    if os.path.isdir(dirdest):
        shutil.rmtree(dirdest)
    shutil.copytree(dirsrc, dirdest)
    os.rename(dirdest+'/favicon.ico', './favicon.ico')

    generator.process_toplevel_html_file('index.html',
                               args.doxdatadir,
                               title=args.title,
                               products=products,
                               qch_enabled=args.qhp
                               )
    generator.process_subgroup_html_files('index.html',
                                args.doxdatadir,
                                title=args.title,
                                groups=groups,
                                available_platforms=available_platforms,
                                qch_enabled=args.qhp
                                )
    tmp_dir = tempfile.mkdtemp(prefix='kapidox-')

    try:
        if args.depdiagram_dot_dir:
            dot_files = utils.find_dot_files(args.depdiagram_dot_dir)
            assert(dot_files)
        for lib in libraries:
            logging.info('# Generating doc for {}'.format(lib.fancyname))
            if args.depdiagram_dot_dir:
                png_path = os.path.join(tmp_dir, lib.name) + '.png'
                ok = generator.generate_diagram(png_path, lib.fancyname,
                                      dot_files, tmp_dir)
                if ok:
                    lib.dependency_diagram = png_path

            # store this as we won't use that everytime
            create_qhp = args.qhp
            args.qhp = False
            ctx = generator.create_fw_context(args, lib, tagfiles)
            # set it back
            args.qhp = create_qhp

            generator.gen_fw_apidocs(ctx, tmp_dir)
            tagfiles.insert(0, generator.create_fw_tagfile_tuple(lib))

        # Rebuild for interdependencies
        for lib in libraries:
            logging.info('# Rebuilding {} for interdependencies'
                         .format(lib.fancyname))
            shutil.rmtree(lib.outputdir)
            ctx = generator.create_fw_context(args, lib, tagfiles, copyright)
            generator.gen_fw_apidocs(ctx, tmp_dir)
            generator.finish_fw_apidocs(ctx, None)
            logging.info('# Generate indexing files')
            generator.indexer(lib)
        for product in products:
            generator.create_product_index(product)
            if product.logo_url is not None:
                logodir = os.path.dirname(product.logo_url)
                if not os.path.isdir(logodir):
                    os.mkdir(logodir)
                shutil.copy(product.logo_url_src, product.logo_url)
        generator.create_global_index(products)
        if args.qhp:
            logging.info('# Merge qch files'
                         .format(lib.fancyname))
            generator.create_qch(products, tagfiles)
        logging.info('# Done')
    finally:
        if args.keep_temp_dirs:
            logging.info('Kept temp dir at {}'.format(tmp_dir))
        else:
            shutil.rmtree(tmp_dir)
