#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014  Alex Merry <alex.merry@kdemail.net>
# Copyright 2014  Aurélien Gâteau <agateau@kde.org>
# Copyright 2014  Alex Turbov <i.zaufi@gmail.com>
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
import datetime
import logging
import codecs
import os
import shutil
import string
import subprocess
import tempfile

import yaml

from kapidox import argparserutils
from kapidox import utils
from kapidox import generator
try:
    from kapidox import depdiagram
    DEPDIAGRAM_AVAILABLE = True
except ImportError:
    DEPDIAGRAM_AVAILABLE = False

PLATFORM_ALL = "All"
PLATFORM_UNKNOWN = "UNKNOWN"

def serialize_name(name):
    if name is not None:
        return '_'.join(name.lower().split(' '))
    else:
        return None

def create_metainfo(frameworksdir, path):
    if not os.path.isdir(path):
        return None

    metainfo_file = os.path.join(path, 'metainfo.yaml')
    if not os.path.isfile(metainfo_file):
        #logging.warning('{} does not contain a library (metainfo.yml missing)'.format(path))
        return None

    # FIXME: option in yaml file to disable docs
    try:
        metainfo = yaml.load(open(metainfo_file))
    except:
        logging.warning('Could not load config.kapidox for {}, skipping it'.format(path))
        return None

    if metainfo is None:
        logging.warning('Empty metainfo.yml for {}, skipping it'.format(path))
        return None

    if 'subgroup' in metainfo and 'group' not in metainfo:
        logging.warning('Subgroup but no group in {}, skipping it'.format(path))
        return None

    name = path.split('/')[-1]
    fancyname = utils.parse_fancyname(path)
    if not fancyname:
        logging.warning('Could not find fancy name for {}, skipping it'.format(path))
        return None

    metainfo.update({
        'fancyname': fancyname,
        'name': name,
        'public_lib': metainfo.get('public_lib', False),
        'dependency_diagram': None,
        'path': path,
        })

    return metainfo


def sort_metainfo(metalist, all_maintainers):

    def get_logo_url(dct, name):
        # take care of the logo
        if 'logo' in dct:
            logo_url = os.path.join(metainfo['path'], dct['logo'])
            if os.path.isfile(logo_url):
                return logo_url
            else:
                logging.warning("{} logo file doesn't exist, set back to None".format(name))
                return None
        else:
            return None

    products = []
    groups = []
    libraries = []
    available_platforms = set(['Windows', 'MacOSX', 'Linux'])

    for metainfo in metalist:
        outputdir = metainfo.get('name')
        if 'group' in metainfo:
            outputdir = metainfo.get('group') + '/' + outputdir
        outputdir = serialize_name(outputdir)

        try:
            platforms = metainfo['platforms']
            #platform_info = metainfo['platforms']
            platform_lst = [x['name'] for x in platforms if x['name'] not in (PLATFORM_ALL, PLATFORM_UNKNOWN)]
            available_platforms.update(set(platform_lst))
        except (KeyError, TypeError):
            logging.warning('{} framework lacks valid platform definitions'.format(metainfo['fancyname']))
            platforms = [dict(name=PLATFORM_UNKNOWN)]

        dct = dict((x['name'], x.get('note', '')) for x in platforms)

        expand_platform_all(dct, available_platforms)
        platforms = dct

        lib = {
            'name': metainfo['name'],
            'fancyname': metainfo['fancyname'],
            'description': metainfo.get('description'),
            'maintainers': set_maintainers(metainfo, 'maintainer', all_maintainers),
            'platforms': platforms,
            'parent': {'group': serialize_name(metainfo.get('group')), 'subgroup': serialize_name(metainfo.get('subgroup'))},
            'href': '../'+outputdir.lower() + '/html/index.html',
            'outputdir': outputdir.lower(),
            'path':  metainfo['path'],
            'srcdirs':  metainfo.get('public_source_dirs', ['src']),
            'docdir':  metainfo.get('public_doc_dir', 'docs'),
            'exampledir':  metainfo.get('public_example_dir', 'examples'),
            'dependency_diagram': None,
            'type': metainfo.get('type', ''),
            'portingAid': metainfo.get('portingAid', False),
            'deprecated': metainfo.get('deprecated', False),
            'libraries': metainfo.get('libraries', []),
            'cmakename': metainfo.get('cmakename', '')
        }
        libraries.append(lib)

        # if there is a group, the product is the group
        # else the product is directly the library
        if 'group_info' in metainfo:

            product = {
                'name': serialize_name(metainfo['group']),
                'fancyname': metainfo['group_info'].get('fancyname', string.capwords(metainfo['group'])),
                'description': metainfo['group_info'].get('description'),
                'long_description': metainfo['group_info'].get('long_description', []),
                'maintainers': set_maintainers(metainfo['group_info'], 'maintainer', all_maintainers),
                'platforms': metainfo['group_info'].get('platforms'),
                'logo_url': get_logo_url(metainfo['group_info'], metainfo['group']),
                'href': serialize_name(metainfo['group']) + '/index.html',
                'outputdir': serialize_name(metainfo['group']),
                'libraries': []
            }
            subgroups = []
            if 'subgroups' in metainfo['group_info']:
                for sg in metainfo['group_info']['subgroups']:
                    if 'name' in sg:
                        subgroups.append({
                            'fancyname': sg['name'],
                            'name': serialize_name(sg['name']),
                            'description': sg.get('description'),
                            'libraries': []
                        })
            product['subgroups'] = subgroups;
            products.append(product)
        elif 'group' not in metainfo:
            products.append({
                'name': serialize_name(metainfo['name']),
                'fancyname': metainfo['fancyname'],
                'description': metainfo.get('description'),
                'maintainers': set_maintainers(metainfo, 'maintainer', all_maintainers),
                'platform': metainfo.get('platform'),
                'logo_url': get_logo_url(metainfo, metainfo['fancyname']),
                'href': metainfo['name']+'/html/index.html',
                'outputdir': metainfo['name']
            })

    # We have all groups and libraries, let set the parents.
    # and check the platforms
    for lib in libraries:
        if lib['parent'].get('group') is not None:
            product = [x for x in products if x['name'].lower() == lib['parent']['group'].lower()][0]
            lib['product'] = product
            product['libraries'].append(lib)
            if lib['parent'].get('subgroup') is None:
                lib['subgroup'] = None
            else:
                subgroup_list = [x for x in lib['product']['subgroups'] if x['name'].lower() == lib['parent']['subgroup'].lower()]
                if not subgroup_list:
                    logging.warning("Subgroup {} of library {} not documentated, setting subgroup to None"
                                    .format(lib['parent']['subgroup'], lib['name']))
                    lib['subgroup'] = None
                    lib['parent'] = None
                else:
                    subgroup = subgroup_list[0]
                    lib['subgroup'] = subgroup
                    subgroup['libraries'].append(lib)
        else:
            lib['parent'] = None

        groups.append(product)

    return products, groups, libraries, available_platforms

