#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os

setup(
        name='kapidox',
        version='5.27.0',
        description='KDE API documentation generation tools',
        maintainer = 'Alex Merry',
        maintainer_email = 'alex.merry@kde.org',
        url='https://projects.kde.org/projects/frameworks/kapidox',
        packages = [
            'kapidox',
            'kapidox.depdiagram'
        ],
        package_dir = {
            'kapidox': 'src/kapidox',
            'kapidox.depdiagram': 'src/kapidox/depdiagram',
        },
        package_data = {
            'kapidox': [
                'data/*.*',
                'data/htmlresource/*.*',
                'data/htmlresource/icons/*.*',
                'data/templates/*.*',
            ]
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
