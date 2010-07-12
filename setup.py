#!/usr/bin/env python

# 
# Copyright (C) 2010  Platform Computing
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 

from distutils.core import setup, Extension

setup(name = 'Service Sharing Facility',
      version = '0.1',
      license = 'LICENSE',
      description = 'Service Sharing Facility',
      author = 'Thijs Metsch',
      author_email = 'tmetsch@platform.com',
      url = 'http://www.platform.com',
      packages = ['ssf', 'pyrest'],
      ext_package = 'pylsf',
      ext_modules = [Extension('_lsf', ['pylsf/lsf.i'],
                               include_dirs = ['/usr/include/python2.6'],
                               library_dirs = ['/opt/lsf/7.0/linux2.6-glibc2.3-x86/lib'],
                               libraries = ['c', 'nsl', 'lsf', 'bat', 'fairshareadjust', 'lsbstream'])],
      py_modules = ['pylsf.lsf'],
     )



