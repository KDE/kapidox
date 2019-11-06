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

import logging
import os.path
import string
from kapidox import utils

## @package kapidox.models
#
# Contains the classes representing the objects used by kapidox
#

class Library(object):
    """ Library
    """
    
    def __init__(self, metainfo, products, platforms, all_maintainers):
        """
            Constructor of the Library object
            
            Args:
                metainfo:     (dict) dictionary describing a library
                products:     (list of Products) list of all already created products
                platforms:    (dict) dictionary of all platforms for which the library
                              is available, where the key is a platform and the value
                              is a restriction. For instance:  
                                { 
                                    'Linux': '', 
                                    'Windows': 'Tested with Windows 10 only'
                                }
                              would work.
                all_maintainers: (dict of dict)  all possible maintainers, where the main key
                              is a username/unique pseudo, and the key is a dictionary of name,
                              email address. For example:
                                {
                                    'username01': { 'name': 'Paul Developer', 'email': 'mail@example.com' },
                                    'username02': { 'name': 'Marc Developer2', 'email': 'mail2@example.com' }
                                }
                              would work. 
                                
        """
        self.product = None        
        self.subproduct = None

        if 'group' in metainfo:
            productname = metainfo['group']
            self.part_of_group = True
        else:
            productname = metainfo['name']
            self.part_of_group = False
        if utils.serialize_name(productname) not in products:
            productname = metainfo['name']
            del metainfo['group']
            products[utils.serialize_name(metainfo['name'])] = Product(metainfo, all_maintainers)
            self.part_of_group = False
            logging.warning("Group of {} not found: dropped.".format(metainfo['fancyname']))
        self.product = products[utils.serialize_name(productname)]
        if self.product is None:
            raise ValueError("'{}' does not belong to a product."
                             .format(metainfo['name']))

        if 'subgroup' in metainfo and self.part_of_group:
            for sp in self.product.subproducts:
                if sp.name == utils.serialize_name(metainfo['subgroup']):
                    self.subproduct = sp
            if self.subproduct is None:
                logging.warning("Subgroup {} of library {} not documented, subgroup will be None"
                                .format(metainfo['subgroup'], metainfo['name']))

        if self.subproduct is not None:
            self.parent = self.subproduct
            self.subproduct.libraries.append(self)
        else:
            self.parent = self.product
        self.product.libraries.append(self)

        self.name = metainfo['name']
        self.fancyname = metainfo['fancyname']
        self.description = metainfo.get('description')
        self.maintainers = utils.set_maintainers(metainfo.get('maintainer'), all_maintainers)
        self.platforms = platforms
        self.outputdir = self._set_outputdir(self.part_of_group)
        self.href = '../' + self.outputdir.lower() + '/html/index.html'
        self.path = metainfo['path']
        self.srcdirs = utils.tolist(metainfo.get('public_source_dirs', ['src']))
        self.docdir = utils.tolist(metainfo.get('public_doc_dir', ['docs']))
        self.exampledir = utils.tolist(metainfo.get('public_example_dir', ['examples']))
        self.dependency_diagram = None
        self.type = metainfo.get('type', '')
        self.portingAid = metainfo.get('portingAid', False)
        self.deprecated = metainfo.get('deprecated', False)
        self.libraries = metainfo.get('libraries', [])
        self.cmakename = metainfo.get('cmakename', '')
        self.irc = metainfo.get('irc', self.product.irc)
        self.mailinglist = metainfo.get('mailinglist', self.product.mailinglist)

    def _extend_parent(self, metainfo, key, key_obj, default):
        if key in metainfo:
            return metainfo[key]
        elif getattr(self.product, key_obj) is not None:
            return getattr(self.product, key_obj)
        else:
            return default

    def _set_outputdir(self, grouped):
        outputdir = self.name
        if grouped:
            outputdir = self.product.outputdir + '/' + outputdir
        return outputdir.lower()


