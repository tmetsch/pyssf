# coding=utf-8
'''
Created on Feb 2, 2012

@author: tmetsch
'''

# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Invalid name' pylint check (We need longer names here)
# pylint: disable=R0904,C0103

from occi.core_model import Action, Kind, Mixin, Resource, Link
from occi.protocol.json_rendering import JsonRendering
from occi.registry import NonePersistentRegistry
import unittest


class JsonRenderingTest(unittest.TestCase):
    '''
    Test for the Json rendering.
    '''

    parser = JsonRendering(NonePersistentRegistry())

    def setUp(self):
        action = Action('http://example.com/foo#', 'action')

        self.kind = Kind('http://example.com/foo#', 'bar',
                         ['http://schemeas.ogf.org/occi/core#'],
                          [action], 'Some bla bla',
                          {'foo': 'required', 'foo2': 'immutable', 'bar': ''},
                          '/foo/')
        self.mixin = Mixin('http://example.com/foo#', 'mixin')
        self.action = Action('http://example.com/foo#', 'action')

        self.target = Resource('/foo/target', self.kind, [], [])
        self.source = Resource('/foo/src', self.kind, [self.mixin], [])

        self.link = Link('/link/foo', self.kind, [], self.source, self.target)

        self.source.links = [self.link]
        self.source.actions = [action]
        self.source.attributes = {'occi.compute.cores': 2}

    #==========================================================================
    # Success
    #==========================================================================

    def test_from_entity_for_success(self):
        '''
        Test from entity...
        '''
        self.parser.from_entity(self.link)
        self.parser.from_entity(self.source)

    def test_from_entities_for_success(self):
        '''
        Test from entities...
        '''
        self.parser.from_entities([self.source], '/foo/')
        self.parser.from_entities([], '/foo/')

    def test_from_categories_for_success(self):
        '''
        Test from categories...
        '''
        self.parser.from_categories([self.kind, self.mixin, self.action])