def expand_platform_all(dct, available_platforms):
    """If one of the keys of dct is PLATFORM_ALL (or PLATFORM_UNKNOWN), remove it and add entries for all available platforms to dct"""
    add_all_platforms = False
    if PLATFORM_ALL in dct:
        note = dct[PLATFORM_ALL]
        add_all_platforms = True
        del dct[PLATFORM_ALL]
    if PLATFORM_UNKNOWN in dct:
        add_all_platforms = True
        note = dct[PLATFORM_UNKNOWN]
        del dct[PLATFORM_UNKNOWN]
    if add_all_platforms:
        for platform in available_platforms:
            if not platform in dct:
                dct[platform] = note


def process_toplevel_html_file(outputfile, doxdatadir, products, title,
        api_searchbox=False):

    products.sort(key=lambda x: x['name'].lower())
    mapping = {
            'resources': '.',
            'api_searchbox': api_searchbox,
            # steal the doxygen css from one of the frameworks
            # this means that all the doxygen-provided images etc. will be found
            'doxygencss': products[0]['outputdir'] + '/html/doxygen.css',
            'title': title,
            'breadcrumbs': {
                'entries': [
                    {
                        'href': './index.html',
                        'text': 'KDE API Reference'
                    }
                    ]
                },
            'product_list': products,
        }
    tmpl = generator.create_jinja_environment(doxdatadir).get_template('frontpage.html')
    with codecs.open(outputfile, 'w', 'utf-8') as outf:
        outf.write(tmpl.render(mapping))

def process_subgroup_html_files(outputfile, doxdatadir, groups, available_platforms, title,
                                api_searchbox=False):

    for group in groups:
        mapping = {
            'resources': '..',
            'api_searchbox': api_searchbox,
            # steal the doxygen css from one of the frameworks
            # this means that all the doxygen-provided images etc. will be found
            'doxygencss': group['libraries'][0]['outputdir'] + '/html/doxygen.css',
            'title': title,
            'breadcrumbs': {
                'entries': [
                    {
                        'href': '../index.html',
                        'text': 'KDE API Reference'
                    },
                    {
                        'href': './index.html',
                        'text': group['fancyname']
                    }
                    ]
                },
            'group': group,
            'available_platforms': sorted(available_platforms),
        }

        if not os.path.isdir(group['name']):
            os.mkdir(group['name'])
        outputfile = group['name']+'/index.html'
        tmpl = generator.create_jinja_environment(doxdatadir).get_template('subgroup.html')
        with codecs.open(outputfile, 'w', 'utf-8') as outf:
            outf.write(tmpl.render(mapping))

