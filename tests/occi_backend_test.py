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
Some tests for the backend.

Created on Jul 5, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Method could be function' pyling check (well guess who's fault..)
# pylint: disable=C0103,R0904,R0201

from occi import backend
from occi.backend import KindBackend, ActionBackend
from occi.core_model import Kind, Resource, Link, Action
import unittest


class TestKindBackend(unittest.TestCase):
    '''
    Some sanity checks for convenient routines in the backend.
    '''

    def setUp(self):
        self.back = KindBackend()
        self.action = Action('foo', 'action')
        self.kind = Kind('foo', 'bar', actions=[self.action],
                         attributes={'foo': 'mutable', 'bar': 'required'})
        self.link_kind = Kind('foo', 'bar', related=self.kind)
        self.resource = Resource('/foo/1', self.kind, [])
        self.resource.actions = [self.action]
        self.link = Link('/link/1', self.link_kind, [], None, self.resource)

    def test_simple_calls(self):
        '''
        Test all possible calls if the pass...
        '''
        self.back.create(None, None)
        self.back.retrieve(None, None)
        self.back.delete(None, None)
        self.back.update(None, None, None)
        self.back.replace(None, None, None)

    def test_is_related_for_sanity(self):
        '''
        Tests links...
        '''
        self.assertTrue(backend.is_related_valid(self.link))
        link2 = Link('/link/2', self.kind, [], None, self.resource)
        self.assertFalse(backend.is_related_valid(link2))

    def test_attr_mutable_for_sanity(self):
        '''
        Test attributes.
        '''
        self.assertFalse(backend.is_attr_mutable(self.kind, 'bar'))
        self.assertTrue(backend.is_attr_mutable(self.kind, 'foo'))

    def test_attr_required_for_sanity(self):
        '''
        Test attributes.
        '''
        self.assertFalse(backend.is_attr_required(self.kind, 'foo'))
        self.assertTrue(backend.is_attr_required(self.kind, 'bar'))

    def test_action_applicable_for_sanity(self):
        '''
        Test action stuff.
        '''
        self.assertTrue(backend.is_action_applicable(self.resource,
                                                     self.action))

        action2 = Action('foo', 'start')
        self.assertFalse(backend.is_action_applicable(self.resource, action2))

        action3 = Action('foo', 'start')
        self.resource.actions.append(action3)
        self.assertFalse(backend.is_action_applicable(self.resource, action3))


class TestActionBackend(unittest.TestCase):
    '''
    Test the Action backend...
    '''

    def test_simple_calls(self):
        '''
        Test if default pass...
        '''
        back = ActionBackend()
        back.action(None, None, None, None)
