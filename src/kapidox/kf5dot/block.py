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
from contextlib import contextmanager

class Block(object):
    INDENT_SIZE = 4

    def __init__(self, out, depth = 0):
        self.out = out
        self.depth = depth

    def writeln(self, text):
        self.out.write(self.depth * Block.INDENT_SIZE * " " + text + "\n")

    def write_attrs(self, **attrs):
        for key, value in attrs.items():
            self.writeln('"{}" = "{}";'.format(key, value))

    def write_list_attrs(self, name, **attrs):
        with self.square_block(name) as b:
            for key, value in attrs.items():
                b.writeln('"{}" = "{}"'.format(key, value))

    def write_nodes(self, nodes):
        for node in sorted(nodes):
            self.writeln('"{}";'.format(node))

    @contextmanager
    def block(self, opener, closer, **attrs):
        self.writeln(opener)
        block = Block(self.out, depth=self.depth + 1)
        block.write_attrs(**attrs)
        yield block
        self.writeln(closer)

    def square_block(self, prefix, **attrs):
        return self.block(prefix + " [", "]", **attrs)

    def curly_block(self, prefix, **attrs):
        return self.block(prefix + " {", "}", **attrs)

    def cluster_block(self, title, **attrs):
        return self.curly_block("subgraph " + quote("cluster_" + title), label=title, **attrs)


def quote(txt):
    return '"{}"'.format(txt)
