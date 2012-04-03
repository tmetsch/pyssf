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
Module to test the parser.

Created on Jul 4, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Method could be func' pylint check (naw...)
# pylint: disable=C0103,R0904,R0201

from occi.backend import KindBackend, ActionBackend, MixinBackend
from occi.core_model import Kind, Resource, Action, Mixin
from occi.exceptions import HTTPError
from occi.protocol.occi_rendering import Rendering
from occi.registry import NonePersistentRegistry, Registry
import unittest


class TestAbstractClass(unittest.TestCase):
    '''
    Tests the abstract Registry class.
    '''

    def test_not_implemented(self):
        '''
        Test if NotImplementedErrors are thrown.
        '''
        self.assertRaises(NotImplementedError, Registry().get_renderer, None)
        self.assertRaises(NotImplementedError, Registry().set_renderer, None,
                          None)
        self.assertRaises(NotImplementedError, Registry().get_backend, None,
                          None)
        self.assertRaises(NotImplementedError, Registry().get_all_backends,
                          None, None)
        self.assertRaises(NotImplementedError, Registry().set_backend, None,
                          None, None)
        self.assertRaises(NotImplementedError, Registry().delete_mixin, None,
                          None)
        self.assertRaises(NotImplementedError, Registry().get_category, None,
                          None)
        self.assertRaises(NotImplementedError, Registry().get_categories, None)
        self.assertRaises(NotImplementedError, Registry().get_resource, None,
                          None)
        self.assertRaises(NotImplementedError, Registry().add_resource, None,
                          None, None)
        self.assertRaises(NotImplementedError, Registry().delete_resource,
                          None, None)
        self.assertRaises(NotImplementedError, Registry().get_resource_keys,
                          None)
        self.assertRaises(NotImplementedError, Registry().get_resources, None)

    def test_hostname_for_sanity(self):
        '''
        Test if hostname can be get and set.
        '''
        reg = Registry()
        reg.set_hostname('foo')
        self.assertEqual('foo', reg.get_hostname())


class TestBackendsRegistry(unittest.TestCase):
    '''
    Test for the registry.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.kind1 = Kind('http://example.com#', '1')
        self.kind2 = Kind('http://example.com#', '2')
        self.action = Action('http://example.com#', 'action')
        self.mixin = Mixin('http://example.com#', 'mixin',
                           related=[self.kind1])

        self.registry.set_backend(self.kind1, KindBackend(), None)
        self.registry.set_backend(self.kind2, DummyBackend(), None)
        self.registry.set_backend(self.action, ActionBackend(), None)
        self.registry.set_backend(self.mixin, MixinBackend(), None)

        self.entity = Resource('foo', self.kind1, [self.mixin])

    def tearDown(self):
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    #==========================================================================
    # Success
    #==========================================================================

    def test_get_backend_for_success(self):
        '''
        Test if backend can be retrieved...
        '''
        self.registry.get_backend(self.kind1, None)
        self.registry.get_backend(self.kind2, None)
        self.registry.get_backend(self.action, None)
        self.registry.get_backend(self.mixin, None)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_get_backend_for_failure(self):
        '''
        Test if backend can be retrieved...
        '''
        self.assertRaises(AttributeError, self.registry.get_backend,
                          Kind('foo', 'bar'), None)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_get_backend_for_sanity(self):
        '''
        Test if backend can be retrieved...
        '''
        back1 = self.registry.get_backend(self.kind1, None)
        back2 = self.registry.get_backend(self.kind2, None)
        self.assertTrue(isinstance(back1, KindBackend))
        self.assertTrue(isinstance(back2, DummyBackend))

    def test_get_all_backends_for_sanity(self):
        '''
        Test if all backends can be retrieved...
        '''
        backs = self.registry.get_all_backends(self.entity, None)
        self.assertTrue(len(backs) == 2)


class TestParserRegistry(unittest.TestCase):
    '''
    Test if parser can be found...
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.set_renderer('text/plain', DummyRendering(self.registry))
        self.registry.set_renderer('text/occi', DummyRendering(self.registry))

    def tearDown(self):
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    def test_get_parser_for_success(self):
        '''
        Test retrieval of parsers.
        '''
        self.registry.get_renderer('text/plain')
        self.registry.get_renderer('text/occi')

    def test_get_parser_for_failure(self):
        '''
        Test failure handling of retrieval.
        '''
        self.assertRaises(HTTPError, self.registry.get_renderer, 'foo')

    def test_set_parser_for_failure(self):
        '''
        Test failure handling of setting a renderer.
        '''
        self.assertRaises(AttributeError, self.registry.set_renderer, 'foo',
                          None)

    def test_get_parser_for_sanity(self):
        '''
        Some sanity checks.
        '''
        parser1 = self.registry.get_renderer('text/plain')
        parser2 = self.registry.get_renderer('text/plain;q=0.9')
        parser3 = self.registry.get_renderer('*/*')

        self.assertEquals(parser1, parser3)
        self.assertEquals(parser2, parser3)


class CategoryRegistryTest(unittest.TestCase):
    '''
    Test the capabilities to retrieve categories.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.kind1 = Kind('http://example.com#', '1')
        self.kind2 = Kind('http://example.com#', '2', location='/foo/')

        self.registry.set_backend(self.kind1, KindBackend(), None)
        self.registry.set_backend(self.kind2, DummyBackend(), None)

    def tearDown(self):
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    def test_get_category_for_sanity(self):
        '''
        Test if the category can be retrieved from a URN.
        '''
        result = self.registry.get_category('/1/', None)
        self.assertTrue(self.kind1 == result)

        result = self.registry.get_category('/foo/', None)
        self.assertTrue(self.kind2 == result)

        result = self.registry.get_category('/bar/', None)
        self.assertTrue(result == None)

    def test_set_category_for_sanity(self):
        '''
        Test the hash function of the categories...
        '''
        cat1 = Kind('http://example.com#', 'foo')
        cat2 = Kind('http://example.com#', 'foo')

        self.assertEqual(cat1, cat2)


class ResourcesTest(unittest.TestCase):
    '''
    Tests the reigstry's resource handling.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.res1 = Resource('foo', None, None)
        self.res2 = Resource('bar', None, None)

    def tearDown(self):
        for resource in self.registry.get_resources(None):
            self.registry.delete_resource(resource.identifier, None)

    def test_get_resource_for_sanity(self):
        '''
        Test if added resource can be retrieved.
        '''
        self.registry.add_resource('foo', self.res1, None)
        self.assertEquals(self.res1, self.registry.get_resource('foo', None))

    def test_delete_resource_for_sanity(self):
        '''
        Test if delete resource cannot be retrieved.
        '''
        self.registry.add_resource('foo', self.res1, None)
        self.registry.delete_resource('foo', None)
        self.assertRaises(KeyError, self.registry.get_resource, 'foo', None)

    def test_resources_for_sanity(self):
        '''
        Test is all resources and all keys can be retrieved.
        '''
        self.registry.add_resource('foo', self.res1, None)
        self.registry.add_resource('bar', self.res2, None)
        self.assertTrue(len(self.registry.get_resources(None)) == 2)
        self.assertTrue(len(self.registry.get_resource_keys(None)) == 2)


class DummyBackend(KindBackend):
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


class DummyRegistry(Registry):
    '''
    Just here to satify pylint and so Registry os referenced more than once...
    '''

    # disabling 'Not implemented' pylint check (well wedon't need it:))
    # pylint: disable=W0223

    pass
