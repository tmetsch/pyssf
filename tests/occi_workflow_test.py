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
from occi.backend import Backend
from occi.core_model import Resource, Kind, Link, Action, Mixin
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


class CollectionWorkflowTest(unittest.TestCase):
    '''
    Test the workflow on operations on collections...
    '''

    def setUp(self):
        self.kind = Kind('http://example.com/foo#', 'bar')
        self.link_kind = Kind('http://example.com/foo#', 'link')
        self.mixin = Mixin('http://example.com/foo#', 'mixin')

        target = Resource('/foo/target', self.kind, [], [])

        source = Resource('/foo/src', self.kind, [self.mixin], [])
        source.attributes = {'foo': 'bar'}

        link = Link('/link/foo', self.link_kind, [], source, target)
        link.attributes = {'foo': 'bar'}
        source.links = [link]

        self.resources = [source, target, link]
        for item in self.resources:
            registry.RESOURCES[item.identifier] = item

        registry.BACKENDS[self.kind] = Backend

    def tearDown(self):
        registry.RESOURCES = {}
        registry.BACKENDS = {}

    #==========================================================================
    # Success
    #==========================================================================

    def test_get_entities_for_success(self):
        '''
        Tests retrieval of resources.
        '''
        lst = workflow.get_entities_under_path('/')
        self.assertTrue(self.resources[0] in lst)

    def test_filter_entities_for_success(self):
        '''
        Call the filter test.
        '''
        workflow.filter_entities(self.resources, [], {})
        workflow.filter_entities(self.resources, [self.kind], {})
        workflow.filter_entities(self.resources, [], {'foo': 'bar'})

    #==========================================================================
    # Failure
    #==========================================================================

    def test_update_collection_for_failure(self):
        '''
        Check if the update functionalities are implemented correctly.
        '''
        self.assertRaises(AttributeError, workflow.update_collection,
                          self.kind, [], [])

    def test_replace_collection_for_failure(self):
        '''
        Check if the replace functionalities are implemented correctly.
        '''
        self.assertRaises(AttributeError, workflow.replace_collection,
                          self.kind, [], [])

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_get_entities_for_sanity(self):
        '''
        Test if correct entities are returned.
        '''
        lst = workflow.get_entities_under_path('/link/')
        self.assertTrue(self.resources[2] in lst)
        self.assertTrue(len(lst) == 1)

        lst = workflow.get_entities_under_path('/bar/')
        self.assertTrue(self.resources[0] in lst)
        self.assertTrue(self.resources[1] in lst)
        self.assertTrue(len(lst) == 2)

    def test_update_collection_for_sanity(self):
        '''
        Check if the update functionalities are implemented correctly.
        '''
        res1 = Resource('/foo/target', self.kind, [self.mixin], [])
        res2 = Resource('/foo/target', self.kind, [], [])
        workflow.update_collection(self.mixin, [res1], [res2])
        self.assertTrue(self.mixin in res1.mixins)
        self.assertTrue(self.mixin in res2.mixins)

    def test_replace_collection_for_sanity(self):
        '''
        Check if the replace functionalities are implemented correctly.
        '''
        res1 = Resource('/foo/target', self.kind, [self.mixin], [])
        res2 = Resource('/foo/target', self.kind, [], [])
        workflow.replace_collection(self.mixin, [res1], [res2])
        self.assertTrue(self.mixin not in res1.mixins)
        self.assertTrue(self.mixin in res2.mixins)

    def test_filter_entities_for_sanity(self):
        '''
        Check if the filter operates correctly.
        '''
        # return all
        res = workflow.filter_entities(self.resources, [], {})
        self.assertTrue(self.resources[0] in res)
        self.assertTrue(self.resources[1] in res)
        self.assertTrue(self.resources[2] in res)
        self.assertTrue(len(res) == 3)

        # return just the two resources
        res = workflow.filter_entities(self.resources, [self.kind], {})
        self.assertTrue(self.resources[0] in res)
        self.assertTrue(self.resources[1] in res)
        self.assertTrue(len(res) == 2)

        # return source and link
        res = workflow.filter_entities(self.resources, [], {'foo': 'bar'})
        self.assertTrue(self.resources[0] in res)
        self.assertTrue(self.resources[2] in res)
        self.assertTrue(len(res) == 2)

        # return just the source
        res = workflow.filter_entities(self.resources, [self.mixin], {})
        self.assertTrue(self.resources[0] in res)
        self.assertTrue(len(res) == 1)

        # return just the source and link
        res = workflow.filter_entities(self.resources, [self.mixin,
                                                        self.link_kind], {})
        self.assertTrue(self.resources[0] in res)
        self.assertTrue(self.resources[2] in res)
        self.assertTrue(len(res) == 2)

        # return just the link...
        res = workflow.filter_entities(self.resources, [self.kind],
                                       {'foo': 'bar'})
        self.assertTrue(self.resources[0] in res)
        self.assertTrue(len(res) == 1)


class QueriyInterfaceTest(unittest.TestCase):
    '''
    Tests the QI routines.
    '''

    def setUp(self):
        self.kind1 = Kind('http://www.example.com#', 'foo')
        self.kind2 = Kind('http://www.example.com#', 'bar')
        self.mixin = Mixin('http://www.new.com#', 'bar')
        registry.BACKENDS = {self.kind1: Backend(), self.kind2: Backend()}

    def tearDown(self):
        registry.BACKENDS = {}

    #==========================================================================
    # Failure
    #==========================================================================

    def test_append_mixin_for_failure(self):
        '''
        Test if exception is thrown.
        '''
        self.assertRaises(AttributeError, workflow.append_mixin, self.kind2)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_filter_categories_for_sanity(self):
        '''
        Test the simple filter options.
        '''
        res = workflow.filter_categories([])
        self.assertTrue(self.kind1 in res)
        self.assertTrue(self.kind2 in res)
        self.assertTrue(len(res) == 2)

        res = workflow.filter_categories([self.kind1])
        self.assertTrue(self.kind1 in res)
        self.assertFalse(self.kind2 in res)
        self.assertTrue(len(res) == 1)

    def test_append_mixin_for_sanity(self):
        '''
        Test if mixins get appended.
        '''
        workflow.append_mixin(self.mixin)
        self.assertTrue(self.mixin in registry.BACKENDS)
        self.assertTrue(isinstance(registry.BACKENDS[self.mixin], Backend))

    def test_remove_mixin_for_sanity(self):
        '''
        Test if mixin get removed.
        '''
        workflow.append_mixin(self.mixin)
        workflow.remove_mixin(self.mixin)
        self.assertFalse(self.mixin in registry.BACKENDS)
