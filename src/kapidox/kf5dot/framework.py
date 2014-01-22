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
class Framework(object):
    """
    A framework has a tier, a name, a collection of targets it provides.
    For each target it provides, it knows which targets they depend on.

    It also has a list of frameworks it depends on, for framework-to-framework
    dependencies. This is useful for cases when a framework depends on macros
    provided by another framework.
    """
    def __init__(self, tier, name):
        self.tier = tier
        self.name = name

        # A dict of target => set([targets])
        self._target_dict = {}

        # A list of other frameworks (not targets!) this framework depends on.
        self._fw_list = []

    def add_target(self, target):
        # Add a new target provided by this framework
        assert target not in self._target_dict
        self._target_dict[target] = set()

    def add_target_dependency(self, target, dep):
        # Add a new dependency target to a target provided by this framework
        assert target in self._target_dict
        self._target_dict[target].add(dep)

    def get_targets(self):
        return self._target_dict.keys()

    def has_target(self, target):
        return target in self._target_dict

    def get_all_target_dependencies(self):
        deps = self._target_dict.values()
        if not deps:
            return set()
        return reduce(lambda x,y: x.union(y), deps)

    def get_dependencies_for_target(self, target):
        return self._target_dict[target]

    def add_extra_framework(self, name):
        # Add a framework this framework depends on because of a
        # framework-to-framework dependency
        self._fw_list.append(name)

    def get_extra_frameworks(self):
        # Returns frameworks this framework depends on because of a
        # framework-to-framework dependency
        return self._fw_list

    def __repr__(self):
        return self.name
