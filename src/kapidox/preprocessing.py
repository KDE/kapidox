# -*- coding: utf-8 -*-
#
# Copyright 2016  Olivier Churlaud <olivier@churlaud.com>
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
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import logging
import os

try:
    from urllib2 import Request, urlopen, HTTPError
except:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

import yaml

from kapidox import utils
from kapidox.models import Library, Product

__all__ = (
    "create_metainfo",
    "parse_tree")


PLATFORM_ALL = "All"
PLATFORM_UNKNOWN = "UNKNOWN"


## @package kapidox.preprocessing
#
# Preprocessing of the needed information.
#
# The module allow to walk through folders, read metainfo files and create
# products, subgroups and libraries representing the projects.
#

def expand_platform_all(dct, available_platforms):
    """If one of the keys of dct is `PLATFORM_ALL` (or `PLATFORM_UNKNOWN`),
    remove it and add entries for all available platforms to dct

    Args:
        dct: (dictionary) dictionary to expand
        available_platforms: (list of string) name of platforms
    """

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
    """Look for a `metadata.yaml` file and create a dictionary out it.

    Args:
        path: (string) the current path to search.
    Returns:
        A dictionary containing all the parsed information, or `None` if it
    did not fullfill some conditions.
    """

    if not os.path.isdir(path):
        return None

    metainfo_file = os.path.join(path, 'metainfo.yaml')
    if not os.path.isfile(metainfo_file):
        return None

    try:
        metainfo = yaml.load(open(metainfo_file))
    except Exception as e:
        print(e)
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
    if 'fancyname' in metainfo:
        fancyname = metainfo['fancyname']
    else:
        fancyname = utils.parse_fancyname(path)

    if not fancyname:
        logging.warning('Could not find fancy name for {}, skipping it'
                        .format(path))
        return None
    # A fancyname has 1st char capitalized
    fancyname = fancyname[0].capitalize() + fancyname[1:]
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

    Args:
        rootdir: (string)  Top level directory containing the libraries.

    Returns:
        A list of metainfo dictionary (see create_metainfo()).

    """
    metalist = []
    for path, dirs, _ in os.walk(rootdir):
        # We don't want to do the recursion in the dotdirs
        dirs[:] = [d for d in dirs if not d[0] == '.']
        metainfo = create_metainfo(path)
        if metainfo is not None:
            if metainfo['public_lib'] or 'group_info' in metainfo:
                metalist.append(metainfo)
            else:
                logging.warning("{} has no public libraries"
                                .format(metainfo['name']))

    return metalist


def sort_metainfo(metalist, all_maintainers):
    """Extract the structure (Product/Subproduct/Library) from the metainfo
    list.

    Args:
        metalist: (list of dict) lists of the metainfo extracted in
    parse_tree().
        all_maintainers: (dict of dict)  all possible maintainers.

    Returns:
        A list of Products, a list of groups (which are products containing
    several libraries), a list of Libraries and the available platforms.
    """
    products = dict()
    groups = []
    libraries = []
    available_platforms = set(['Windows', 'MacOSX', 'Linux', 'Android', 'FreeBSD'])

    # First extract the structural info
    for metainfo in metalist:
        product = extract_product(metainfo, all_maintainers)
        if product is not None:
            products[product.name] = product

    # Second extract the libraries
    for metainfo in metalist:
        try:
            platforms = metainfo['platforms']
            platform_lst = [x['name'] for x in platforms
                            if x['name'] not in (PLATFORM_ALL,
                                                 PLATFORM_UNKNOWN)]

            available_platforms.update(set(platform_lst))
        except (KeyError, TypeError):
            logging.warning('{} library lacks valid platform definitions'
                            .format(metainfo['fancyname']))
            platforms = [dict(name=PLATFORM_UNKNOWN)]

        dct = dict((x['name'], x.get('note', '')) for x in platforms)

        expand_platform_all(dct, available_platforms)
        platforms = dct

        if metainfo['public_lib']:
            lib = Library(metainfo, products, platforms, all_maintainers)
            libraries.append(lib)

    groups = []
    for key in products.copy():
        if len(products[key].libraries) == 0:
            del products[key]
        elif products[key].part_of_group:
            groups.append(products[key])

    return list(products.values()), groups, libraries, available_platforms


def extract_product(metainfo, all_maintainers):
    """Extract a product from a metainfo dictionary.

    Args:
        metainfo: (dict) metainfo created by the create_metainfo() function.
        all_maintainer: (dict of dict) all possible maintainers

    Returns:
        A Product or None if the metainfo does not describe a product.
    """

    if 'group_info' not in metainfo and 'group' in metainfo:
        # This is not a product but a simple lib
        return None

    try:
        product = Product(metainfo, all_maintainers)
        return product
    except ValueError as e:
        logging.error(e)
        return None
