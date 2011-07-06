#
# Copyright (C) 2010-2011 Platform Computing
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
Some tests for the core model...

Created on Jul 5, 2011

@author: tmetsch
'''

# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Method could be func' pylint check (naw...)
# pylint: disable=R0904,R0201

from occi.core_model import Category, Kind, Action, Mixin, Resource, Link
import unittest


class TestCore(unittest.TestCase):
    '''
    Some sanity checks for the core model.
    '''

    def test_type_system_for_sanity(self):
        '''
        Test category, Action, Kind and Mixin.
        '''
        cat1 = Category('http://example.com#', 'foo')
        cat2 = Category('http://example.com#', 'foo')
        kind = Kind('http://example.com#', 'bar')
        action = Action('http://example.com#', 'action')
        mixin = Mixin('http://example.com#', 'mixin')

        # test eq
        self.assertEquals(cat1, cat2)
        self.assertFalse(cat1 == str)
        self.assertFalse(cat1 == kind)

        # test str
        self.assertEqual(str(cat1), 'http://example.com#foo')

        # test repr
        self.assertEqual(repr(kind), 'kind')
        self.assertEqual(repr(action), 'action')
        self.assertEqual(repr(mixin), 'mixin')

    def test_entities_for_sanity(self):
        '''
        Tests for Entity, Resource and Link.
        '''
        Resource(None, None, None)
        Link(None, None, None, 'foo', 'bar')
