#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
      name='coursera',
      version='1.0',
      description='Automatize tasks in Coursera course\'s sites, namely the download of resources.',
      author='Francisco José Marques Vieira',
      author_email='francisco.j.m.vieira@gmail.com',
      url='https://github.com/fvieira/coursera_resources_downloader',
      scripts = ['coursera'],
      requires=[
          'argparse',
          'lxml',
          'requests',
      ],
)
