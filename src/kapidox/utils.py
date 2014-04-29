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

import logging
import os
import re

"""
This module contains code which is shared between depdiagram-prepare and other
components.

Code in this dir should not import any module which is not shipped with Python
because this module is used by depdiagram-prepare, which must be able to run
on builds.kde.org, which may not have all the required dependencies.
"""

def setup_logging():
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT, datefmt='%H:%M:%S', level=logging.DEBUG)


def parse_fancyname(fw_dir):
    """Returns the framework name for a given source dir

    The framework name is the name of the toplevel CMake project
    """
    cmakelists_path = os.path.join(fw_dir, "CMakeLists.txt")
    if not os.path.exists(cmakelists_path):
        logging.error("No CMakeLists.txt in {}".format(fw_dir))
        return None
    project_re = re.compile(r"project\s*\(\s*(\w+)", re.I)
    with open(cmakelists_path) as f:
        for line in f.readlines():
            match = project_re.search(line)
            if match:
                return match.group(1)
    logging.error("Failed to find framework name: Could not find a 'project()' command in {}.".format(cmakelists_path))
    return None