class Product(object):
    """ Product
    """

    # TODO: If no name and no group, it will fail !
    def __init__(self, metainfo, all_maintainers):
        """
            Constructor of the Product object
            
            Args:
                metainfo:     (dict) dictionary describing a product
                all_maintainers: (dict of dict)  all possible maintainers, where the main key
                              is a username/unique pseudo, and the key is a dictionary of name,
                              email address. For example:
                                {
                                    'username01': { 'name': 'Paul Developer', 'email': 'mail@example.com' },
                                    'username02': { 'name': 'Marc Developer2', 'email': 'mail2@example.com' }
                                }
                              would work. 
                                
        """
        
        self.parent = None
        # if there is a group, the product is the group
        # else the product is directly the library
            
        if 'group_info' in metainfo:
            self.name = utils.serialize_name(metainfo['group_info'].get('name', metainfo.get('group')))
            self.fancyname = metainfo['group_info'].get('fancyname', string.capwords(self.name))
            self.description = metainfo['group_info'].get('description')
            self.long_description = metainfo['group_info'].get('long_description', [])
            self.maintainers = utils.set_maintainers(metainfo['group_info'].get('maintainer'),
                                                     all_maintainers)
            self.platforms = metainfo['group_info'].get('platforms')
            self.outputdir = self.name
            self.href = self.outputdir + '/index.html'
            self.logo_url_src = self._set_logo_src(metainfo['path'],
                                                   metainfo['group_info'])
            self.logo_url = self._set_logo()
            self.libraries = []  # We'll set this later
            self.subgroups = []  # We'll set this later
            self.irc = metainfo['group_info'].get('irc', 'kde-devel')
            self.mailinglist = metainfo['group_info'].get('mailinglist', 'kde-devel')
            self.subproducts = self._extract_subproducts(metainfo['group_info'])
            self.part_of_group = True

        elif 'group' not in metainfo:
            self.name = utils.serialize_name(metainfo['name'])
            self.fancyname = metainfo['fancyname']
            self.description = metainfo.get('description')
            self.maintainers = utils.set_maintainers(metainfo.get('maintainer'), all_maintainers)
            self.platforms = [x['name'] for x in metainfo.get('platforms', [{'name': None}])]
            self.outputdir = self.name
            self.href = self.outputdir + '/html/index.html'
            self.logo_url_src = self._set_logo_src(metainfo['path'], metainfo)
            self.logo_url = self._set_logo()
            self.libraries = []
            self.irc = None
            self.mailinglist = None
            self.part_of_group = False
        else:
            raise ValueError("I do not recognize a product in {}."
                             .format(metainfo['name']))

    def _extract_subproducts(self, groupinfo):
        subproducts = []
        if 'subgroups' in groupinfo:
            for sg in groupinfo['subgroups']:
                sg
                if 'name' in sg:
                    subproducts.append(Subproduct(sg, self))
        return subproducts

    def _set_logo(self):
        if self.logo_url_src is not None:
            filename, ext = os.path.splitext(self.logo_url_src)
            return self.outputdir + '/' + self.name + ext
        else:
            return None

    def _set_logo_src(self, path, dct):
        if 'logo' in dct:
            logo_url = os.path.join(path, dct['logo'])
            if os.path.isfile(logo_url):
                return logo_url
            else:
                logging.warning("{} logo file doesn't exist, set back to None"
                                .format(self.fancyname))
                return None
        else:
            return None

class Subproduct(object):
    """ Subproduct
    """
    def __init__(self, spinfo, product):
        """
            Constructor of the Subproduct object
            
            Args:
                spinfo:       (dict) description of the subproduct. It is not more than:
                {
                    'name': 'Subproduct Name',
                    'description': 'This subproduct does this and that',
                    'order': 3, # this is optional
                }
                for example.
                product:      (Product) the product it is part of.
        """
        self.fancyname = spinfo['name']
        self.name = utils.serialize_name(spinfo['name'])
        self.description = spinfo.get('description')
        self.order = spinfo.get('order', 99)  # If no order, go to end
        self.libraries = []
        self.product = product
        self.parent = product
