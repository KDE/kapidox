#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='kapidox',
      version='5.0.0',
      description='KDE API documentation generation tools',
      maintainer = 'Aurélien Gâteau',
      maintainer_email = 'agateau@kde.org',
      url='https://projects.kde.org/projects/frameworks/kapidox',
      packages = ['kapidox'],
      package_dir = {'kapidox': 'src/kapidox'},
      package_data = {'kapidox': ['data/*.*', 'data/htmlresource/*']},
      scripts = ['src/kgenapidox', 'src/kgenframeworksapidox'],
      classifiers = [
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Topic :: Software Development'
          ])
