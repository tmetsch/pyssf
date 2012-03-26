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
Tests for the renderings.

Created on Jul 5, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# pylint: disable=C0103,R0904

from occi.core_model import Resource, Kind, Link, Action, Mixin
from occi.protocol.html_rendering import HTMLRendering
from occi.registry import NonePersistentRegistry
import unittest


class TestHTMLRendering(unittest.TestCase):
    '''
    Just some simple calls on the HTML rendering.
    '''

    registry = NonePersistentRegistry()
    parser = HTMLRendering(registry)

    def setUp(self):
        action = Action('http://example.com/foo#', 'action')
        self.kind = Kind('http://example.com/foo#', 'bar',
                         'http://schemeas.ogf.org/occi/core#',
                          [action], 'Some bla bla',
                          {'foo': 'required', 'foo2': 'immutable', 'bar': ''},
                          '/foo/')
        mixin = Mixin('http://example.com/foo#', 'mixin')
        action = Action('http://example.com/foo#', 'action')
        self.target = Resource('/foo/target', self.kind, [], [])
        self.source = Resource('/foo/src', self.kind, [mixin], [])
        self.link = Link('/link/foo', self.kind, [], self.source, self.target)
        self.source.links = [self.link]
        self.source.actions = [action]

        self.registry.set_backend(action, None, None)

    #==========================================================================
    # Success
    #==========================================================================

    def test_init_for_success(self):
        '''
        Test init...
        '''
        parser = HTMLRendering(NonePersistentRegistry(),
                               css='body {background: #d00;}')
        self.assertEquals(parser.css, 'body {background: #d00;}')

    def test_from_entity_for_success(self):
        '''
        Test from entity...
        '''
        self.parser.from_entity(self.source)
        self.parser.from_entity(self.link)

    def test_from_entities_for_success(self):
        '''
        Test from entities...
        '''
        self.parser.from_entities([self.source], '/foo/')
        self.parser.from_entities([], '/')

    def test_from_categories_for_success(self):
        '''
        Test from categories...
        '''
        self.parser.from_categories([self.kind])

    def test_to_action_for_success(self):
        '''
        Test actions...
        '''
        self.parser.to_action({'Query_String':
                               'action=action?scheme=http://example.com/foo'},
                              'foobar', None)

    #==========================================================================
    # Test for failure
    #==========================================================================

    def test_to_action_for_failure(self):
        '''
        Test actions...
        '''
        self.assertRaises(AttributeError, self.parser.to_action,
                          {'Query_String': 'action=foo?'}, '', None)
        self.assertRaises(AttributeError, self.parser.to_action,
                          {'Query_String': 'scheme=bar'}, '', None)
        self.assertRaises(AttributeError, self.parser.to_action,
                          {'Query_String': 'action=foo?scheme=bar'}, '', None)
