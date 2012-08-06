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
Module to the web request handlers. Follows the HTTP rendering spec.

Created on Jul 4, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Unused variable' pylint check (sometime I only look in the body)
# disabling 'Method could be func' pylint check (naw...)
# pylint: disable=C0103,R0904,W0612,R0201

from occi.backend import KindBackend, MixinBackend, ActionBackend
from occi.core_model import Resource, Link, Mixin
from occi.exceptions import HTTPError
from occi.extensions.infrastructure import COMPUTE, STORAGE, NETWORK, \
    NETWORKINTERFACE, IPNETWORKINTERFACE, IPNETWORK, START
from occi.handlers import QueryHandler, CollectionHandler, \
    ResourceHandler, ACCEPT, CATEGORY, LOCATION, ATTRIBUTE, LINK, CONTENT_TYPE
from occi.protocol.occi_rendering import TextOcciRendering, \
    TextUriListRendering, TextPlainRendering
from occi.registry import NonePersistentRegistry
import occi.protocol.occi_parser as parser
import unittest


class TestBaseHandler(unittest.TestCase):
    '''
    Test the BaseHandler.
    '''

    def test_handle_for_success(self):
        '''
        Tests if the handle method does what it need to do.
        '''
        ResourceHandler(None, None, None, None).handle('GET', '')

    def test_handle_for_failure(self):
        '''
        Tests if the handle method throws error on failure.
        '''
        handler = ResourceHandler(None, None, None, None)
        status, header, body = handler.handle('GET', '')
        self.assertEquals(status, 405)


