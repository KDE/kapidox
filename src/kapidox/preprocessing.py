# -*- coding: utf-8 -*-
#
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
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import logging
import os
import string
import sys
if sys.version_info.major < 3:
    from urllib2 import Request, urlopen, HTTPError
else:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

import yaml

import kapidox as kdx

__all__ = (
    "create_metainfo",
    "parse_tree",
    "set_maintainers")


PLATFORM_ALL = "All"
PLATFORM_UNKNOWN = "UNKNOWN"


def expand_platform_all(dct, available_platforms):
    """If one of the keys of dct is PLATFORM_ALL (or PLATFORM_UNKNOWN),
    remove it and add entries for all available platforms to dct"""

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
            if platform not in dct:
                dct[platform] = note


def create_metainfo(path):
    if not os.path.isdir(path):
        return None

    metainfo_file = os.path.join(path, 'metainfo.yaml')
    if not os.path.isfile(metainfo_file):
        return None

    try:
        metainfo = yaml.load(open(metainfo_file))
    except:
        logging.warning('Could not load metainfo.yaml for {}, skipping it'
                        .format(path))
        return None

    if metainfo is None:
        logging.warning('Empty metainfo.yaml for {}, skipping it'
                        .format(path))
        return None

    if 'subgroup' in metainfo and 'group' not in metainfo:
        logging.warning('Subgroup but no group in {}, skipping it'
                        .format(path))
        return None

    name = os.path.basename(path)
    fancyname = kdx.utils.parse_fancyname(path)
    if not fancyname:
        logging.warning('Could not find fancy name for {}, skipping it'
                        .format(path))
        return None

    metainfo.update({
        'fancyname': fancyname,
        'name': name,
        'public_lib': metainfo.get('public_lib', False),
        'dependency_diagram': None,
        'path': path,
        })

    return metainfo


def parse_tree(rootdir):
    """Recursively call create_metainfo() in subdirs of rootdir

    Parameters
    ----------
    rootdir : string
        Top level directory containing the libraries

    Return
    ------
    metalist : list of dictionaries
        list of metainfo dictionary (see :any:`create_metainfo`)

    """
    metalist = []
    for path, dirs, _ in os.walk(rootdir):
        # We don't want to do the recursion in the dotdirs
        dirs[:] = [d for d in dirs if not d[0] == '.']
        metainfo = create_metainfo(path)
        if metainfo is not None:

            if metainfo['public_lib']:
                metalist.append(metainfo)
            else:
                logging.warning("{} has no public libraries"
                                .format(metainfo['name']))

    return metalist


def sort_metainfo(metalist, all_maintainers):
    products = []
    groups = []
    libraries = []
    available_platforms = set(['Windows', 'MacOSX', 'Linux'])

    all_groups = []
    defined_groups = []
    for metainfo in metalist:
        if 'group' in metainfo:
            all_groups.append(metainfo['group'])
        if 'group_info' in metainfo:
            defined_groups.append(metainfo['group'])
    undefined_groups = [x for x in list(set(all_groups)) if x not in defined_groups]

    for metainfo in metalist:

        try:
            platforms = metainfo['platforms']
            platform_lst = [x['name'] for x in platforms
                            if x['name'] not in (PLATFORM_ALL,
                                                 PLATFORM_UNKNOWN)]

            available_platforms.update(set(platform_lst))
        except (KeyError, TypeError):
            logging.warning('{} framework lacks valid platform definitions'
                            .format(metainfo['fancyname']))
            platforms = [dict(name=PLATFORM_UNKNOWN)]

        dct = dict((x['name'], x.get('note', '')) for x in platforms)

        expand_platform_all(dct, available_platforms)
        platforms = dct

        lib = extract_lib(metainfo, platforms, all_maintainers)
        libraries.append(lib)

        product = extract_product(metainfo, platforms, all_maintainers, undefined_groups)
        if product is not None:
            products.append(product)

    # We have all groups and libraries, let set the parents.
    # and check the platforms
    for lib in libraries:
        if lib['parent'].get('group') is not None:
            product_list = [x for x in products if x['name'].lower() == lib['parent']['group'].lower()]
            if not product_list:
                continue  # The group_info was not defined
            else:
                product = product_list[0]
            lib['product'] = product
            if lib['mailinglist'] is None:
                if product['mailinglist'] is not None:
                    lib['mailinglist'] = product['mailinglist']
                else:
                    lib['mailinglist'] = 'kde-devel'
            if lib['irc'] is None:
                if product['irc'] is not None:
                    lib['irc'] = product['irc']
                else:
                    lib['irc'] = 'kde-devel'

            product['libraries'].append(lib)
            if lib['parent'].get('subgroup') is None:
                lib['subgroup'] = None
            else:
                subgroup_list = [x for x in lib['product']['subgroups'] if x['name'].lower() == lib['parent']['subgroup'].lower()]
                if not subgroup_list:
                    logging.warning("Subgroup {} of library {} not documentated, setting subgroup to None"
                                    .format(lib['parent']['subgroup'], lib['name']))
                    lib['subgroup'] = None
                    lib['parent'] = product
                else:
                    subgroup = subgroup_list[0]
                    lib['subgroup'] = subgroup
                    subgroup['libraries'].append(lib)
            groups.append(product)
        else:
            lib['parent'] = None

    return products, groups, libraries, available_platforms


