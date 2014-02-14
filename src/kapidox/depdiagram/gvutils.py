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

"""
A set of classes and functions to make it easier to work with Graphviz graphs
"""

from __future__ import division, absolute_import, print_function, unicode_literals

import gv


class Node(object):
    def __init__(self, node_handle):
        self.handle = node_handle

    @property
    def name(self):
        return gv.nameof(self.handle)

    @property
    def label(self):
        return gv.getv(self.handle, b"label")

    @property
    def shape(self):
        return gv.getv(self.handle, b"shape")


class Edge(object):
    def __init__(self, edge_handle):
        self.handle = edge_handle

    @property
    def head(self):
        handle = gv.headof(self.handle)
        if handle is None:
            return None
        else:
            return Node(handle)

    @property
    def tail(self):
        handle = gv.tailof(self.handle)
        if handle is None:
            return None
        else:
            return Node(handle)


def get_node_list(graph_h):
    """Generator to iterate over all nodes of a graph"""
    handle = gv.firstnode(graph_h)
    while gv.ok(handle):
        yield handle
        handle = gv.nextnode(graph_h, handle)


def get_edge_list(graph_h):
    """Generator to iterate over all edges of a graph"""
    handle = gv.firstedge(graph_h)
    while gv.ok(handle):
        yield handle
        handle = gv.nextedge(graph_h, handle)
