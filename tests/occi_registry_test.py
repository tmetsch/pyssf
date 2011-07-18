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
Module to test the parser.

Created on Jul 4, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Method could be func' pylint check (naw...)
# pylint: disable=C0103,R0904,R0201

from occi import registry
from occi.backend import Backend
from occi.core_model import Kind, Resource
from occi.protocol.occi_rendering import Rendering
import unittest


class TestBackendsRegistry(unittest.TestCase):
    '''
    Test for the registry.
    '''

    def setUp(self):
        self.kind1 = Kind('http://example.com#', '1')
        self.kind2 = Kind('http://example.com#', '2')

        registry.BACKENDS = {self.kind1: Backend(),
                             self.kind2: DummyBackend()}

        self.entity = Resource('foo', self.kind1, [self.kind2])

    #==========================================================================
    # Success
    #==========================================================================

    def test_get_backend_for_success(self):
        '''
        Test if backend can be retrieved...
        '''
        registry.get_backend(self.kind1)
        registry.get_backend(self.kind2)

    #==========================================================================
    # Failure
    #==========================================================================

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_get_backend_for_sanity(self):
        '''
        Test if backend can be retrieved...
        '''
        back1 = registry.get_backend(self.kind1)
        back2 = registry.get_backend(self.kind2)
        back3 = registry.get_backend(Kind('foo', 'bar'))
        self.assertTrue(isinstance(back1, Backend))
        self.assertTrue(isinstance(back2, DummyBackend))
        self.assertTrue(isinstance(back3, Backend))

    def test_get_all_backends_for_sanity(self):
        '''
        Test if all backends can be retrieved...
        '''
        backs = registry.get_all_backends(self.entity)
        self.assertTrue(len(backs) == 2)


class TestParserRegistry(unittest.TestCase):
    '''
    Test if parser can be found...
    '''

    def setUp(self):
        registry.RENDERINGS = {'text/plain': DummyRendering,
                               'text/occi': DummyRendering}

    def test_get_parser_for_success(self):
        '''
        Test retrieval of parsers.
        '''
        registry.get_parser('text/plain')
        registry.get_parser('text/occi')

    def test_get_parser_for_failure(self):
        '''
        Test failure handling of retrieval.
        '''
        self.assertRaises(AttributeError, registry.get_parser, 'foo')

    def test_get_parser_for_sanity(self):
        '''
        Some sanity checks.
        '''
        parser1 = registry.get_parser('text/plain')
        parser2 = registry.get_parser('text/plain;q=0.9')
        parser3 = registry.get_parser('*/*')

        self.assertEquals(parser1, parser3)
        self.assertEquals(parser2, parser3)


class CategoryRegistryTest(unittest.TestCase):
    '''
    Test the capabilities to retrieve categories.
    '''

    def setUp(self):
        self.kind1 = Kind('http://example.com#', '1')
        self.kind2 = Kind('http://example.com#', '2', location='/foo/')

        registry.BACKENDS = {self.kind1: Backend(),
                             self.kind2: DummyBackend()}

    def test_get_category_for_sanity(self):
        '''
        Test if the category can be retrieved from a URN.
        '''
        result = registry.get_category('/1/')
        self.assertTrue(self.kind1 == result)

        result = registry.get_category('/foo/')
        self.assertTrue(self.kind2 == result)

        result = registry.get_category('/bar/')
        self.assertTrue(result == None)


class DummyBackend(Backend):
    '''
    A dummy...
    '''

    pass


class DummyRendering(Rendering):
    '''
    A dummy...
    '''

    # disabling 'Not overridden' pylint check (not needed here)
    # pylint: disable=W0223

    pass
