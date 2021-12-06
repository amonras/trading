#!/usr/bin/env python

from distutils.core import setup

setup(name='Backtesting',
      version='0.1',
      description='Backtesting tool',
      author='Alex Monras',
      author_email='amb.physis@gmail.com',
      packages=['exchanges', 'strategies', 'optimization', 'models', 'utils'],
     )