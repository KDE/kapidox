#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os

# Walk list of data files to install to ensure we install everything. This
# needs to generate paths relative to the package source.
kapidox_data_files = []
for root, dirs, files in os.walk('src/kapidox/data/'):
    data_root = os.path.relpath(root, 'src/kapidox/')
    root_files = [os.path.join(data_root, f) for f in files]
    kapidox_data_files += root_files

setup(
        name='kapidox',
        version='5.64.0',
        description='KDE API documentation generation tools',
        maintainer = 'Olivier Churlaud',
        maintainer_email = 'olivier@churlaud.com',
        url='https://cgit.kde.org/kapidox.git',
        packages = [
            'kapidox',
            'kapidox.depdiagram'
        ],
        package_dir = {
            'kapidox': 'src/kapidox',
            'kapidox.depdiagram': 'src/kapidox/depdiagram',
        },
        package_data = {
            'kapidox': kapidox_data_files
        },
        scripts = [
            'src/kapidox_generate',
            'src/depdiagram-prepare',
            'src/depdiagram-generate',
            'src/depdiagram-generate-all',
        ],
        data_files= [
            (os.path.join('share', 'man', 'man1'), ['docs/depdiagram-prepare.1',
                'docs/depdiagram-generate.1',
                'docs/depdiagram-generate-all.1'])],
        classifiers = [
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Software Development'
        ],
    )
