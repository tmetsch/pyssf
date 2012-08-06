# coding=utf-8
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
'''
Tests for the exceptions.

Created on Nov 24, 2011

@author: tmetsch
'''

# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Method could be func' pylint check (naw...)
# pylint: disable=R0904,R0201

from occi.exceptions import HTTPError
import unittest


class TestHTTPError(unittest.TestCase):
    '''
    Test the HTTP Error class.
    '''

    def test_instanciation_for_success(self):
        '''
        Test if an HTTP Error can be instanciated.
        '''
        HTTPError(200, 'foo')

    def test_str_for_sanity(self):
        '''
        test if __str__ is ok.
        '''
        err = HTTPError(200, 'foo')
        self.assertEquals(err.__str__(), '200 - foo')
