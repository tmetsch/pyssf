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
Tests for the renderings.

Created on Jul 5, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# pylint: disable=C0103,R0904

from occi.backend import KindBackend, MixinBackend, ActionBackend
from occi.core_model import Kind, Resource, Link, Mixin, Action
from occi.handlers import CONTENT_TYPE
from occi.protocol.occi_rendering import TextOcciRendering, Rendering, \
    TextPlainRendering, TextUriListRendering
from occi.registry import NonePersistentRegistry
import unittest


class TestTextOcciRendering(unittest.TestCase):
    '''
    Simple sanity checks...
    '''

    # disable 'Unused attr' pylint check (not needing body here)
    # disable 'Too many instance attributes' pyling check (It's a test :))
    # pylint: disable=W0612,R0902

    registry = NonePersistentRegistry()

    def setUp(self):
        self.rendering = TextOcciRendering(self.registry)
        # type system...
        self.kind = Kind('http://example.com#', 'foo', related=[Resource.kind])
        self.invalid_kind = Kind('http://example.com#', 'invalid')
        self.link = Kind('http://example.com#', 'link', related=[Link.kind])
        self.mixin = Mixin('http://example.com#', 'mixin')
        self.action = Action('http://example.com#', 'action')

        self.registry.set_backend(self.kind, KindBackend())
        self.registry.set_backend(self.invalid_kind, KindBackend())
        self.registry.set_backend(self.link, KindBackend())
        self.registry.set_backend(self.mixin, MixinBackend())
        self.registry.set_backend(self.action, ActionBackend())

        # 2 linked entities
        self.entity = Resource('/foo/1', self.kind, [self.mixin])
        trg = Resource('/foo/2', self.kind, [], [])
        self.link1 = Link('/link/1', self.link, [], self.entity, trg)
        self.entity.links = [self.link1]

        self.registry.add_resource('/foo/2', trg)
        self.registry.add_resource('/link/1', self.link1)
        self.registry.add_resource('/foo/1', self.entity)

    def tearDown(self):
        for res in self.registry.get_resources():
            self.registry.delete_resource(res.identifier)
        for item in self.registry.get_categories():
            self.registry.delete_mixin(item)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_resource_for_failure(self):
        '''
        Check if the correct exceptions are thrown.
        '''
        # no kind available...
        res = Resource('/foo/1', self.mixin, [], links=[])
        headers, body = self.rendering.from_entity(res)
        self.assertRaises(AttributeError, self.rendering.to_entity,
                          headers, body, None)

        # kind does not relate to link or resource...
        res.kind = self.invalid_kind
        headers, body = self.rendering.from_entity(res)
        self.assertRaises(AttributeError, self.rendering.to_entity,
                          headers, body, None)

    def test_resources_for_failure(self):
        '''
        Tests is a set of resource can be set and retrieved.
        '''
        heads = {'X-OCCI-Location': '/bla/bla/2'}
        self.assertRaises(AttributeError, self.rendering.to_entities, heads,
                          '')

    def test_link_for_failure(self):
        '''
        Test link...
        '''
        # call creation of entity with non existing trg resource.
        trg = Resource('/bar/1', self.kind, [], [])
        link = Link('/bar/1', self.link, [], self.entity, trg)
        headers, body = self.rendering.from_entity(link)
        self.assertRaises(AttributeError, self.rendering.to_entity,
                          headers, body, None)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_resource_for_sanity(self):
        '''
        Test is a resource can be rendered and retrieved.
        '''
        # basic check
        headers, body = self.rendering.from_entity(self.entity)
        new = self.rendering.to_entity(headers, body, None)
        self.assertEqual(self.entity.kind, new.kind)
        self.assertEqual(len(self.entity.links), len(new.links))

        # verify that provided kind is taken
        kind = Kind('foo', 'bar', related=[Resource.kind])
        headers, body = self.rendering.from_entity(self.entity)
        new = self.rendering.to_entity(headers, body, kind)
        self.assertEqual(new.kind, kind)
        self.assertEqual(len(self.entity.links), len(new.links))

        # verify that actions get added
        self.entity.actions = [self.action]
        headers, body = self.rendering.from_entity(self.entity)
        self.assertTrue('?action' in headers['Link'])

    def test_resources_for_sanity(self):
        '''
        Tests is a set of resource can be set and retrieved for sanity.
        '''
        res = self.registry.get_resources()
        heads, body = self.rendering.from_entities(res, '/')
        entities = self.rendering.to_entities(heads, body)
        self.assertEqual(self.registry.get_resources(), entities)

    def test_link_for_sanity(self):
        '''
        Test is a link can be rendered and retrieved.
        '''
        headers, body = self.rendering.from_entity(self.link1)
        tmp = 'occi.core.target=' + self.link1.target.identifier
        tmp += ', occi.core.source=' + self.link1.source.identifier
        headers['X-OCCI-Attribute'] = tmp
        new = self.rendering.to_entity(headers, body, None)
        self.assertEqual(self.link1.kind, new.kind)
        # do not alter the source entity link list!
        self.assertTrue(len(self.entity.links) == 1)

    def test_qi_categories_for_sanity(self):
        '''
        Tests QI interface rendering...
        '''
        heads = {'Category': 'foo; scheme="http://example.com#";' +
                 ' location="/foo/"'}
        mixins = self.rendering.to_mixins(heads, '')
        headers, body = self.rendering.from_categories(mixins)
        self.assertTrue('foo' in headers['Category'])
        self.assertTrue('scheme="http://example.com#"' in headers['Category'])
        self.assertTrue('location="/foo/"' in headers['Category'])

    def test_action_for_sanity(self):
        '''
        Test the to actions function...
        '''
        heads = {'Category': self.action.term + '; scheme="'
                 + self.action.scheme + '"'}
        action = self.rendering.to_action(heads, None)
        self.assertEqual(action, self.action)

    def test_get_filters_for_sanity(self):
        '''
        Test if filters can be retrieved...
        '''
        headers, body = self.rendering.from_categories([self.kind])
        cats, attrs = self.rendering.get_filters(headers, '')
        self.assertTrue(cats == [self.kind])
        self.assertTrue(attrs == {})

        headers['X-OCCI-Attribute'] = 'foo="bar"'
        cats, attrs = self.rendering.get_filters(headers, '')
        self.assertTrue(cats == [self.kind])
        self.assertTrue(attrs['foo'] == 'bar')


