#! /usr/bin/env python

# Python 2/3 compatibility (NB: we require at least 2.7)
from __future__ import division, absolute_import, print_function, unicode_literals
#from future_builtins import ascii, filter, hex, map, oct, zip

import argparse
import codecs
import datetime
from fnmatch import fnmatch
import os
import re
import shutil
import subprocess
import sys
from urlparse import urljoin

def check_datadir_files(directory, files):
    for f in files:
        if not os.path.exists(os.path.join(directory,f)):
            return False
    return True

def find_datadir(searchpaths, testfiles, suggestion=None, complain=True):
    """Find data files

    searchpaths -- directories to test
    testfiles   -- files to check for in the directory
    suggestion  -- the first place to look
    complain    -- print a warning if suggestion is not correct
    """
    if not suggestion is None:
        real_suggestion = os.path.realpath(suggestion)
        if not os.path.isdir(real_suggestion):
            print(suggestion + " is not a directory")
        elif not check_datadir_files(real_suggestion, testfiles):
            print(suggestion + " does not contain the expected files")
        else:
            return real_suggestion


    for d in searchpaths:
        d = os.path.realpath(d)
        if os.path.isdir(d) and check_datadir_files(d, testfiles):
            return d

    return None

def find_doxdatadir(suggestion=None):
    """Find common apidox data"""
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    return find_datadir(
            searchpaths=[os.path.join(scriptdir,'../common')],
            testfiles=['doxygen.css'],
            suggestion=suggestion)

def find_qt_tagfiles(docdir=None, doclink=None, linkstyle='auto'):
    """Find Qt documentation tag files
    
    Generates a list of pairs of (tag_file,link_path)"""

    searchpaths = ['/usr/share/doc/qt5',
                   '/usr/share/doc/qt']

    flatdir = find_datadir(
            searchpaths=searchpaths,
            testfiles=['qtcore.tags','qtgui.tags'],
            suggestion=docdir,
            complain=False)

    tagfiles = []

    isurl = False
    if not doclink is None:
        if "://" in doclink:
            isurl = True

    if not flatdir is None:
        print("Found Qt documentation (flat) at " + flatdir)
        if doclink is None:
            doclink = flatdir
        for f in os.listdir(flatdir):
            if f.endswith('.tags'):
                tagfile = os.path.join(flatdir,f)
                if linkstyle != 'split':
                    module = f[0:-5]
                    if isurl:
                        tagfiles.append((tagfile,urljoin(doclink,module)))
                    else:
                        tagfiles.append((tagfile,os.path.join(doclink,module)))
                else:
                    tagfiles.append((tagfile,doclink))

    else:
        splitdir = find_datadir(
                searchpaths=searchpaths,
                testfiles=['qtcore/qtcore.tags','qtgui/qtgui.tags'],
                suggestion=docdir,
                complain=True)
        if splitdir is None:
            print("Could not find Qt documentation")
            return tagfiles

        print("Found Qt documentation (split) at " + splitdir)
        if doclink is None:
            doclink = splitdir
        for d in os.listdir(splitdir):
            d = os.path.join(splitdir,d)
            if os.path.isdir(d):
                module = os.path.basename(d)
                tagfile = os.path.join(d, module + '.tags')
                if os.path.isfile(tagfile):
                    if linkstyle == 'flat':
                        tagfiles.append((tagfile,doclink))
                    elif isurl:
                        tagfiles.append((tagfile,urljoin(doclink,module)))
                    else:
                        tagfiles.append((tagfile,os.path.join(doclink,module)))

    return tagfiles


def copy_dir_contents(directory):
    ignored = ['CMakeLists.txt','*.template']
    ignore = shutil.ignore_patterns(*ignored)
    print("Copying contents of " + directory)
    for fn in os.listdir(directory):
        f = os.path.join(directory,fn)
        if os.path.isfile(f):
            docopy = True
            for i in ignored:
                if fnmatch(fn,i):
                    docopy = False
                    break
            if docopy:
                shutil.copy(f,'.')
        elif os.path.isdir(f):
            shutil.copytree(f,fn,ignore=ignore)


def generate_menu():
    entries = [
            ('Main Page','index.html'),
            ('Namespace List','namespaces.html'),
            ('Namespace Members','namespacemembers.html'),
            ('Alphabetical List','classes.html'),
            ('Class List','annotated.html'),
            ('Class Hierarchy','hierarchy.html'),
            ('Class Members','functions.html'),
            ('File List','files.html'),
            ('File Members','globals.html'),
            ('Modules','modules.html'),
            ('Directories','dirs.html'),
            ('Related Pages','pages.html')
            ]
    menu = '<ul>'
    for (name,f) in entries:
        if os.path.isfile(f):
            menu += '<li><a href="' + f + '">' + name + '</a></li>'
    menu += '</ul>'
    return menu


def postprocess(substitutions):
    # avoid dealing with encodings (in case source files have weird
    # characters in) -- this should also be faster
    for idx,(a,b) in enumerate(substitutions):
        substitutions[idx] = (a.encode('utf-8'),b.encode('utf-8'))

    for f in os.listdir('.'):
        if f.endswith('.html'):
            print("Postprocessing " + f)
            newf = f + '.new'
            with open(f, 'r') as inf:
                with open(newf, 'w') as outf:
                    for line in inf:
                        for (a,b) in substitutions:
                            line = line.replace(a,b)
                        outf.write(line)
            os.remove(f)
            os.rename(newf,f)