class TestQueryCapabilites(unittest.TestCase):
    '''
    Test the QI.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))

        backend = KindBackend()

        self.registry.set_backend(COMPUTE, backend, None)
        self.registry.set_backend(STORAGE, backend, None)
        self.registry.set_backend(NETWORK, backend, None)

    def tearDown(self):
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_retrieval_for_failure(self):
        '''
        Tests failure handling on retrieval...
        '''
        # faulty accept header
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'sldkfj'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.get)

    def test_add_mixin_for_failure(self):
        '''
        Test failure handling off adding mixins.
        '''
        # missing locaction -> reject
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo; scheme="http://example.com#"'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.post)

        # existing location -> reject
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo; scheme = "http://example.com#";'
                             ' location = "/compute/"'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.post)

        # faulty location -> reject
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo; scheme = "http://example.com#";'
                             ' location = "/sdf"'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.post)

        # already existing...
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'compute; scheme = "http://schemas.ogf.org'
                             '/occi/infrastructure#";'
                             ' location = "/bla/"'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.post)

    def test_remove_mixin_for_failure(self):
        '''
        Test failure handling off removing mixins.
        '''
        # missing locaction -> reject
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo; scheme="http://example.com#"'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.delete)

        # not available
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo2; scheme="http://example.com#";'
                             ' location="/foo/"'}
        handler = QueryHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.delete)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_retrieval_for_sanity(self):
        '''
        Test HTTP GET on QI.
        '''
        # tests if all 3 kinds can be retrieved.
        headers = {ACCEPT: 'text/occi', }
        handler = QueryHandler(self.registry, headers, '', [])
        status, headers, body = handler.get()
        self.assertTrue(len(headers['Category'].split(',')) == 3)

        # test the filtering...
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = QueryHandler(self.registry, headers, '', [])
        status, headers, body = handler.get()
        self.assertTrue(len(headers['Category'].split(',')) == 1)

    def test_mixin_for_sanity(self):
        '''
        Test if a user defined mixin can be added.
        '''
        # add a mixin.
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo; scheme="http://example.com#";'
                             ' location="/foo/"'}
        handler = QueryHandler(self.registry, headers, '', [])
        status, headers, body = handler.post()
        self.assertTrue(body == 'OK')

        # remove the mixin.
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foo; scheme="http://example.com#";'
                             ' location="/foo/"'}
        handler = QueryHandler(self.registry, headers, '', [])
        status, headers, body = handler.delete()
        self.assertTrue(body == 'OK')


class TestCollectionCapabilites(unittest.TestCase):
    '''
    Test the collection handler.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.set_hostname('http://127.0.0.1')

        self.registry.set_renderer('text/plain',
                                   TextPlainRendering(self.registry))
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))
        self.registry.set_renderer('text/uri-list',
                                   TextUriListRendering(self.registry))

        self.mixin = Mixin('foo', 'mystuff')

        self.compute = Resource('/compute/1', COMPUTE, [])
        self.compute.attributes = {'foo2': 'bar2'}
        self.network = Resource('/network/1', NETWORK, [IPNETWORK])
        self.network_interface = Link('/network/interface/1', NETWORKINTERFACE,
                                      [IPNETWORKINTERFACE], self.compute,
                                      self.network)

        self.registry.set_backend(COMPUTE, SimpleComputeBackend(), None)
        self.registry.set_backend(NETWORK, KindBackend(), None)
        self.registry.set_backend(self.mixin, MixinBackend(), None)
        self.registry.set_backend(START, SimpleComputeBackend(), None)

        self.registry.add_resource(self.compute.identifier, self.compute, None)
        self.registry.add_resource(self.network.identifier, self.network, None)
        self.registry.add_resource(self.network_interface.identifier,
                                   self.network_interface, None)

    def tearDown(self):
        for item in self.registry.get_resources(None):
            self.registry.delete_resource(item.identifier, None)
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_retrieve_for_failure(self):
        '''
        Do a get with garbeage as filter...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'asdf'}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.get, '')

    def test_action_for_failure(self):
        '''
        Tests if actions can be triggered with garbage as content
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'foobar'}
        handler = CollectionHandler(self.registry, headers, '',
                                    ['action', 'start'])
        self.assertRaises(HTTPError, handler.post, '')

    def test_update_mixin_collection_for_failure(self):
        '''
        Add mixins to resources.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.compute.identifier}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.post, '/bla')

    def test_remove_entities_from_collection_for_failure(self):
        '''
        Add mixins to resources.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.compute.identifier}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.delete, '/bla/')

        headers = {CONTENT_TYPE: 'text/xml',
                   LOCATION: self.compute.identifier}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.delete, '/bla/')

    def test_replace_mixin_collection_for_failure(self):
        '''
        Add mixins to resources.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.network.identifier}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.put, '/bla')

    def test_create_entity_for_failure(self):
        '''
        Simple test - more complex one in TestResourceHandler...
        '''
        headers = {CONTENT_TYPE: 'text/xml',
                   'Categories': parser.get_category_str(COMPUTE,
                                                         self.registry)}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.post, '/compute')

        headers = {CONTENT_TYPE: 'text/occi',
                   'Categories': parser.get_category_str(COMPUTE,
                                                         self.registry)}
        handler = CollectionHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.post, '/compute')

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_retrieve_state_of_ns_for_sanity(self):
        '''
        Test GET with uri-list
        '''
        headers = {ACCEPT: 'text/uri-list'}
        handler = CollectionHandler(self.registry, headers, '', ())
        status, headers, body = handler.get('/')
        self.assertTrue(headers[CONTENT_TYPE] == 'text/uri-list')
        self.assertTrue(len(body) == 98)

    def test_retrieve_for_sanity(self):
        '''
        Test GET with uri-list
        '''
        headers = {ACCEPT: 'text/occi'}
        handler = CollectionHandler(self.registry, headers, '', ())
        status, headers, body = handler.get('/compute/')
        self.assertTrue(headers[CONTENT_TYPE] == 'text/occi')
        self.assertTrue(self.compute.identifier in headers['X-OCCI-Location'])

        # filter on category
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(self.compute.kind,
                                                     self.registry)}

        handler = CollectionHandler(self.registry, headers, '', [])
        status, headers, body = handler.get('/')
        self.assertTrue(headers[CONTENT_TYPE] == 'text/occi')
        self.assertTrue(self.compute.identifier in headers['X-OCCI-Location'])
        self.assertFalse(self.network.identifier in headers['X-OCCI-Location'])

        # filter on attr...
        headers = {ACCEPT: 'text/occi',
                   CONTENT_TYPE: 'text/occi',
                   ATTRIBUTE: 'foo2="bar2"'}

        handler = CollectionHandler(self.registry, headers, '', [])
        status, headers, body = handler.get('/')
        self.assertTrue(headers[CONTENT_TYPE] == 'text/occi')
        self.assertTrue(self.compute.identifier in headers['X-OCCI-Location'])
        self.assertFalse(self.network.identifier in headers['X-OCCI-Location'])

    def test_delete_for_sanity(self):
        '''
        Tests if complete resource collection can be removed.
        '''
        handler = CollectionHandler(self.registry, {}, '', [])
        handler.delete('/compute')
        self.assertFalse(self.compute in self.registry.get_resources(None))

    def test_action_for_sanity(self):
        '''
        Tests if actions can be triggered on a resource set.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(START, self.registry)}

        handler = CollectionHandler(self.registry, headers, '',
                                    ['action', 'start'])
        handler.post('/compute/')
        self.assertTrue(self.compute.attributes['occi.compute.state']
                        == 'active')

    def test_update_mixin_collection_for_sanity(self):
        '''
        Add mixins to resources.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.compute.identifier}

        handler = CollectionHandler(self.registry, headers, '', ())
        handler.post('/mystuff/')
        self.assertTrue(self.mixin in self.compute.mixins)

    def test_remove_entities_from_collection_for_sanity(self):
        '''
        Add mixins to resources.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.compute.identifier}

        handler = CollectionHandler(self.registry, headers, '', ())
        handler.post('/mystuff/')

        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.compute.identifier}

        handler = CollectionHandler(self.registry, headers, '', ())
        handler.delete('/mystuff/')
        self.assertTrue(self.mixin not in self.compute.mixins)

    def test_replace_mixin_collection_for_sanity(self):
        '''
        Add mixins to resources.
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.compute.identifier}

        handler = CollectionHandler(self.registry, headers, '', ())
        handler.post('/mystuff/')

        headers = {CONTENT_TYPE: 'text/occi',
                   LOCATION: self.network.identifier}

        handler = CollectionHandler(self.registry, headers, '', ())
        handler.put('/mystuff/')
        self.assertTrue(self.mixin not in self.compute.mixins)
        self.assertTrue(self.mixin in self.network.mixins)

    def test_create_entity_for_sanity(self):
        '''
        Simple test - more complex one in TestResourceHandler...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = CollectionHandler(self.registry, headers, '', ())
        handler.post('/compute/')
        self.assertTrue(len(self.registry.get_resources(None)) == 4)


