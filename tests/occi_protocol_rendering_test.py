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

from occi import registry
from occi.backend import Backend
from occi.core_model import Kind, Resource, Link, Mixin, Action
from occi.protocol.rendering import TextOcciRendering, Rendering, HTMLRendering
import unittest


class TestOcciRendering(unittest.TestCase):
    '''
    Simple sanity checks...
    '''

    rendering = TextOcciRendering()

    def setUp(self):
        # type system...
        self.kind = Kind('http://example.com#', 'foo', related=[Resource.kind])
        self.invalid_kind = Kind('http://example.com#', 'invalid')
        self.link = Kind('http://example.com#', 'link', related=[Link.kind])
        self.mixin = Mixin('http://example.com#', 'mixin')
        self.action = Action('http://example.com#', 'action')
        registry.BACKENDS[self.kind] = Backend()
        registry.BACKENDS[self.invalid_kind] = Backend()
        registry.BACKENDS[self.link] = Backend()
        registry.BACKENDS[self.mixin] = Backend()
        registry.BACKENDS[self.action] = Backend()

        # 2 linked entities
        self.entity = Resource('/foo/1', self.kind, [self.mixin])
        trg = Resource('/foo/2', self.kind, [], [])
        self.link1 = Link('/link/1', self.link, [], self.entity, trg)
        self.entity.links = [self.link1]
        registry.RESOURCES = {'/foo/2': trg,
                              '/link/1': self.link1,
                              '/foo/1': self.entity}

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
                          headers, body)

        # kind does not relate to link or resource...
        res.kind = self.invalid_kind
        headers, body = self.rendering.from_entity(res)
        self.assertRaises(AttributeError, self.rendering.to_entity,
                          headers, body)

    def test_link_for_failure(self):
        '''
        Test link...
        '''
        # call creation of entity with non existing trg resource.
        trg = Resource('/bar/1', self.kind, [], [])
        link = Link('/bar/1', self.link, [], self.entity, trg)
        headers, body = self.rendering.from_entity(link)
        self.assertRaises(AttributeError, self.rendering.to_entity,
                          headers, body)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_resource_for_sanity(self):
        '''
        Test is a resource can be rendered and retrieved.
        '''
        # basic check
        headers, body = self.rendering.from_entity(self.entity)
        new = self.rendering.to_entity(headers, body)
        self.assertEqual(self.entity.kind, new.kind)
        self.assertEqual(len(self.entity.links), len(new.links))

        # verify that actions get added
        self.entity.actions = [self.action]
        headers, body = self.rendering.from_entity(self.entity)
        self.assertTrue('?action' in headers['Link'])

    def test_link_for_sanity(self):
        '''
        Test is a link can be rendered and retrieved.
        '''
        headers, body = self.rendering.from_entity(self.link1)
        tmp = 'occi.core.target=' + self.link1.target.identifier
        tmp += ', occi.core.source=' + self.link1.source.identifier
        headers['X-OCCI-Attribute'] = tmp
        new = self.rendering.to_entity(headers, body)
        self.assertEqual(self.link1.kind, new.kind)
        # do not alter the source entity link list!
        self.assertTrue(len(self.entity.links) == 1)

    def test_action_for_sanity(self):
        '''
        Test the to actions function...
        '''
        heads = {'Category': self.action.term + '; scheme="'
                 + self.action.scheme + '"'}
        action = self.rendering.to_action(heads, None)
        self.assertEqual(action, self.action)


class TestHTMLRendering(unittest.TestCase):
    '''
    Just some simple calls on the HTML rendering.
    '''

    parser = HTMLRendering()

    def setUp(self):
        self.resource = Resource('/foo/bar', None, [])

    #==========================================================================
    # Success
    #==========================================================================

    def test_from_entity_for_success(self):
        '''
        Test from entity...
        '''
        self.parser.from_entity(self.resource)

    def test_from_entities_for_success(self):
        '''
        Test from entities...
        '''
        self.parser.from_entities([self.resource], '/')
        self.parser.from_entities([], '/')


class TestRendering(unittest.TestCase):
    '''
    Test for the abstract Rendering class.
    '''

    def test_if_not_implemented_is_thrown(self):
        '''
        Just to check the abstract class.
        '''
        rendering = Rendering()
        self.assertRaises(NotImplementedError, rendering.to_entity, None, None)
        self.assertRaises(NotImplementedError, rendering.to_action, None, None)
        self.assertRaises(NotImplementedError, rendering.from_entity, None)
        self.assertRaises(NotImplementedError, rendering.from_entities, None,
                          None)