class TestTextPlainRendering(unittest.TestCase):
    '''
    Test the text / plain rendering. This is simple since it's derived from
    text/occi rendering.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.rendering = TextPlainRendering(self.registry)

    def test_data_routines_for_sanity(self):
        '''
        Test if set and get data are overwritten and work properly
        '''
        headers = {}
        body = 'Category: foo\n' \
            'Category: foo,bar\n' \
            'Link: bar\n' \
            'Link: foo,bar\n' \
            'X-OCCI-Location: foo,bar\n' \
            'X-OCCI-Location: bar\n' \
            'X-OCCI-Attribute: foo\n' \
            'X-OCCI-Attribute: bar,foo\n'
        data = self.rendering.get_data(headers, body)
        headers, body = self.rendering.set_data(data)
        self.assertTrue(body.count('Category') == 3)
        self.assertTrue(body.count('Link') == 3)
        self.assertTrue(body.count('X-OCCI-Attribute') == 3)
        self.assertTrue(body.count('X-OCCI-Location') == 3)


class TestTextURIListRendering(unittest.TestCase):
    '''
    Test the uri-list rendering.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.rendering = TextUriListRendering(self.registry)

    def test_from_entities_for_sanity(self):
        '''
        Test uri listings...
        '''
        res = Resource('/foo/123', None, [])
        entities = [res]
        heads, body = self.rendering.from_entities(entities, 'foo')
        self.assertTrue(heads == {CONTENT_TYPE: self.rendering.mime_type})
        self.assertTrue(res.identifier in body)

    def test_not_support_thrown_for_success(self):
        '''
        Tests is attr-exp are thrown for unsupported operations.
        '''
        self.assertRaises(AttributeError, self.rendering.to_entity, None,
                          None, None)
        self.assertRaises(AttributeError, self.rendering.from_entity, None)
        self.assertRaises(AttributeError, self.rendering.to_entities, None,
                          None)
        self.assertRaises(AttributeError, self.rendering.from_categories, None)
        self.assertRaises(AttributeError, self.rendering.to_action, None, None)
        self.assertRaises(AttributeError, self.rendering.to_mixins, None, None)
        self.assertRaises(AttributeError, self.rendering.get_filters, None,
                          None)


class TestRendering(unittest.TestCase):
    '''
    Test for the abstract Rendering class.
    '''

    registry = NonePersistentRegistry()

    def test_if_not_implemented_is_thrown(self):
        '''
        Just to check the abstract class.
        '''
        rendering = Rendering(self.registry)
        self.assertRaises(NotImplementedError, rendering.to_entity, None, None,
                          None)
        self.assertRaises(NotImplementedError, rendering.to_action, None, None)
        self.assertRaises(NotImplementedError, rendering.to_entities, None,
                          None)
        self.assertRaises(NotImplementedError, rendering.to_mixins, None, None)
        self.assertRaises(NotImplementedError, rendering.get_filters, None,
                          None)
        self.assertRaises(NotImplementedError, rendering.from_entity, None)
        self.assertRaises(NotImplementedError, rendering.from_categories, None)
        self.assertRaises(NotImplementedError, rendering.from_entities, None,
                          None)
