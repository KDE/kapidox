# -*- coding: utf-8 -*-
#
# Copyright 2014  Aurélien Gâteau <agateau@kde.org>
# Copyright 2014  Alex Merry <alex.merry@kdemail.net>
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

def _quote(txt):
    return '"' + txt + '"'

class DoxyfileWriter(object):
    """Makes it easy to write entries in a Doxyfile, correctly handling quoting
    """
    def __init__(self, fl):
        self.fl = fl

    def write_entry(self, key, value):
        """Write an entry

        Args:
            key: the key part of the entry
            value: the value part of the entry. Can be a string, a list, a
        tuple or a boolean
        """
        if isinstance(value, (list, tuple)):
            txt = ' '.join([_quote(x) for x in value])
        elif isinstance(value, bool):
            txt = ['NO', 'YES'][value]
        else:
            txt = _quote(str(value))
        self.fl.write(key + ' = ' + txt + '\n')

    def write_entries(self, **kwargs):
        """ Call write_entry for all arguments passed"""
        for key, value in kwargs.items():
            self.write_entry(key, value)
