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

import os
import shutil
import subprocess
import sys

import yaml

__all__ = ('prepare',)

def _generate_dot(fw_dir, build_dir):
    """Calls cmake to generate the dot file for a framework.

    Returns true on success, false on failure"""
    fw_name = os.path.basename(fw_dir)
    ret = subprocess.call(["cmake", fw_dir, "--graphviz={}.dot".format(fw_name)],
        stdout=open("/dev/null", "w"),
        cwd=build_dir)
    if ret != 0:
        sys.stdout.write("ERROR: Generating the dot file for {} failed.\n".format(fw_name))
        return False
    return True


def prepare(fw_base_dir, dot_dir):
    """Generate dot files for all frameworks.

    Looks for frameworks in `fw_base_dir`. Output the dot files in sub dirs of
    `dot_dir`.
    """
    lst = os.listdir(fw_base_dir)
    for idx, fw_name in enumerate(lst):
        fw_dir = os.path.join(fw_base_dir, fw_name)
        yaml_path = os.path.join(fw_dir, fw_name + ".yaml")
        if not os.path.exists(yaml_path):
            continue

        progress = int(100 * (idx + 1) / len(lst))
        print("{}% {}".format(progress, fw_name))

        with open(yaml_path) as f:
            fw_info = yaml.load(f)
            tier = fw_info["tier"]

        build_dir = os.path.join(dot_dir, "tier" + str(tier), fw_name)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        if not _generate_dot(fw_dir, build_dir):
            continue
        shutil.copy(yaml_path, build_dir)