def main():
    parser = argparse.ArgumentParser(description='Generate API documentation in the KDE style')
    parser.add_argument('moduledir', help='Location of the module to build API documentation for; it should contain a README.md file and a src/ subdirectory')
    parser.add_argument('--doxdatadir', help='Location of the HTML header files and support graphics.')
    parser.add_argument('--installdir', help='Location of other apidox modules (should contain subdirectories called *-apidocs/, which area searched for tag files)')
    parser.add_argument('--qtdoc-dir', help='Location of (local) Qt documentation')
    parser.add_argument('--qtdoc-link',
            help='Override Qt documentation location for the links in the html files')
    parser.add_argument('--qtdoc-link-style', choices=['auto','flat','split'],
            default='auto',
            help='Whether Qt modules (eg: qtcore) are in their own subdirectory; auto means the style found in qtdoc-dir will be used')
    parser.add_argument('--doxygen', default='doxygen',
            help='(Path to) the doxygen executable')
    parser.add_argument('--qhelpgenerator', default='qhelpgenerator',
            help='(Path to) the qhelpgenerator executable')
    args = parser.parse_args()

    if not os.path.isdir(args.moduledir):
        print(args.moduledir + " is not a directory")
        exit(1)

    srcdir = os.path.abspath(os.path.realpath(args.moduledir))

    # Basic project info
    modulename = os.path.basename(args.moduledir)
    outputdir = modulename + '-apidocs'
    readme_file = os.path.join(srcdir, 'README.md')
    if os.path.isfile(readme_file):
        with codecs.open(readme_file, 'r', 'utf-8') as f:
            topline = f.readline(100)
        fancyname = re.sub(r'\s*{#.*}\s*$', '', topline.lstrip(' #')).rstrip()
        del topline
    else:
        print("The module does not provide a README.md file")
        fancyname = modulename

    doxdatadir = find_doxdatadir(suggestion=args.doxdatadir)
    if doxdatadir is None:
        print("Could not find a valid doxdatadir")
        sys.exit(3)
    else:
        print("Found doxdatadir at " + doxdatadir)

    qttagfiles = find_qt_tagfiles(
            docdir = args.qtdoc_dir,
            doclink = args.qtdoc_dir,
            linkstyle = args.qtdoc_link_style)

    generate_manpages = False
    generate_qhp = False
    searchengine = False

    # FIXME: preprocessing?

    os.makedirs(outputdir)
    os.chdir(outputdir)

    copy_dir_contents(os.path.join(doxdatadir,'resource'))
    module_api_dir = os.path.join(srcdir,'docs/api')
    if os.path.isdir(os.path.join(module_api_dir,'resource')):
        copy_dir_contents(os.path.join(module_api_dir,'resource'))

    shutil.copy(os.path.join(doxdatadir,'Doxyfile.global'), 'Doxyfile')

    with codecs.open('Doxyfile','a','utf-8') as doxyfile:
        doxyfile.write('PROJECT_NAME = "' + fancyname + '"\n')
        # FIXME: can we get the project version from CMake?
        doxyfile.write('INPUT = "' + srcdir + '"\n')
        doxyfile.write('DOTFILE_DIRS = "' + srcdir + '"\n')
        doxyfile.write('OUTPUT_DIRECTORY = .\n')
        if os.path.isfile(readme_file):
            doxyfile.write('USE_MDFILE_AS_MAINPAGE = README.md\n')

        doxyfile.write('GENERATE_TAGFILE = ' + modulename + '.tags\n')

        doxyfile.write('IMAGE_PATH =')
        if os.path.isdir(module_api_dir):
            doxyfile.write(' ' + module_api_dir)
        if os.path.isdir(os.path.join(srcdir,'docs/pics')):
            doxyfile.write(' ' + os.path.join(srcdir,'docs/pics'))
        doxyfile.write('\n')

        doxyfile.write('EXAMPLES =')
        if os.path.isdir(os.path.join(module_api_dir,'examples')):
            doxyfile.write(' ' + os.path.join(module_api_dir,'examples'))
        if os.path.isdir(os.path.join(srcdir,'docs/examples')):
            doxyfile.write(' ' + os.path.join(srcdir,'docs/examples'))
        doxyfile.write('\n')

        doxyfile.write('HTML_HEADER = "' + doxdatadir + '/header.html"\n')
        doxyfile.write('HTML_FOOTER = "' + doxdatadir + '/footer.html"\n')
        doxyfile.write('HTML_STYLESHEET = "' + doxdatadir + '/doxygen.css"\n')

        doxyfile.write('HTML_OUTPUT = .\n')
        doxyfile.write('QHP_VIRTUAL_FOLDER = ' + modulename + '\n')
        doxyfile.write('QHG_LOCATION = "' + args.qhelpgenerator + '"\n')
        if generate_manpages:
            doxyfile.write('GENERATE_MAN = YES\n')
        if generate_qhp:
            doxyfile.write('GENERATE_QHP = YES\n')
        if searchengine:
            doxyfile.write('SEARCHENGINE = YES\n')

        doxyfile.write('TAGFILES =')
        for (tagfile,path) in qttagfiles:
            doxyfile.write(' "' + tagfile + '=' + path + '"')
        doxyfile.write('\n')

        # module-specific settings
        if os.path.isfile('Doxyfile.local'):
            with open('Doxyfile.local') as localdoxyfile:
                for line in localdoxyfile:
                    doxyfile.write(line)
                    doxyfile.write("\n")

    subprocess.call([args.doxygen,'Doxyfile'])

    print(repr(datetime.date))
    copyright = '1996-' + str(datetime.date.today().year) + ' The KDE developers'
    # FIXME: generate classmap.inc (do this from the tags file?)
    postprocess([
            ('<!-- menu -->',generate_menu()),
            ('@topdir@','.'),
            ('@topname@',fancyname + ' API Reference'),
            ('@copyright@',copyright),
            ('@TITLE@','KDE API Reference')
            # FIXME: API searchbox
            # FIXME: cmenu
            ])

if __name__ == "__main__":
    main()

