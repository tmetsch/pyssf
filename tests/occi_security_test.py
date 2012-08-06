# coding=utf-8
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
Unittest mostly to demo security dealings.

Created on Mar 26, 2012

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Too few public methos' pylint check (dummies are small...)
# pylint: disable=C0103,R0904,R0903

from occi.backend import KindBackend
from occi.core_model import Mixin, Entity
from occi.exceptions import HTTPError
from occi.extensions.infrastructure import COMPUTE
from occi.protocol import occi_parser
from occi.protocol.occi_rendering import TextOcciRendering
from occi.registry import NonePersistentRegistry
from occi.wsgi import Application
import unittest


class MyRegistry(NonePersistentRegistry):
    '''
    An self written registry which does security checks on listings.

    NOTE: you would need to overwrite get_resource_keys as well to be ueber
    perfect.
    '''

    def get_extras(self, extras):
        return extras['sec']['id']


class MyApplication(Application):
    '''
    Overwritten OCCI app with security handling
    '''

    def __call__(self, environ, response):
        '''
        Create a security object.

        environ -- environment.
        response -- The reponse object.
        '''
        sec_obj = {'id': environ['username']}
        return self._call_occi(environ, response, sec=sec_obj)


class SecurityChecksTest(unittest.TestCase):
    '''
    Following assumptions are made:

    Security should be handled in the real application not the pyssf framework.

    Therefore security in general should be handled in the backends. Compare
    the values in the sec_obj (passed through the extras argument) and compare
    it with the security objects in your own application. You should however
    also set the entity.owner attribute so that the registry can do a compare
    itself for the listing of all resource.

    While doing this it is assured that no unauthorized access/modifications
    are made.
    '''

    env = {'SERVER_NAME': 'localhost',
           'SERVER_PORT': '8888',
           'PATH_INFO': '/compute/',
           'REQUEST_METHOD': 'GET'}

    my_registry = MyRegistry()

    def setUp(self):
        '''
        Setup an OCCI app with own registry and overwritten call methid (for
        the extras argument).
        '''
        unittest.TestCase.setUp(self)

        self.my_registry.set_renderer('text/occi',
                                 TextOcciRendering(self.my_registry))

        tmp = Entity('foo', '', COMPUTE, [])
        self.my_registry.add_resource('foo', tmp, None)

        backend = MyBackend()

        self.my_registry.set_backend(COMPUTE, backend, None)

    def tearDown(self):
        self.my_registry.backends = {}
        self.my_registry.resources = {}
        self.my_registry = None

    #==========================================================================
    # Test for failure
    #==========================================================================

    def test_get_query_interface_for_failure(self):
        '''
        Check that only resource belong to a user are shown.
        '''
        app = MyApplication(registry=self.my_registry)
        # create a user defined mixin
        env1 = self.env.copy()
        env1['username'] = 'foo'
        env1['PATH_INFO'] = '/-/'
        env1['REQUEST_METHOD'] = 'POST'
        env1['CONTENT_TYPE'] = 'text/occi'
        env1['HTTP_CATEGORY'] = occi_parser.get_category_str(Mixin('foo#',
                                                                   'bar'),
                                                             app.registry)
        app(env1, Response())

        # create a second user defined mixin
        env2 = self.env.copy()
        env2['username'] = 'foo'
        env2['PATH_INFO'] = '/-/'
        env2['REQUEST_METHOD'] = 'POST'
        env2['CONTENT_TYPE'] = 'text/occi'
        env2['HTTP_CATEGORY'] = occi_parser.get_category_str(Mixin('foo#',
                                                                   'bar'),
                                                             app.registry)
        self.assertRaises(AttributeError, app, env2, Response())

    #==========================================================================
    # Test for sanity
    #==========================================================================

    def test_get_resource_for_sanity(self):
        '''
        Check that only resource belong to a user are shown.
        '''
        app = MyApplication(registry=self.my_registry)
        # create one vm for user foo1
        env1 = self.env.copy()
        env1['username'] = 'foo'
        env1['REQUEST_METHOD'] = 'POST'
        env1['CONTENT_TYPE'] = 'text/occi'
        env1['HTTP_CATEGORY'] = occi_parser.get_category_str(COMPUTE,
                                                             app.registry)
        app(env1, Response())

        env2 = env1.copy()
        env2['username'] = 'bar'
        app(env2, Response())

    def test_get_resources_for_sanity(self):
        '''
        Check that only resource belong to a user are shown.
        '''
        app = MyApplication(registry=self.my_registry)
        # create one vm for user foo1
        env1 = self.env.copy()
        env1['username'] = 'foo'
        env1['REQUEST_METHOD'] = 'POST'
        env1['CONTENT_TYPE'] = 'text/occi'
        env1['HTTP_CATEGORY'] = occi_parser.get_category_str(COMPUTE,
                                                             app.registry)
        app(env1, Response())

        # create one vm for user foo2
        env2 = env1.copy()
        env2['username'] = 'bar'
        app(env2, Response())

        # check that they can't list and see each others VMs
        self.assertTrue(len(app.registry.get_resource_keys({'sec':
                                                         {'id': 'foo'}})) == 2)
        self.assertTrue(len(app.registry.get_resource_keys({'sec':
                                                         {'id': 'bar'}})) == 2)
        self.assertTrue(len(app.registry.resources) == 3)

        env1_list = self.env.copy()
        env1_list['username'] = 'foo'
        id1 = app(env1_list, Response())[0]. strip().split('\n')
        self.assertTrue(len(app(env1_list,
                                Response())[0].strip().split('\n')) == 2)

        env2_list = self.env.copy()
        env2_list['username'] = 'bar'
        id2 = app(env2_list, Response())[0]. strip().split('\n')
        self.assertTrue(len(app(env2_list,
                                Response())[0].strip().split('\n')) == 2)

        self.assertTrue(id1 != id2)

    def test_get_query_interface_for_sanity(self):
        '''
        Check that only categories belong to a user are shown.
        '''
        app = MyApplication(registry=self.my_registry)
        # create a user defined mixin
        env1 = self.env.copy()
        env1['username'] = 'foo'
        env1['PATH_INFO'] = '/-/'
        env1['REQUEST_METHOD'] = 'POST'
        env1['CONTENT_TYPE'] = 'text/occi'
        env1['HTTP_CATEGORY'] = occi_parser.get_category_str(Mixin('foo',
                                                                   'bar',
                                                        location='/bar/'),
                                                             app.registry)
        app(env1, Response())

        # check that they can't list and see each others categories
        self.assertTrue(len(app.registry.get_categories(None)) == 1)
        self.assertTrue(len(app.registry.get_categories({'sec':
                                                         {'id': 'foo'}}))
                        == 2)

        env2 = env1.copy()
        env2['REQUEST_METHOD'] = 'DELETE'
        app(env2, Response())


class MyBackend(KindBackend):
    '''
    Dummy impl...
    '''

    def create(self, entity, extra_values):
        '''
        Set owner so registry has sth to compare :-)
        '''
        entity.extras = extra_values['sec']['id']

    def retrieve(self, entity, extras):
        '''
        checks locally - but you could also check in your app...
        '''
        if entity.extras != extras['id']:
            raise HTTPError(401, 'Forbidden')


class Response(object):
    '''
    Dummy mocking object.
    '''

    def __init__(self):
        pass

    def __call__(self, one, two):
        if one == '400 Bad Request':
            raise AttributeError(one + str(two))