def find_dot_files(dot_dir):
    """Returns a list of path to files ending with .dot in subdirs of `dot_dir`."""
    lst = []
    for (root, dirs, files) in os.walk(dot_dir):
        lst.extend([os.path.join(root, x) for x in files if x.endswith('.dot')])
    return lst


def generate_diagram(png_path, fancyname, dot_files, tmp_dir):
    """Generate a dependency diagram for a framework.
    """
    def run_cmd(cmd, **kwargs):
        try:
            subprocess.check_call(cmd, **kwargs)
        except subprocess.CalledProcessError as exc:
            logging.error(
                    'Command {exc.cmd} failed with error code {exc.returncode}.'.format(exc=exc))
            return False
        return True

    logging.info('Generating dependency diagram')
    dot_path = os.path.join(tmp_dir, fancyname + '.dot')

    with open(dot_path, 'w') as f:
        with_qt = False
        ok = depdiagram.generate(f, dot_files, framework=fancyname, with_qt=with_qt)
        if not ok:
            logging.error('Generating diagram failed')
            return False

    logging.info('- Simplifying diagram')
    simplified_dot_path = os.path.join(tmp_dir, fancyname + '-simplified.dot')
    with open(simplified_dot_path, 'w') as f:
        if not run_cmd(['tred', dot_path], stdout=f):
            return False

    logging.info('- Generating diagram png')
    if not run_cmd(['dot', '-Tpng', '-o' + png_path, simplified_dot_path]):
        return False

    # These os.unlink() calls are not in a 'finally' block on purpose.
    # Keeping the dot files around makes it possible to inspect their content
    # when running with the --keep-temp-dirs option. If generation fails and
    # --keep-temp-dirs is not set, the files will be removed when the program
    # ends because they were created in `tmp_dir`.
    os.unlink(dot_path)
    os.unlink(simplified_dot_path)
    return True


def set_maintainers(dictionary, key, maintainers):
    if key not in dictionary:
        fw_maintainers = []
    elif isinstance(dictionary[key], list):
        fw_maintainers = map(lambda x: maintainers.get(x, None),
                             dictionary[key])
    else:
        fw_maintainers = [maintainers.get(dictionary[key], None)]

    fw_maintainers = [x for x in fw_maintainers if x is not None]
    return fw_maintainers


def create_fw_context(args, lib, tagfiles):
    return generator.Context(args,
                            # Names
                            modulename=lib['name'],
                            fancyname=lib['fancyname'],
                            fwinfo=lib,
                            # KApidox files
                            resourcedir='../..' if lib['parent'] is None else '../../..',
                            # Input
                            #srcdir=lib['srcdir'],
                            tagfiles=tagfiles,
                            dependency_diagram=lib['dependency_diagram'],
                            # Output
                            outputdir=lib['outputdir'],
                            )

def gen_fw_apidocs(ctx, tmp_base_dir):
    generator.create_dirs(ctx)
    # tmp_dir is deleted when tmp_base_dir is
    tmp_dir = tempfile.mkdtemp(prefix=ctx.modulename + '-', dir=tmp_base_dir)
    generator.generate_apidocs(ctx, tmp_dir,
            doxyfile_entries=dict(WARN_IF_UNDOCUMENTED=True)
            )

def finish_fw_apidocs(ctx, group_menu):
    classmap = generator.build_classmap(ctx.tagfile)
    generator.write_mapping_to_php(classmap, os.path.join(ctx.outputdir, 'classmap.inc'))

    entries = [{
        'href': '../../index.html',
        'text': 'KDE API Reference'
        }]
    if ctx.fwinfo['parent'] is not None:
        entries[0]['href'] = '../' + entries[0]['href']
        entries.append({
            'href': '../../index.html',
            'text': ctx.fwinfo['product']['fancyname']
            })
    entries.append({
        'href': 'index.html',
        'text': ctx.fancyname
        })

    template_mapping={
                'breadcrumbs': {
                    'entries': entries
                    },
                #'group_menu': group_menu
                }
    copyright = '1996-' + str(datetime.date.today().year) + ' The KDE developers'
    mapping = {
            'doxygencss': 'doxygen.css',
            'resources': ctx.resourcedir,
            'title': ctx.title,
            'fwinfo': ctx.fwinfo,
            'copyright': copyright,
            'api_searchbox': ctx.api_searchbox,
            'doxygen_menu': {'entries': generator.menu_items(ctx.htmldir, ctx.modulename)},
            'class_map': {'classes': classmap},
            'kapidox_version': utils.get_kapidox_version(),
        }
    if template_mapping:
        mapping.update(template_mapping)
    logging.info('Postprocessing')

    tmpl = generator.create_jinja_environment(ctx.doxdatadir).get_template('doxygen2.html')
    generator.postprocess_internal(ctx.htmldir, tmpl, mapping)

