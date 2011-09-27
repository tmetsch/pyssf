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
Module to the web request handlers. Follows the HTTP rendering spec.

Created on Jul 4, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# disabling 'Unused variable' pylint check (sometime I only look in the body)
# pylint: disable=C0103,R0904,W0612

from occi.backend import KindBackend, MixinBackend, ActionBackend
from occi.core_model import Resource, Link, Mixin
from occi.extensions.infrastructure import COMPUTE, STORAGE, NETWORK, \
    NETWORKINTERFACE, IPNETWORKINTERFACE, IPNETWORK, START
from occi.protocol.occi_rendering import TextOcciRendering, \
    TextUriListRendering, TextPlainRendering
from occi.registry import NonePersistentRegistry
from occi.web import QueryHandler, BaseHandler, CollectionHandler, \
    ResourceHandler
from tornado.httpserver import HTTPRequest
from tornado.web import Application, HTTPError
import occi.protocol.occi_parser as parser
import unittest
import urlparse


class Request(HTTPRequest):
    '''
    Wraps around an HTTP request from Tornado.
    '''

    def write(self, data):
        pass

    def finish(self):
        pass


class TestMixin(BaseHandler):
    '''
    Mixin which overwrites some functions.
    '''

    # disabling 'Arguments number differs' pylint check (Needed here...)
    # pylint: disable=W0221

    heads = {}
    body = ''

    def __init__(self, application, request, **kwargs):
        super(TestMixin, self).__init__(application, request, **kwargs)
        self._transforms = []
        self.request.remote_ip = '10.0.0.1'

    def initialize(self):
        pass

    def response(self, status, mime_type, headers, body='OK'):
        super(TestMixin, self).response(status, mime_type, headers, body)
        self.heads = self._headers
        self.body = body

    def get_output(self):
        '''
        Retrieve the output from an operation.
        '''
        heads, data = self.heads, self.body
        self.body = ''
        self.heads = {}
        return heads, data


class QueryWrapper(QueryHandler, TestMixin):
    '''
    Adds the Mixin to the QueryHandler.
    '''
    pass