def extract_lib(metainfo, platforms, all_maintainers):
    outputdir = metainfo.get('name')
    if 'group' in metainfo:
        outputdir = metainfo.get('group') + '/' + outputdir
    outputdir = kdx.utils.serialize_name(outputdir)

    lib = {
        'name': metainfo['name'],
        'fancyname': metainfo['fancyname'],
        'description': metainfo.get('description'),
        'maintainers': set_maintainers(metainfo, 'maintainer', all_maintainers),
        'platforms': platforms,
        'parent': {'group': kdx.utils.serialize_name(metainfo.get('group')),
                   'subgroup': kdx.utils.serialize_name(metainfo.get('subgroup'))},
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
        'cmakename': metainfo.get('cmakename', ''),
        'irc': metainfo.get('irc'),
        'mailinglist': metainfo.get('mailinglist'),
        }

    return lib


def extract_product(metainfo, platforms, all_maintainers, undefined_groups):
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

    def set_logo(product):
        if product['logo_url_src'] is not None:
            filename = os.path.basename(product['logo_url_src'])
            product['logo_url'] = outputdir + '/'+ product['name'] + '.' + filename.split('.')[-1]

    # if there is a group, the product is the group
    # else the product is directly the library
    if 'group_info' in metainfo:
        outputdir = kdx.utils.serialize_name(metainfo['group'])
        product = {
            'name': kdx.utils.serialize_name(metainfo['group']),
            'fancyname': metainfo['group_info'].get('fancyname', string.capwords(metainfo['group'])),
            'description': metainfo['group_info'].get('description'),
            'long_description': metainfo['group_info'].get('long_description', []),
            'maintainers': set_maintainers(metainfo['group_info'],
                                           'maintainer',
                                           all_maintainers),
            'platforms': metainfo['group_info'].get('platforms'),
            'logo_url_src': get_logo_url(metainfo['group_info'],
                                         metainfo['group']),
            'logo_url': None,  # We'll set this later
            'outputdir': outputdir,
            'href': outputdir + '/index.html',
            'libraries': [],  # We'll set this later
            'subgroups': [],  # We'll set this later
            'irc': metainfo['group_info'].get('irc'),
            'mailinglist': metainfo['group_info'].get('mailinglist'),
            }

        if 'subgroups' in metainfo['group_info']:
            for sg in metainfo['group_info']['subgroups']:
                if 'name' in sg:
                    product['subgroups'].append({
                            'fancyname': sg['name'],
                            'name': kdx.utils.serialize_name(sg['name']),
                            'description': sg.get('description'),
                            'order': sg.get('order', 99),  # If no order, go to end
                            'libraries': []
                            })
        set_logo(product)
        return product
    elif 'group' in metainfo and metainfo['group'] in undefined_groups:
        outputdir = kdx.utils.serialize_name(metainfo['group'])
        product = {
            'name': kdx.utils.serialize_name(metainfo['group']),
            'fancyname': string.capwords(metainfo['group']),
            'description': '',
            'long_description': [],
            'maintainers': set_maintainers(dict(),
                                           'maintainer',
                                           all_maintainers),
            'platforms': None,
            'logo_url_src': None,
            'logo_url': None,  # We'll set this later
            'outputdir': outputdir,
            'href': outputdir + '/index.html',
            'libraries': [],  # We'll set this later
            'subgroups': [],  # We'll set this later
            'irc': None,
            'mailinglist': None,
            }
        return product
    elif 'group' not in metainfo:
        outputdir = metainfo['name']

        product = {
            'name': kdx.utils.serialize_name(metainfo['name']),
            'fancyname': metainfo['fancyname'],
            'description': metainfo.get('description'),
            'maintainers': set_maintainers(metainfo,
                                          'maintainer',
                                          all_maintainers),
            'platforms': platforms,
            'logo_url_src': get_logo_url(metainfo, metainfo['fancyname']),
            'logo_url': None,  # We'll set that later
            'href': outputdir + '/html/index.html',
            'outputdir': outputdir
            }
        set_logo(product)
        return product
    else:
        return None

def set_maintainers(dictionary, key, maintainers):
    """ Expend the name of the maintainers.

    Use
    ---
    metainfo = { 'key1': 'something', 'maintainers': ['arthur', 'toto']}
    myteam = [{'arthur': {'name': 'Arthur Pendragon',
                          'email': 'arthur@example.com'},
               'toto': {'name': 'Toto',
                        'email: 'toto123@example.com'}
                }]
    set_maintainers(metainfo, "maintainers", my_team)

    Parameters
    ----------
    dictonary : dict
        Dictionary from which the name to expend must be read.
    key : string
        Key of the dictionary where the name to expend is saved.
    maintainers : list of dict
        Look-up table where the names and emails of the maintainers are stored.
    """

    if key not in dictionary:
        fw_maintainers = []
    elif isinstance(dictionary[key], list):
        fw_maintainers = map(lambda x: maintainers.get(x, None),
                             dictionary[key])
    else:
        fw_maintainers = [maintainers.get(dictionary[key], None)]

    fw_maintainers = [x for x in fw_maintainers if x is not None]
    return fw_maintainers