def create_fw_tagfile_tuple(lib):
    tagfile = os.path.abspath(
                os.path.join(
                    lib['outputdir'],
                    'html',
                    lib['fancyname']+'.tags'))
    return (tagfile, '../../' + lib['outputdir'] + '/html/')


def parse_args():
    parser = argparse.ArgumentParser(description='Generate API documentation for the KDE Frameworks')
    group = argparserutils.add_sources_group(parser)
    group.add_argument('frameworksdir',
            help='Location of the frameworks modules.')
    group.add_argument('--depdiagram-dot-dir',
            help='Generate dependency diagrams, using the .dot files from DIR.',
            metavar="DIR")
    argparserutils.add_output_group(parser)
    argparserutils.add_qt_doc_group(parser)
    argparserutils.add_paths_group(parser)
    argparserutils.add_misc_group(parser)
    args = parser.parse_args()
    argparserutils.check_common_args(args)

    if args.depdiagram_dot_dir and not DEPDIAGRAM_AVAILABLE:
        logging.error('You need to install the Graphviz Python bindings to generate dependency diagrams.\nSee <http://www.graphviz.org/Download.php>.')
        exit(1)

    if not os.path.isdir(args.frameworksdir):
        logging.error(args.frameworksdir + " is not a directory")
        exit(2)

    return args


def main():
    utils.setup_logging()
    args = parse_args()

    tagfiles = generator.search_for_tagfiles(
            suggestion = args.qtdoc_dir,
            doclink = args.qtdoc_link,
            flattenlinks = args.qtdoc_flatten_links,
            searchpaths = ['/usr/share/doc/qt5', '/usr/share/doc/qt'])
    maintainers = generator.download_kde_identities()
    #tiers = {1:[],2:[],3:[],4:[]}
    metalist = []

    for path, dirs, _ in os.walk(args.frameworksdir):
        # We don't want to do the recursion in the dotdirs
        dirs[:] = [d for d in dirs if not d[0] == '.']
        metainfo = create_metainfo(args.frameworksdir, path)
        if metainfo is not None:
            if metainfo['public_lib']:
                metalist.append(metainfo)
            else:
                logging.warning("{} has no public libraries".format(metainfo['name']))
    products, groups, libraries, available_platforms = sort_metainfo(metalist, maintainers)
    generator.copy_dir_contents(os.path.join(args.doxdatadir,'htmlresource'),'.')
    #group_menu = generate_group_menu(metalist)

    process_toplevel_html_file('index.html', args.doxdatadir,
            title=args.title, products=products, api_searchbox=args.api_searchbox)
    process_subgroup_html_files('index.html', args.doxdatadir,
            title=args.title, groups=groups, available_platforms=available_platforms,
            api_searchbox=args.api_searchbox)
    tmp_dir = tempfile.mkdtemp(prefix='kgenframeworksapidox-')

    try:
        if args.depdiagram_dot_dir:
            dot_files = find_dot_files(args.depdiagram_dot_dir)
            assert(dot_files)

        for lib in libraries:
            logging.info('# Generating doc for {}'.format(lib['fancyname']))
            if args.depdiagram_dot_dir:
                png_path = os.path.join(tmp_dir, lib['name']) + '.png'
                ok = generate_diagram(png_path, lib['name'], dot_files, tmp_dir)
                if ok:
                    lib['dependency_diagram'] = png_path
            ctx = create_fw_context(args, lib, tagfiles)
            gen_fw_apidocs(ctx, tmp_dir)
            tagfiles.append(create_fw_tagfile_tuple(lib))
        # Rebuild for interdependencies
        # FIXME: can we be cleverer about deps?
        for lib in libraries:
            logging.info('# Rebuilding {} for interdependencies'.format(lib['name']))
            shutil.rmtree(lib['outputdir'])
            ctx = create_fw_context(args, lib, tagfiles)
            gen_fw_apidocs(ctx, tmp_dir)
            finish_fw_apidocs(ctx, None)
        logging.info('# Done')
    finally:
        if args.keep_temp_dirs:
            logging.info('Kept temp dir at {}'.format(tmp_dir))
        else:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    main()