class TestQueryCapabilites(unittest.TestCase):
    '''
    Test the QI.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.app = Application([(r"/-/", QueryWrapper)])
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))

        backend = KindBackend()

        self.registry.set_backend(COMPUTE, backend)
        self.registry.set_backend(STORAGE, backend)
        self.registry.set_backend(NETWORK, backend)

    def tearDown(self):
        for item in self.registry.get_categories():
            self.registry.delete_mixin(item)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_retrieval_for_failure(self):
        '''
        Tests failure handling on retrieval...
        '''
        # faulty accept header
        headers = {'Content-Type': 'text/occi',
                   'Category': 'sldkfj'}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.get)

    def test_add_mixin_for_failure(self):
        '''
        Test failure handling off adding mixins.
        '''
        # missing locaction -> reject
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo; scheme="http://example.com#"'}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post)

        # existing location -> reject
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo; scheme="http://example.com#";' \
                   ' location="/compute/"'}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post)

        # faulty location -> reject
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo; scheme="http://example.com#";' \
                   ' location="/sdf"'}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post)

        # already existing...
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'compute; scheme="http://schemas.ogf.org' \
                   '/occi/infrastructure#";' \
                   ' location="/bla/"'}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post)

    def test_remove_mixin_for_failure(self):
        '''
        Test failure handling off removing mixins.
        '''
        # missing locaction -> reject
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo; scheme="http://example.com#"'}
        request = create_request('DELETE', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.delete)

        # not available
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo2; scheme="http://example.com#";' \
                   ' location="/foo/"'}
        request = create_request('DELETE', headers, '')
        handler = QueryWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.delete)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_retrieval_for_sanity(self):
        '''
        Test HTTP GET on QI.
        '''
        # tests if all 3 kinds can be retrieved.
        headers = {'Accept': 'text/occi'}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        handler.get()
        headers, body = handler.get_output()
        self.assertTrue(len(headers['Category'].split(',')) == 3)

        # test the filtering...
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('GET', headers, '')
        handler = QueryWrapper(self.app, request)
        handler.get()
        headers, body = handler.get_output()
        self.assertTrue(len(headers['Category'].split(',')) == 1)

    def test_mixin_for_sanity(self):
        '''
        Test if a user defined mixin can be added.
        '''
        # add a mixin.
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo; scheme="http://example.com#";' \
                   ' location="/foo/"'}
        request = create_request('POST', headers, '')
        handler = QueryWrapper(self.app, request)
        handler.post()
        headers, body = handler.get_output()
        self.assertTrue(body == 'OK')

        # remove the mixin.
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': 'foo; scheme="http://example.com#";' \
                   ' location="/foo/"'}
        request = create_request('DELETE', headers, '')
        handler = QueryWrapper(self.app, request)
        handler.delete()
        headers, body = handler.get_output()
        self.assertTrue(body == 'OK')


class CollectionWrapper(CollectionHandler, TestMixin):
    '''
    Adds the Mixin to the CollectionHandler.
    '''
    pass


class TestCollectionCapabilites(unittest.TestCase):
    '''
    Test the collection handler.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.registry.set_hostname('http://127.0.0.1')
        self.app = Application([(r"(.*)/", CollectionWrapper)])

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

        self.registry.set_backend(COMPUTE, SimpleComputeBackend())
        self.registry.set_backend(NETWORK, KindBackend())
        self.registry.set_backend(self.mixin, MixinBackend())
        self.registry.set_backend(START, SimpleComputeBackend())

        self.registry.add_resource(self.compute.identifier, self.compute)
        self.registry.add_resource(self.network.identifier, self.network)
        self.registry.add_resource(self.network_interface.identifier,
                                   self.network_interface)

    def tearDown(self):
        for item in self.registry.get_resources():
            self.registry.delete_resource(item.identifier)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_retrieve_for_failure(self):
        '''
        Do a get with garbeage as filter...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': 'asdf'}
        request = create_request('GET', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.get, '')

    def test_action_for_failure(self):
        '''
        Tests if actions can be triggered with garbage as content
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': 'foobar'}
        request = create_request('POST', headers, '', '/compute/?action=start')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '')

    def test_update_mixin_collection_for_failure(self):
        '''
        Add mixins to resources.
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/bla')

    def test_remove_entities_from_collection_for_failure(self):
        '''
        Add mixins to resources.
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('DELETE', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.delete, '/bla/')

        headers = {'Content-Type': 'text/xml',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('DELETE', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.delete, '/bla/')

    def test_replace_mixin_collection_for_failure(self):
        '''
        Add mixins to resources.
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.network.identifier}
        request = create_request('PUT', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.put, '/bla')

    def test_create_entity_for_failure(self):
        '''
        Simple test - more complex one in TestResourceHandler...
        '''
        headers = {'Content-Type': 'text/xml',
                   'Categories': parser.get_category_str(COMPUTE)}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/compute')

        headers = {'Content-Type': 'text/occi',
                   'Categories': parser.get_category_str(COMPUTE)}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/compute')

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_retrieve_state_of_ns_for_sanity(self):
        '''
        Test GET with uri-list
        '''
        headers = {'Accept': 'text/uri-list'}
        request = create_request('GET', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.get('')
        headers, body = handler.get_output()
        self.assertTrue(headers['Content-Type'] == 'text/uri-list')
        self.assertTrue(len(body) == 98)

    def test_retrieve_for_sanity(self):
        '''
        Test GET with uri-list
        '''
        headers = {'Accept': 'text/occi'}
        request = create_request('GET', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.get('/compute/')
        headers, body = handler.get_output()
        self.assertTrue(headers['Content-Type'] == 'text/occi')
        self.assertTrue(self.compute.identifier in headers['X-OCCI-Location'])

        # filter on category
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(self.compute.kind)}
        request = create_request('GET', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.get('/')
        headers, body = handler.get_output()
        self.assertTrue(headers['Content-Type'] == 'text/occi')
        self.assertTrue(self.compute.identifier in headers['X-OCCI-Location'])
        self.assertFalse(self.network.identifier in headers['X-OCCI-Location'])

        # filter on attr...
        headers = {'Accept': 'text/occi',
                   'Content-Type': 'text/occi',
                   'X-Occi-Attribute': 'foo2="bar2"'}
        request = create_request('GET', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.get('/')
        headers, body = handler.get_output()
        self.assertTrue(headers['Content-Type'] == 'text/occi')
        self.assertTrue(self.compute.identifier in headers['X-OCCI-Location'])
        self.assertFalse(self.network.identifier in headers['X-OCCI-Location'])

    def test_delete_for_sanity(self):
        '''
        Tests if complete resource collection can be removed.
        '''
        request = create_request('DELETE', {}, '')
        handler = CollectionWrapper(self.app, request)
        handler.delete('/compute')
        self.assertFalse(self.compute in self.registry.get_resources())

    def test_action_for_sanity(self):
        '''
        Tests if actions can be triggered on a resource set.
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(START)}
        request = create_request('POST', headers, '', '/compute/?action=start')
        handler = CollectionWrapper(self.app, request)
        handler.post('/compute/')
        self.assertTrue(self.compute.attributes['occi.compute.state']
                        == 'active')

    def test_update_mixin_collection_for_sanity(self):
        '''
        Add mixins to resources.
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.post('/mystuff/')
        self.assertTrue(self.mixin in self.compute.mixins)

    def test_remove_entities_from_collection_for_sanity(self):
        '''
        Add mixins to resources.
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.post('/mystuff/')

        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('DELETE', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.delete('/mystuff/')
        self.assertTrue(self.mixin not in self.compute.mixins)

    def test_replace_mixin_collection_for_sanity(self):
        '''
        Add mixins to resources.
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.compute.identifier}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.post('/mystuff/')

        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Location': self.network.identifier}
        request = create_request('PUT', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.put('/mystuff/')
        self.assertTrue(self.mixin not in self.compute.mixins)
        self.assertTrue(self.mixin in self.network.mixins)

    def test_create_entity_for_sanity(self):
        '''
        Simple test - more complex one in TestResourceHandler...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('POST', headers, '')
        handler = CollectionWrapper(self.app, request)
        handler.post('/compute/')
        self.assertTrue(len(self.registry.get_resources()) == 4)


class ResourceWrapper(ResourceHandler, TestMixin):
    '''
    Adds the Mixin to the ResourceHandler.
    '''
    pass


class TestResourceCapabilites(unittest.TestCase):
    '''
    Test the Resource Handler.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.app = Application([(r"(.*)", ResourceWrapper)])
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))

        self.registry.set_backend(COMPUTE, SimpleComputeBackend())
        self.registry.set_backend(NETWORK, KindBackend())
        self.registry.set_backend(NETWORKINTERFACE, KindBackend())
        self.registry.set_backend(START, SimpleComputeBackend())

    def tearDown(self):
        for item in self.registry.get_resources():
            self.registry.delete_resource(item.identifier)

    #==========================================================================
    # Failure
    #==========================================================================

    def test_create_resource_for_failure(self):
        '''
        Put two resource and one link...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': 'garbage'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.put, '/compute/1')

    def test_retrieve_resource_for_failure(self):
        '''
        test retrieval...
        '''
        headers = {'Accept': 'text/occi'}
        request = create_request('GET', headers, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.get, '/bla')

    def test_partial_update_for_failure(self):
        '''
        test update...
        '''
        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Attribute': 'occi.compute.cores="2"'}
        request = create_request('POST', headers, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/bla')

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Attribute': 'garbage'}
        request = create_request('POST', headers, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/compute/1')

    def test_replace_for_failure(self):
        '''
        test update...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE),
                   'X-Occi-Attribute': 'occi.compute.memory="2.0"'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'Category': 'garbage'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.put, '/compute/1')

    def test_delete_for_failure(self):
        '''
        Test delete...
        '''
        request = create_request('DELETE', {}, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.delete, '/compute/2')

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE),
                   'X-Occi-Attribute': 'undeletable="true"'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        request = create_request('DELETE', {}, '')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.delete, '/compute/1')

    def test_trigger_action_for_failure(self):
        '''
        Trigger an action...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/3')
        self.assertTrue('/compute/3' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'Category': 'blabla'}
        request = create_request('POST', headers, '', '/compute/3?action=' \
                                 'start')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/compute/3')

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(START)}
        request = create_request('POST', headers, '', '/compute/3?action=' \
                                 'start')
        handler = ResourceWrapper(self.app, request)
        self.assertRaises(HTTPError, handler.post, '/bla"')

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_create_resource_for_sanity(self):
        '''
        Put two resource and one link...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(NETWORK)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/network/1')
        self.assertTrue('/network/1' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(NETWORKINTERFACE),
                   'X-Occi-Attribute': 'occi.core.source="/compute/1",' \
                                       ' occi.core.target="/network/1"'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/network/link/1')
        self.assertTrue('/network/link/1' in self.registry.get_resource_keys())
        compute = self.registry.get_resource('/compute/1')
        self.assertTrue(len(compute.links) == 1)
        heads, body = handler.get_output()
        self.assertTrue('/network/link/1' in heads['Location'])

    def test_retrieve_resource_for_sanity(self):
        '''
        test retrieval...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        headers = {'Accept': 'text/occi'}
        request = create_request('GET', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.get('/compute/1')
        heads, body = handler.get_output()
        self.assertTrue('"/compute/1"' in heads['X-OCCI-Attribute'])
        self.assertTrue('compute' in heads['Category'])
        self.assertTrue('text/occi' in heads['Content-Type'])

    def test_partial_update_for_sanity(self):
        '''
        test update...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'X-Occi-Attribute': 'occi.compute.cores="2"'}
        request = create_request('POST', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.post('/compute/1')

        compute = self.registry.get_resource('/compute/1')
        self.assertTrue('occi.compute.cores' in compute.attributes.keys())
        heads, body = handler.get_output()

    def test_replace_for_sanity(self):
        '''
        test update...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE),
                   'X-Occi-Attribute': 'occi.compute.memory="2.0"'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE),
                   'X-Occi-Attribute': 'occi.compute.cores="2"'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')

        compute = self.registry.get_resource('/compute/1')
        self.assertTrue('occi.compute.memory' not in compute.attributes.keys())
        self.assertTrue('occi.compute.cores' in compute.attributes.keys())

        heads, body = handler.get_output()

    def test_delete_for_sanity(self):
        '''
        Test delete...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE),
                   'X-Occi-Attribute': 'occi.compute.memory="2.0"'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/1')
        self.assertTrue('/compute/1' in self.registry.get_resource_keys())

        request = create_request('DELETE', {}, '')
        handler = ResourceWrapper(self.app, request)
        handler.delete('/compute/1')
        self.assertTrue('/compute/1' not in self.registry.get_resource_keys())

    def test_trigger_action_for_sanity(self):
        '''
        Trigger an action...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE)}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/3')
        self.assertTrue('/compute/3' in self.registry.get_resource_keys())

        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(START)}
        request = create_request('POST', headers, '', '/compute/3?action' \
                                 '=start')
        handler = ResourceWrapper(self.app, request)
        handler.post('/compute/3')

        compute = self.registry.get_resource('/compute/3')
        self.assertTrue(compute.attributes['occi.compute.state']
                        == 'active')


