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


from fnmatch import fnmatch
import logging
import os
import re
import subprocess
import shutil
import sys
import tempfile

## @package kapidox.utils
#
# Multiple usage utils.
#
# This module contains code which is shared between depdiagram-prepare and
# other components.
#
# Code in this dir should not import any module which is not shipped with
# Python because this module is used by depdiagram-prepare, which must be able
# to run on builds.kde.org, which may not have all the required dependencies.
#

def setup_logging():
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT, datefmt='%H:%M:%S', level=logging.DEBUG)


def tolist(a):
    """ Return a list based on `a`. """
    return a if type(a) is list else [a]


def serialize_name(name):
    """ Return a serialized name.

    For now it only replaces ' ' with '_' and lower the letters.
    """
    if name is not None:
        return '_'.join(name.lower().split(' '))
    else:
        return None


def set_maintainers(maintainer_keys, all_maintainers):
    """ Expend the name of the maintainers.

    Args:
        dictionary: (dict) Dictionary from which the name to expend will be read.
        key: (string) Key of the dictionary where the name to expend is saved.
        all_maintainers: (dict of dict) Look-up table where the names and emails of
    the maintainers are stored.

    Examples:
        >>> maintainer_keys = ['arthur', 'toto']

        >>> myteam = {'arthur': {'name': 'Arthur Pendragon',
                                 'email': 'arthur@example.com'},
                      'toto': {'name': 'Toto',
                               'email: 'toto123@example.com'}
                      }

        >>> set_maintainers(maintainer_keys, my_team)
    """

    if not maintainer_keys:
        maintainers = []
    elif isinstance(maintainer_keys, list):
        maintainers = map(lambda x: all_maintainers.get(x, None),
                             maintainer_keys)
    else:
        maintainers = [all_maintainers.get(maintainer_keys, None)]

    maintainers = [x for x in maintainers if x is not None]
    return maintainers


def parse_fancyname(fw_dir):
    """Return the framework name for a given source dir

    The framework name is the name of the toplevel CMake project
    """
    cmakelists_path = os.path.join(fw_dir, "CMakeLists.txt")
    if not os.path.exists(cmakelists_path):
        logging.error("No CMakeLists.txt in {}".format(fw_dir))
        return None
    project_re = re.compile(r"project\s*\(\s*([\w\-\_]+)", re.I)
    with open(cmakelists_path) as f:
        for line in f.readlines():
            match = project_re.search(line)
            if match:
                return match.group(1)
    logging.error("Failed to find framework name: Could not find a "
                  "'project()' command in {}.".format(cmakelists_path))
    return None


def cache_dir():
    """Find/create a semi-long-term cache directory.

    We do not use tempdir, except as a fallback, because temporary directories
    are intended for files that only last for the program's execution.
    """
    cachedir = None
    if sys.platform == 'darwin':
        try:
            from AppKit import NSSearchPathForDirectoriesInDomains
            # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
            # NSApplicationSupportDirectory = 14
            # NSUserDomainMask = 1
            # True for expanding the tilde into a fully qualified path
            cachedir = os.path.join(
                    NSSearchPathForDirectoriesInDomains(14, 1, True)[0],
                    'KApiDox')
        except:
            pass
    elif os.name == "posix":
        if 'HOME' in os.environ and os.path.exists(os.environ['HOME']):
            cachedir = os.path.join(os.environ['HOME'], '.cache', 'kapidox')
    elif os.name == "nt":
        if 'APPDATA' in os.environ and os.path.exists(os.environ['APPDATA']):
            cachedir = os.path.join(os.environ['APPDATA'], 'KApiDox')
    if cachedir is None:
        cachedir = os.path.join(tempfile.gettempdir(), 'kapidox')
    if not os.path.isdir(cachedir):
        os.makedirs(cachedir)
    return cachedir


def svn_export(remote, local, overwrite=False):
    """Wraps svn export.

    Args:
        remote:     (string) the remote url.
        local:      (string) the local path where to dowload.
        overwrite:  (bool) whether to overwrite `local` or not. (optional,
    default = False)

    Returns:
        True if success.

    Raises:
        FileNotFoundError: &nbsp;
        subprocess.CalledProcessError: &nbsp;
    """
    try:
        import svn.core
        import svn.client
        logging.debug("Using Python libsvn bindings to fetch %s", remote)
        ctx = svn.client.create_context()
        ctx.auth_baton = svn.core.svn_auth_open([])

        latest = svn.core.svn_opt_revision_t()
        latest.type = svn.core.svn_opt_revision_head

        svn.client.export(remote, local, latest, True, ctx)
    except ImportError:
        logging.debug("Using external svn client to fetch %s", remote)
        cmd = ['svn', 'export', '--quiet']
        if overwrite:
            cmd.append('--force')
        cmd += [remote, local]
        try:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise subprocess.StandardException(e.output)
        except FileNotFoundError as e:
            logging.debug("External svn client not found")
            return False
    # subversion will set the timestamp to match the server
    os.utime(local, None)
    return True


def copy_dir_contents(directory, dest):
    """Copy the contents of a directory

    Args:
        directory: (string) the directory to copy the contents of.
        dest: (string) the directory to copy them into.
    """
    ignored = ['CMakeLists.txt']
    ignore = shutil.ignore_patterns(*ignored)
    for fn in os.listdir(directory):
        f = os.path.join(directory, fn)
        if os.path.isfile(f):
            docopy = True
            for i in ignored:
                if fnmatch(fn, i):
                    docopy = False
                    break
            if docopy:
                shutil.copy(f, dest)
        elif os.path.isdir(f):
            dest_f = os.path.join(dest, fn)
            if os.path.isdir(dest_f):
                shutil.rmtree(dest_f)
            shutil.copytree(f, dest_f, ignore=ignore)


_KAPIDOX_VERSION = None
def get_kapidox_version():
    """Get commit id of running code if it is running from git repository.

    May return an empty string if it failed to extract the commit id.

    Assumes .git/HEAD looks like this:

        ref: refs/heads/master

    and assumes .git/refs/heads/master contains the commit id
    """
    global _KAPIDOX_VERSION

    if _KAPIDOX_VERSION is not None:
        return _KAPIDOX_VERSION

    _KAPIDOX_VERSION = ""
    bin_dir = os.path.dirname(sys.argv[0])
    git_dir = os.path.join(bin_dir, "..", ".git")
    if not os.path.isdir(git_dir):
        # Looks like we are not running from the git repo, exit silently
        return _KAPIDOX_VERSION

    git_HEAD = os.path.join(git_dir, "HEAD")
    if not os.path.isfile(git_HEAD):
        logging.warning("Getting git info failed: {} is not a file".format(git_HEAD))
        return _KAPIDOX_VERSION

    try:
        line = open(git_HEAD).readline()
        ref_name = line.split(": ")[1].strip()
        with open(os.path.join(git_dir, ref_name)) as f:
            _KAPIDOX_VERSION = f.read().strip()
    except Exception as exc:
        # Catch all exceptions here: whatever fails in this function should not
        # cause the code to fail
        logging.warning("Getting git info failed: {}".format(exc))
    return _KAPIDOX_VERSION


def find_dot_files(dot_dir):
    """Returns a list of path to files ending with .dot in subdirs of `dot_dir`."""
    lst = []
    for (root, dirs, files) in os.walk(dot_dir):
        lst.extend([os.path.join(root, x) for x in files if x.endswith('.dot')])
    return lst
