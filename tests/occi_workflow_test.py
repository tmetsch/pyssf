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
Tests the workflow module.

Created on Jul 5, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# pylint: disable=C0103,R0904

from occi import registry, workflow
from occi.core_model import Resource, Kind, Link, Action
import unittest


class EntityWorkflowTest(unittest.TestCase):
    '''
    Simple tests to test the commands on entities.
    '''

    def setUp(self):
        self.test_kind = Kind('http://example.com#', 'test')
        self.link_kind = Kind('http://example.com#link', 'link')
        mixins = []
        self.action = Action('http://example.com#', 'action')
        self.src_entity = Resource(None, self.test_kind, mixins, [])
        self.trg_entity = Resource('/foo/trg', self.test_kind, mixins, [])
        self.link1 = Link('/link/1', self.link_kind, [], self.src_entity,
                          self.trg_entity)
        self.src_entity.links = [self.link1]
        registry.RESOURCES[self.trg_entity.identifier] = self.trg_entity

    def tearDown(self):
        registry.RESOURCES = {}

    #==========================================================================
    # Success
    #==========================================================================

    def test_replace_entity_for_success(self):
        '''
        Test replace...
        '''
        # not much to verify here - just calls backends...
        workflow.replace_entity(self.src_entity, self.trg_entity)

    def test_update_entity_for_success(self):
        '''
        Test replace...
        '''
        # not much to verify here - just calls backends...
        workflow.update_entity(self.src_entity, self.trg_entity)

    def test_retrieve_entity_for_success(self):
        '''
        Test replace...
        '''
        # not much to verify here - just calls backends...
        workflow.retrieve_entity(self.src_entity)
        workflow.retrieve_entity(self.link1)

    def test_action_entity_for_success(self):
        '''
        Test replace...
        '''
        # not much to verify here - just calls backends...
        workflow.action_entity(self.src_entity, self.action)
        workflow.action_entity(self.link1, self.action)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_create_resource_for_failure(self):
        '''
        Test if create behaves correct on faulty create calls...
        '''
        # the id of this link already exists...
        link2 = Link('/link/1', self.link_kind, [], self.src_entity,
                     self.trg_entity)
        self.src_entity.links.append(link2)
        self.assertRaises(AttributeError, workflow.create_entity, '/foo/bar',
                          self.src_entity)

    def test_replace_entity_for_failure(self):
        '''
        Test replace for failure.
        '''
        self.trg_entity.links = [self.link1]
        # new entity should not have links...
        self.assertRaises(AttributeError, workflow.replace_entity,
                          self.src_entity, self.trg_entity)

    def test_update_entity_for_failure(self):
        '''
        Test update for failure.
        '''
        self.trg_entity.links = [self.link1]
        # new entity should not have links...
        self.assertRaises(AttributeError, workflow.update_entity,
                          self.src_entity, self.trg_entity)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_create_resource_link_ids_for_sanity(self):
        '''
        Test creation...
        '''
        # Check if an id get's set for the link...
        self.link1.identifier = None
        workflow.create_entity('/foo/src', self.src_entity)
        self.assertTrue(self.link1.identifier is not None)

    def test_create_resource_for_sanity(self):
        '''
        Test creation...
        '''
        workflow.create_entity('/foo/src', self.src_entity)
        # id needs to be set
        self.assertEqual(self.src_entity.identifier, '/foo/src')
        # entity needs to be available
        self.assertTrue(self.src_entity in registry.RESOURCES.values())
        # link entity needs to be available...
        self.assertTrue(self.link1 in registry.RESOURCES.values())
        self.assertTrue(len(self.src_entity.links) == 1)

    def test_create_link_for_sanity(self):
        '''
        Test creation...
        '''
        link2 = Link(None, self.link_kind, [], self.src_entity,
                     self.trg_entity)
        workflow.create_entity('/link/2', link2)
        # id needs to be set
        self.assertEqual(link2.identifier, '/link/2')
        # entity needs to be available
        self.assertTrue(link2 in registry.RESOURCES.values())
        # link needs to be added to the src entity
        self.assertTrue(link2 in self.src_entity.links)
        self.assertTrue(len(self.src_entity.links) == 2)

    def test_delete_resource_for_sanity(self):
        '''
        Test deletion...
        '''
        workflow.create_entity('/foo/src', self.src_entity)
        workflow.delete_entity(self.src_entity)
        # ensure that both the resource and it's links are removed...
        self.assertFalse(self.src_entity in registry.RESOURCES.values())
        self.assertFalse(self.link1 in registry.RESOURCES.values())

    def test_delete_link_for_sanity(self):
        '''
        Test deletion...
        '''
        workflow.create_entity('/foo/src', self.src_entity)
        workflow.delete_entity(self.link1)
        self.assertFalse(self.link1 in self.src_entity.links)
        self.assertFalse(self.link1 in registry.RESOURCES.values())
