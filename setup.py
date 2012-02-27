#!/usr/bin/env python

#
# Copyright (C) 2010-2012 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
from distutils.core import setup

setup(name='pyssf',
      version='0.4.4',
      description='Service Sharing Facility',
      license='LGPL',
      keywords='OCCI, Cloud Computing, Datacenter Software',
      url='http://pyssf.sourceforge.net',
      packages=['occi', 'occi.extensions', 'occi.protocol'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Internet",
                   "Topic :: Scientific/Engineering",
                   "Topic :: Software Development",
                   "Topic :: System :: Distributed Computing",
                   "Topic :: Utilities",
                  ],
     )