class TestLinkHandling(unittest.TestCase):
    '''
    Tests links and do request in body for a change :-)
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.app = Application([(r"(.*)", ResourceWrapper)])
        self.registry.set_renderer('text/plain',
                                   TextPlainRendering(self.registry))
        self.registry.set_renderer('text/occi',
                                   TextOcciRendering(self.registry))

        self.registry.set_backend(COMPUTE, SimpleComputeBackend())
        self.registry.set_backend(NETWORK, KindBackend())
        self.registry.set_backend(NETWORKINTERFACE, KindBackend())
        self.registry.set_backend(START, SimpleComputeBackend())

        self.compute = Resource('/compute/1', COMPUTE, [])
        self.network = Resource('/network/1', NETWORK, [IPNETWORK])

        self.registry.add_resource('/compute/1', self.compute)
        self.registry.add_resource('/network/1', self.network)

    def tearDown(self):
        for item in self.registry.get_resources():
            self.registry.delete_resource(item.identifier)

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_inline_creation_for_sanity(self):
        '''
        Test creation of compute with a link to network (inline)...
        '''
        headers = {'Content-Type': 'text/occi',
                   'Category': parser.get_category_str(COMPUTE),
                   'Link': '</network/1>;' \
                   'rel="http://schemas.ogf.org/occi/infrastructure#' \
                   'network";' \
                   'category="http://schemas.ogf.org/occi/infrastructure#' \
                   'networkinterface";' \
                   'occi.networkinterface.interface="eth0";' \
                   'occi.networkinterface.mac="00:11:22:33:44:55";'}
        request = create_request('PUT', headers, '')
        handler = ResourceWrapper(self.app, request)
        handler.put('/compute/2')
        self.assertTrue('/compute/2' in self.registry.get_resource_keys())
        self.assertTrue(len(self.registry.get_resources()) == 4)

        compute = self.registry.get_resource('/compute/2')
        self.assertTrue(len(compute.links) == 1)

        request = create_request('GET', {}, '')
        handler = ResourceWrapper(self.app, request)
        handler.get('/compute/2')
        heads, body = handler.get_output()
        self.assertTrue('Link: ' in body)
        self.assertTrue('self=' in body)

    def test_link_creation_for_sanity(self):
        '''
        Test creation for sanity...
        '''
        headers = {'Content-Type': 'text/plain'}
        body = 'Category: ' + parser.get_category_str(NETWORKINTERFACE) + '\n'
        body += 'X-OCCI-Attribute: occi.core.source="/compute/1"\n'
        body += 'X-OCCI-Attribute: occi.core.target="/network/1"'
        request = create_request('PUT', headers, body)
        handler = ResourceWrapper(self.app, request)
        handler.put('/link/2')
        self.assertTrue('/link/2' in self.registry.get_resource_keys())

        link = self.registry.get_resource('/link/2')
        self.assertTrue(link in link.source.links)

        request = create_request('GET', {}, '')
        handler = ResourceWrapper(self.app, request)
        handler.get('/link/2')
        heads, body = handler.get_output()
        self.assertTrue('occi.core.target' in body)
        self.assertTrue('occi.core.source' in body)


class TestMisc(unittest.TestCase):
    '''
    Several other tests...
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.app = Application([(r"(.*)", ResourceWrapper)])

    def test_get_error_html_for_success(self):
        '''
        Test retrieval of Error codes...
        '''
        handler = BaseHandler(self.app, create_request('GET', {}, ''),
                              registry=self.registry)
        handler.get_error_html(200)


