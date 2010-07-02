#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name = 'Platform SSF',
      version = '0.1',
      description = 'Service Sharing Facility',
      author = 'Thijs Metsch',
      author_email = 'tmetsch@platform.com',
      url = 'http://www.platform.com',
      packages = ['ssf'],
      ext_package = 'pylsf',
      ext_modules = [Extension('_lsf', ['pylsf/lsf.i'],
                               include_dirs = ['/usr/include/python2.6'],
                               library_dirs = ['/opt/lsf/7.0/linux2.6-glibc2.3-x86_64/lib'],
                               libraries = ['c', 'nsl', 'lsf', 'bat', 'fairshareadjust', 'lsbstream'])],
      py_modules = ['pylsf.lsf'],
     )
