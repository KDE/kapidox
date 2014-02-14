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
import tempfile

__all__ = ('prepare', 'prepare_one', 'NoFrameworkError', 'GenerationError')


class NoFrameworkError(Exception):
    pass


class GenerationError(Exception):
    pass


def _generate_dot(fw_dir, output_dir):
    """Calls cmake to generate the dot file for a framework.

    Returns true on success, false on failure"""
    fw_name = os.path.basename(fw_dir)
    dot_path = os.path.join(output_dir, fw_name + ".dot")
    build_dir = tempfile.mkdtemp(prefix="depdiagram-prepare-build-")
    try:
        ret = subprocess.call(["cmake", fw_dir, "--graphviz={}".format(dot_path)],
            stdout=open("/dev/null", "w"),
            cwd=build_dir)
        if ret != 0:
            raise GenerationError("Generating dot file for {} failed.".format(fw_name))
    finally:
        shutil.rmtree(build_dir)


def prepare_one(fw_dir, output_dir):
    fw_name = os.path.basename(fw_dir)
    yaml_path = os.path.join(fw_dir, fw_name + ".yaml")
    if not os.path.exists(yaml_path):
        raise NoFrameworkError("'{}' is not a framework: '{}' does not exist.".format(fw_dir, yaml_path))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    _generate_dot(fw_dir, output_dir)
    shutil.copy(yaml_path, output_dir)


def prepare(fw_base_dir, dot_dir):
    """Generate dot files for all frameworks.

    Looks for frameworks in `fw_base_dir`. Output the dot files in sub dirs of
    `dot_dir`.
    """
    lst = os.listdir(fw_base_dir)
    for idx, fw_name in enumerate(lst):
        fw_dir = os.path.join(fw_base_dir, fw_name)
        if not os.path.isdir(fw_dir):
            continue

        progress = int(100 * (idx + 1) / len(lst))
        print("{}% {}".format(progress, fw_name))

        try:
            prepare_one(fw_dir, dot_dir)
        except NoFrameworkError as e:
            print(e)
        except GenerationError as e:
            print(e)
