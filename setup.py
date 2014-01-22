#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
        name='kapidox',
        version='5.0.0',
        description='KDE API documentation generation tools',
        maintainer = 'Aurélien Gâteau',
        maintainer_email = 'agateau@kde.org',
        url='https://projects.kde.org/projects/frameworks/kapidox',
        packages = [
            'kapidox',
            'kapidox.kf5dot'
        ],
        package_dir = {
            'kapidox': 'src/kapidox',
            'kapidox.kf5dot': 'src/kapidox/kf5dot',
        },
        package_data = {'kapidox': ['data/*.*', 'data/htmlresource/*']},
        scripts = [
            'src/kgenapidox',
            'src/kgenframeworksapidox',
            'src/kf5dot-prepare',
            'src/kf5dot-generate',
            'src/kf5dot-generate-all',
        ],
        classifiers = [
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Software Development'
        ],
    )