class TestResourceCapabilites(unittest.TestCase):
    '''
    Test the Resource Handler.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))
        self.registry.set_renderer('text/plain',
                                   TextPlainRendering(self.registry))

        self.registry.set_backend(COMPUTE, SimpleComputeBackend(), None)
        self.registry.set_backend(NETWORK, KindBackend(), None)
        self.registry.set_backend(NETWORKINTERFACE, KindBackend(), None)
        self.registry.set_backend(START, SimpleComputeBackend(), None)

    def tearDown(self):
        for item in self.registry.get_resources(None):
            self.registry.delete_resource(item.identifier, None)
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_create_resource_for_failure(self):
        '''
        Put two resource and one link...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'garbage'}
        handler = ResourceHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.put, '/compute/1')

    def test_retrieve_resource_for_failure(self):
        '''
        test retrieval...
        '''
        headers = {LOCATION: 'text/occi'}
        handler = ResourceHandler(self.registry, headers, '', [])
        self.assertRaises(HTTPError, handler.get, '/bla')

    def test_partial_update_for_failure(self):
        '''
        test update...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   ATTRIBUTE: 'occi.compute.cores="2"'}
        handler = ResourceHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.post, '/bla')

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   ATTRIBUTE: 'garbage'}
        handler = ResourceHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.post, '/compute/1')

    def test_replace_for_failure(self):
        '''
        test update...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry),
                   ATTRIBUTE: 'occi.compute.memory="2.0"'}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'garbage'}
        handler = ResourceHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.put, '/compute/1')

    def test_delete_for_failure(self):
        '''
        Test delete...
        '''
        handler = ResourceHandler(self.registry, {}, '', ())
        self.assertRaises(HTTPError, handler.delete, '/compute/2')

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry),
                   ATTRIBUTE: 'undeletable="true"'}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        handler = ResourceHandler(self.registry, headers, '', ())
        self.assertRaises(HTTPError, handler.delete, '/compute/1')

    def test_trigger_action_for_failure(self):
        '''
        Trigger an action...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/3')
        self.assertTrue('/compute/3' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: 'blabla'}
        handler = ResourceHandler(self.registry, headers, '',
                                  ['action', 'start'])
        self.assertRaises(HTTPError, handler.post, '/compute/3')

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(START, self.registry)}
        handler = ResourceHandler(self.registry, headers, '',
                                  ['action', 'start'])
        self.assertRaises(HTTPError, handler.post, '/bla"')

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_create_resource_for_sanity(self):
        '''
        Put two resource and one link...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', [])
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(NETWORK, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', [])
        handler.put('/network/1')
        self.assertTrue('/network/1' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(NETWORKINTERFACE,
                                                     self.registry),
                   ATTRIBUTE: 'occi.core.source="/compute/1",'
                              ' occi.core.target="/network/1"'}
        handler = ResourceHandler(self.registry, headers, '', [])
        status, headers, body = handler.put('/network/link/1')
        self.assertTrue('/network/link/1' in
                        self.registry.get_resource_keys(None))
        compute = self.registry.get_resource('/compute/1', None)
        self.assertTrue(len(compute.links) == 1)
        self.assertTrue('/network/link/1' in headers['Location'])

    def test_retrieve_resource_for_sanity(self):
        '''
        test retrieval...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', [])
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        headers = {ACCEPT: 'text/occi'}
        handler = ResourceHandler(self.registry, headers, '', [])
        status, headers, body = handler.get('/compute/1')
        self.assertTrue('"/compute/1"' in headers['X-OCCI-Attribute'])
        self.assertTrue('compute' in headers['Category'])
        self.assertTrue('text/occi' in headers[CONTENT_TYPE])

    def test_partial_update_for_sanity(self):
        '''
        test update...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   ATTRIBUTE: 'occi.compute.cores="2"'}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.post('/compute/1')
        compute = self.registry.get_resource('/compute/1', None)
        self.assertTrue('occi.compute.cores' in compute.attributes.keys())

    def test_replace_for_sanity(self):
        '''
        test update...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry),
                   ATTRIBUTE: 'occi.compute.memory="2.0"'}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry),
                   ATTRIBUTE: 'occi.compute.cores="2"'}
        handler = ResourceHandler(self.registry, headers, '', ())
        handler.put('/compute/1')

        compute = self.registry.get_resource('/compute/1', None)
        self.assertTrue('occi.compute.memory' not in compute.attributes.keys())
        self.assertTrue('occi.compute.cores' in compute.attributes.keys())

    def test_delete_for_sanity(self):
        '''
        Test delete...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry),
                   ATTRIBUTE: 'occi.compute.memory="2.0"'}
        handler = ResourceHandler(self.registry, headers, '', [])
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys(None))

        handler = ResourceHandler(self.registry, headers, '', [])
        handler.delete('/compute/1')
        self.assertTrue('/compute/1' not in
                        self.registry.get_resource_keys(None))

    def test_trigger_action_for_sanity(self):
        '''
        Trigger an action...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry)}
        handler = ResourceHandler(self.registry, headers, '', [])
        handler.put('/compute/3')
        self.assertTrue('/compute/3' in self.registry.get_resource_keys(None))

        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(START, self.registry)}

        handler = ResourceHandler(self.registry, headers, '',
                                  ['action', 'start'])
        handler.post('/compute/3')

        compute = self.registry.get_resource('/compute/3', None)
        self.assertTrue(compute.attributes['occi.compute.state']
                        == 'active')


class TestLinkHandling(unittest.TestCase):
    '''
    Tests links and do request in body for a change :-)
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.set_renderer('text/plain',
                                   TextPlainRendering(self.registry))
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))

        self.registry.set_backend(COMPUTE, SimpleComputeBackend(), None)
        self.registry.set_backend(NETWORK, KindBackend(), None)
        self.registry.set_backend(NETWORKINTERFACE, KindBackend(), None)
        self.registry.set_backend(START, SimpleComputeBackend(), None)

        self.compute = Resource('/compute/1', COMPUTE, [])
        self.network = Resource('/network/1', NETWORK, [IPNETWORK])

        self.registry.add_resource('/compute/1', self.compute, None)
        self.registry.add_resource('/network/1', self.network, None)

    def tearDown(self):
        for item in self.registry.get_resources(None):
            self.registry.delete_resource(item.identifier, None)
        for item in self.registry.get_categories(None):
            self.registry.delete_mixin(item, None)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_inline_creation_for_sanity(self):
        '''
        Test creation of compute with a link to network (inline)...
        '''
        headers = {CONTENT_TYPE: 'text/occi',
                   CATEGORY: parser.get_category_str(COMPUTE, self.registry),
                   LINK: '</network/1>;'
                         'rel="http://schemas.ogf.org/occi/infrastructure#'
                         'network";'
                         'category=\
                                 "http://schemas.ogf.org/occi/infrastructure#'
                         'networkinterface";'
                         'occi.networkinterface.interface="eth0";'
                         'occi.networkinterface.mac="00:11:22:33:44:55";'}
        handler = ResourceHandler(self.registry, headers, '', [])
        handler.put('/compute/2')
        self.assertTrue('/compute/2' in self.registry.get_resource_keys(None))
        self.assertTrue(len(self.registry.get_resources(None)) == 4)

        compute = self.registry.get_resource('/compute/2', None)
        self.assertTrue(len(compute.links) == 1)

        handler = ResourceHandler(self.registry, headers, '', [])
        status, headers, body = handler.get('/compute/2')
        self.assertTrue('Link: ' in body)
        self.assertTrue('self=' in body)

    def test_link_creation_for_sanity(self):
        '''
        Test creation for sanity...
        '''
        headers = {CONTENT_TYPE: 'text/plain'}
        body = 'Category: ' + parser.get_category_str(NETWORKINTERFACE,
                                                      self.registry) + '\n'
        body += 'X-OCCI-Attribute: occi.core.source="/compute/1"\n'
        body += 'X-OCCI-Attribute: occi.core.target="/network/1"'

        handler = ResourceHandler(self.registry, headers, body, [])
        handler.put('/link/2')
        self.assertTrue('/link/2' in self.registry.get_resource_keys(None))

        link = self.registry.get_resource('/link/2', None)
        self.assertTrue(link in link.source.links)

        handler = ResourceHandler(self.registry, headers, '', [])
        status, headers, body = handler.get('/link/2')
        self.assertTrue('occi.core.target' in body)
        self.assertTrue('occi.core.source' in body)


class SimpleComputeBackend(KindBackend, ActionBackend):
    '''
    Simple backend...handing the kinds and Actions!
    '''

    def create(self, entity, extras):
        entity.attributes['occi.compute.state'] = 'inactive'

    def update(self, old, new, extras):
        for attr in new.attributes.keys():
            old.attributes[attr] = new.attributes[attr]

    def replace(self, old, new, extras):
        old.attributes = new.attributes
        del new

    def delete(self, entity, extras):
        if 'undeletable' in entity.attributes:
            raise AttributeError("I cannot be delete...")

    def action(self, entity, action, attributes, extras):
        entity.attributes['occi.compute.state'] = 'active'