def create_request(verb, headers=None, body=None, uri=None):
    '''
    Creates a HTTP request object ready to be used.

    very -- Either GET, POST, PUT or DELETE.
    headers -- The HTTP headers.
    body -- The HTTP body.
    uri -- The URI to operate on.
    '''
    if headers is None:
        headers = {}
    request = Request(verb, '', headers=headers, body=body)
    if uri is not None:
        request.uri = uri
    request.__delattr__('connection')

    arguments = {}
    if uri is not None:
        tmp = urlparse.urlparse(uri)
        arguments[tmp[4].split('=')[0]] = tmp[4].split('=')[1]
    request.arguments = arguments
    return request


class SimpleComputeBackend(KindBackend, ActionBackend):
    '''
    Simple backend...handing the kinds and Actions!
    '''

    def create(self, entity):
        entity.attributes['occi.compute.state'] = 'inactive'

    def update(self, old, new):
        for attr in new.attributes.keys():
            old.attributes[attr] = new.attributes[attr]

    def replace(self, old, new):
        old.attributes = new.attributes
        del(new)

    def delete(self, entity):
        if 'undeletable' in entity.attributes:
            raise AttributeError("I cannot be delete...")

    def action(self, entity, action):
        entity.attributes['occi.compute.state'] = 'active'
