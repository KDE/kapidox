#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
        name='kapidox',
        version='5.5.0',
        description='KDE API documentation generation tools',
        maintainer = 'Aurélien Gâteau',
        maintainer_email = 'agateau@kde.org',
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
            'src/kgenapidox',
            'src/kgenframeworksapidox',
            'src/depdiagram-prepare',
            'src/depdiagram-generate',
            'src/depdiagram-generate-all',
        ],
        classifiers = [
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Software Development'
        ],
    )
