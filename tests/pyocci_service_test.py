# 
# Copyright (C) 2010 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
Created on Nov 10, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci import service
from pyocci.core import Link, Resource
from pyocci.service import ResourceHandler, BaseHandler, ListHandler, \
    QueryHandler, LinkBackend, MixinBackend
from tests import http_body, http_body_action, http_body_mixin, \
    NetworkLinkBackend
from tornado.httpserver import HTTPRequest
from tornado.web import Application, HTTPError
import unittest

def create_request(verb, headers = None, body = None, uri = None):
    if headers is None:
        headers = {}
    request = HTTPRequest(verb, '', headers = headers, body = body)
    if uri is not None:
        request.uri = uri
    request.__delattr__('connection')
    return request

class Wrapper(ResourceHandler):

    body = ''

    def get_output(self):
        heads, data = self._headers, self.body
        self.body = ''
        self._headers = {}
        return heads, data

    def write(self, chunk):
        self.body = chunk

class BaseHandlerTest(unittest.TestCase):

    application = None
    headers = {}

    def setUp(self):
        self.application = Application([(r"(.*)", BaseHandler)])
        self.headers['Content-Type'] = 'test/plain';
        self.headers['Accept'] = '';
        self.headers['Category'] = '';
        self.headers['X-Occi-Attribute'] = '';

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_extract_data_for_success(self):
        request = create_request('GET', headers = self.headers, body = '')
        handler = BaseHandler(self.application, request)
        handler.extract_http_data()
        request = create_request('GET', headers = self.headers, body = 'bla')
        BaseHandler(self.application, request)
        handler.extract_http_data()

    def test_get_error_html_for_success(self):
        request = create_request('GET')
        handler = BaseHandler(self.application, request)
        handler.get_error_html(123)
        handler.get_error_html(404, exception = HTTPError(404))

    # Leaving out all other test - those routines should throw anything!

class BasicOCCISpecificationTest(unittest.TestCase):

    application = None

    def setUp(self):
        self.application = Application([(r"(.*)", Wrapper)])

    # All test done with default */* content-type

    #===========================================================================
    # Test creation of resource instances
    #===========================================================================

    def test_create_resource_instance(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        self.assertTrue(len(heads['Location']) > 10)

        request = create_request('PUT', body = http_body)
        handler = Wrapper(self.application, request)
        handler.put('/foo/123')

        request = create_request('GET')
        handler = Wrapper(self.application, request)
        handler.get('/foo/123')
        heads, data = handler.get_output()

    def test_retrieve_resource_instance(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        url = heads['Location']

        request = create_request('GET')
        handler = Wrapper(self.application, request)
        handler.get(url)
        heads, data = handler.get_output()
        self.assertEquals(http_body, data.strip())

        request = create_request('GET')
        handler = Wrapper(self.application, request)
        handler.get('/')
        heads, data = handler.get_output()
        self.assertTrue(data.find(url) > -1)

        request = create_request('GET', headers = {'Accept':'text/occi'})
        handler = Wrapper(self.application, request)
        handler.get('/')
        heads, data = handler.get_output()
        self.assertTrue(heads['X-OCCI-Location'].find(url) > -1)

    def test_update_resource_instance(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        url = heads['Location']

        request = create_request('PUT', body = 'X-OCCI-Attribute: occi.compute.cores=3\nX-OCCI-Attribute:occi.compute.architecture=x86')
        handler = Wrapper(self.application, request)
        handler.put(url)
        heads, data = handler.get_output()

        request = create_request('GET')
        handler = Wrapper(self.application, request)
        handler.get(url)
        heads, data = handler.get_output()
        self.assertTrue(data.find('X-OCCI-Attribute: occi.compute.cores=3') > -1)

    def test_delete_resource_instance(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        url = heads['Location']

        request = create_request('DELETE')
        handler = Wrapper(self.application, request)
        handler.delete(url)
        heads, data = handler.get_output()
        self.assertRaises(HTTPError, handler.get, url)

    def test_action_resource_instance(self):
        request = create_request('PUT', body = http_body)
        handler = Wrapper(self.application, request)
        handler.put('/bar/123')

        request = create_request('POST', body = http_body_action, uri = '/bar/123?action=start')
        handler = Wrapper(self.application, request)
        handler.post('/bar/123?action=start')
        heads, data = handler.get_output()

class BasicLinkTest(unittest.TestCase):

    application = None

    def setUp(self):
        self.application = Application([(r"(.*)", Wrapper)])

        try:
            request = create_request('PUT', body = http_body)
            handler = Wrapper(self.application, request)
            handler.put('/link_test/1')

            request = create_request('PUT', body = http_body)
            handler = Wrapper(self.application, request)
            handler.put('/link_test/2')

            request = create_request('PUT', body = http_body)
            handler = Wrapper(self.application, request)
            handler.put('/link_test/3')
        except:
            pass
            # All test done with default */* content-type

    #===========================================================================
    # Test creation of links
    #===========================================================================

    def test_link_instance(self):
        link_1_2 = 'Category:' + NetworkLinkBackend.category.term + ';scheme=' + NetworkLinkBackend.category.scheme + '\nX-OCCI-Attribute:source=/link_test/1,target=/link_test/2'

        request = create_request('PUT', body = link_1_2)
        handler = Wrapper(self.application, request)
        handler.put('/my_links/12')

        request = create_request('GET', headers = {'Accept':'text/occi'})
        handler = Wrapper(self.application, request)
        handler.get('/link_test/1')
        header, data = handler.get_output()
        self.assertEqual(header['Link'], '</link_test/2>;self=/my_links/12;')

        link_2_3 = 'Category:' + NetworkLinkBackend.category.term + ';scheme=' + NetworkLinkBackend.category.scheme + '\nX-OCCI-Attribute:source=/link_test/2,target=/link_test/3'

        request = create_request('PUT', body = link_2_3)
        handler = Wrapper(self.application, request)
        handler.put('/my_links/12')

        request = create_request('GET', headers = {'Accept':'text/occi'})
        handler = Wrapper(self.application, request)
        handler.get('/link_test/2')
        header, data = handler.get_output()
        self.assertEqual(header['Link'], '</link_test/3>;self=/my_links/12;')

        link_2_1 = 'Category:' + NetworkLinkBackend.category.term + ';scheme=' + NetworkLinkBackend.category.scheme + '\nX-OCCI-Attribute:source=/link_test/2,target=/link_test/1'
        request = create_request('PUT', body = link_2_3)
        handler = Wrapper(self.application, request)
        handler.put('/my_links/21')

        request = create_request('GET', headers = {'Accept':'text/occi'})
        handler = Wrapper(self.application, request)
        handler.get('/link_test/2')
        header, data = handler.get_output()
        self.assertEqual(header['Link'], '</link_test/3>;self=/my_links/12;,</link_test/3>;self=/my_links/21;')

        request = create_request('DELETE')
        handler = Wrapper(self.application, request)
        handler.delete('/my_links/21')

        request = create_request('GET', headers = {'Accept':'text/occi'})
        handler = Wrapper(self.application, request)
        handler.get('/link_test/2')
        header, data = handler.get_output()
        self.assertEqual(header['Link'], '</link_test/3>;self=/my_links/12;')

class ErrorResourceHandlerTest(unittest.TestCase):

    application = None

    def setUp(self):
        self.application = Application([(r"(.*)", Wrapper)])

    #===========================================================================
    # POST
    #===========================================================================

    def test_post_faulty_content_type(self):
        request = create_request('POST', headers = {'Content-Type':'text/json'}, body = http_body)
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.post, '/')

    def test_post_faulty_category(self):
        request = create_request('POST', body = 'Category=bla;http://ogf.org')
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.post, '/')

    def test_post_no_backend(self):
        request = create_request('POST', body = 'Category:superduper;scheme=http://ogf.org/bla')
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.post, '/')

    def test_post_faulty_action(self):
        request = create_request('PUT', body = http_body)
        handler = Wrapper(self.application, request)
        handler.put('/bar/123')

        request = create_request('POST', body = http_body, uri = '/bar/123?action=start')
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.post, '/bar/123?action=start')

    #===========================================================================
    # PUT
    #===========================================================================

    def test_put_faulty_content_type(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        url = heads['Location']

        request = create_request('PUT', headers = {'Content-Type':'text/json'}, body = http_body)
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.put, url)

    def test_put_on_root(self):
        request = create_request('PUT', body = 'Category:superduper;scheme=http://ogf.org/bla')
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.put, '/')

    def test_put_no_backend(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        url = heads['Location']

        request = create_request('PUT', body = 'Category:superduper;scheme=http://ogf.org/bla')
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.put, url)

    #===========================================================================
    # GET
    #===========================================================================

    def test_get_faulty_accept_header(self):
        request = create_request('POST', body = http_body)
        handler = Wrapper(self.application, request)
        handler.post('/')
        heads, data = handler.get_output()
        url = heads['Location']

        request = create_request('GET', headers = {'Accept':'text/json'}, body = http_body)
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.get, url)

    def test_get_non_existing(self):
        request = create_request('GET', headers = {'Accept':'text/json'}, body = http_body)
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.get, '/foo/bar')

    #===========================================================================
    # DELETE
    #===========================================================================

    def test_delete_non_existing(self):
        request = create_request('DELETE', body = http_body)
        handler = Wrapper(self.application, request)
        self.assertRaises(HTTPError, handler.delete, '/foo/bar')

class ListWrapper(ListHandler):

    body = ''

    def get_output(self):
        heads, data = self._headers, self.body
        self.body = ''
        self._headers = {}
        return heads, data

    def write(self, chunk):
        self.body = chunk

class ListHandlerTest(unittest.TestCase):

    application = None

    def setUp(self):
        self.application = Application([(r"/-/", QueryWrapper), (r"/(.*)/", ListWrapper), (r"(.*)", Wrapper)])

        try:
            request = create_request('PUT', body = http_body_mixin)
            handler = QueryWrapper(self.application, request)
            handler.put()

            request = create_request('PUT', body = http_body)
            handler = Wrapper(self.application, request)
            handler.put('/list_test/1')

            request = create_request('PUT', body = http_body)
            handler = Wrapper(self.application, request)
            handler.put('/list_test/foo/1')

            request = create_request('PUT', body = http_body)
            handler = Wrapper(self.application, request)
            handler.put('/list_test/foo/2')
        except:
            pass

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_get_for_success(self):
#        request = create_request('GET')
#        handler = ListWrapper(self.application, request)
#        handler.get('foo/bar')

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('compute')

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('list_test')

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('list_test/foo')

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_get_for_failure(self):
        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.get, 'blubber')

    def test_put_for_failure(self):
        request = create_request('PUT', body = 'X-OCCI-Location: /list_test/1,/list_test/foo/1')
        handler = ListWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.put, 'foo')

        request = create_request('PUT', body = 'bla')
        handler = ListWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.put, 'foo/bar')

    def test_delete_for_failure(self):
        request = create_request('DELETE', body = 'X-OCCI-Location: /list_test/1,/list_test/foo/1')
        handler = ListWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.delete, 'foo')

        request = create_request('DELETE', body = '/list_test/1,/list_test/foo/1')
        handler = ListWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.delete, 'foo/bar')

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_get_for_sanity(self):
        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('compute')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/bar/123') > -1)
        self.assertTrue(data.find('/list_test/1') > -1)
        self.assertTrue(data.find('/list_test/foo/1') > -1)
        self.assertTrue(data.find('/list_test/foo/2') > -1)

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('list_test')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/1') > -1)
        self.assertTrue(data.find('/list_test/foo/1') > -1)
        self.assertTrue(data.find('/list_test/foo/2') > -1)

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('list_test/foo')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/foo/1') > -1)
        self.assertTrue(data.find('/list_test/foo/2') > -1)

    def test_get_filter_for_sanity(self):
        request = create_request('PUT', headers = {'X-Occi-Location': '/list_test/1,/list_test/foo/1', 'Content-Type':'text/occi'})
        handler = ListWrapper(self.application, request)
        handler.put('foo/bar')

        request = create_request('GET', body = http_body_mixin)
        handler = ListWrapper(self.application, request)
        handler.get('list_test')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/1') > -1)
        self.assertTrue(data.find('/list_test/foo/1') > -1)

        request = create_request('GET', body = http_body)
        handler = ListWrapper(self.application, request)
        handler.get('list_test')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/1') > -1)
        self.assertTrue(data.find('/list_test/foo/1') > -1)
        self.assertTrue(data.find('/list_test/foo/2') > -1)

        request = create_request('GET', body = 'Category: resource;scheme=http://schemas.ogf.org/occi/core')
        handler = ListWrapper(self.application, request)
        handler.get('list_test')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/1') > -1)
        self.assertTrue(data.find('/list_test/foo/1') > -1)
        self.assertTrue(data.find('/list_test/foo/2') > -1)

    def test_put_for_sanity(self):
        request = create_request('PUT', headers = {'X-Occi-Location': '/list_test/1,/list_test/foo/1', 'Content-Type':'text/occi'})
        handler = ListWrapper(self.application, request)
        handler.put('foo/bar')
        heads, data = handler.get_output()

        request = create_request('PUT', body = 'X-OCCI-Location: /list_test/1,/list_test/foo/1')
        handler = ListWrapper(self.application, request)
        handler.put('foo/bar')
        heads, data = handler.get_output()

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('foo/bar')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/1') > -1)
        self.assertTrue(data.find('/list_test/foo/1') > -1)

    def test_delete_for_sanity(self):
        request = create_request('PUT', body = 'X-OCCI-Location: /list_test/1,/list_test/foo/1,/list_test/foo/2')
        handler = ListWrapper(self.application, request)
        handler.put('foo/bar')

        request = create_request('DELETE', body = 'X-OCCI-Location: /list_test/foo/2')
        handler = ListWrapper(self.application, request)
        handler.delete('foo/bar')

        request = create_request('GET')
        handler = ListWrapper(self.application, request)
        handler.get('foo/bar')
        heads, data = handler.get_output()
        self.assertTrue(data.find('/list_test/foo/2') == -1)

class QueryWrapper(QueryHandler):

    body = ''

    def get_output(self):
        heads, data = self._headers, self.body
        self.body = ''
        self._headers = {}
        return heads, data

    def write(self, chunk):
        self.body = chunk

class QueryHandlerTest(unittest.TestCase):

    application = None

    def setUp(self):
        self.application = Application([(r"/-/", QueryWrapper)])

        try:
            request = create_request('DELETE', body = http_body_mixin)
            handler = QueryWrapper(self.application, request)
            handler.delete()
        except:
            pass

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_get_for_success(self):
        request = create_request('GET')
        handler = QueryWrapper(self.application, request)
        handler.get()
        heads, data = handler.get_output()

    def test_put_for_succes(self):
        request = create_request('PUT', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.put()

    def test_delete_for_success(self):
        request = create_request('PUT', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.put()

        request = create_request('DELETE', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.delete()

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_get_for_failure(self):
        request = create_request('GET', headers = {'Accept':'text/json'})
        handler = QueryWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.get)

    def test_put_for_failure(self):
        request = create_request('PUT', body = http_body)
        handler = QueryWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.put)

    def test_delete_for_failure(self):
        request = create_request('PUT', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.put()

        request = create_request('DELETE', body = http_body)
        handler = QueryWrapper(self.application, request)
        self.assertRaises(HTTPError, handler.delete)

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_get_for_sanity(self):
        request = create_request('GET')
        handler = QueryWrapper(self.application, request)
        handler.get()
        heads, data = handler.get_output()

    def test_put_for_sanity(self):
        request = create_request('PUT', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.put()

        request = create_request('GET')
        handler = QueryWrapper(self.application, request)
        handler.get()
        heads, data = handler.get_output()
        self.assertTrue(data.find('mine;scheme=http://mystuff.com/occi;location=/foo/bar/') > -1)

    def test_delete_for_sanity(self):
        request = create_request('PUT', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.put()

        request = create_request('DELETE', body = http_body_mixin)
        handler = QueryWrapper(self.application, request)
        handler.delete()

        request = create_request('GET')
        handler = QueryWrapper(self.application, request)
        handler.get()
        heads, data = handler.get_output()
        self.assertTrue(data.find('mine;scheme=http://mystuff.com/occi;location=/foo/bar/') == -1)

class LinkBackendTest(unittest.TestCase):

    backend = LinkBackend()
    entityOne = Resource()
    entityTwo = Resource()
    link = Link()
    new_link = Link()

    def setUp(self):
        self.link.source = '1'
        self.link.target = '2'
        self.link.attributes['stopme'] = 'jeeha'
        self.new_link.source = '2'
        self.new_link.target = '1'
        self.new_link.attributes['stopme'] = 'ohno'
        self.entityOne.identifier = 1
        self.entityTwo.identifier = 2

        service.RESOURCES['1'] = self.entityOne
        service.RESOURCES['2'] = self.entityTwo

    def tearDown(self):
        service.RESOURCES.pop('1')
        service.RESOURCES.pop('2')

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_create_for_success(self):
        self.backend.create(self.link)

    def test_retrieve_for_success(self):
        self.backend.retrieve(self.link)

    def test_update_for_success(self):
        self.backend.create(self.link)
        self.backend.update(self.link, self.new_link)

    def test_delete_for_success(self):
        self.backend.delete(self.link)

    def test_action_for_success(self):
        self.backend.action(self.link, None)

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_create_for_failure(self):
        self.link.source = ''
        self.assertRaises(AttributeError, self.backend.create, self.link)
        self.link.source = 'bla'
        self.link.target = ''
        self.assertRaises(AttributeError, self.backend.create, self.link)

        defunct = Link()
        defunct.source = 'qwer'
        defunct.source = 'rewq'
        self.assertRaises(AttributeError, self.backend.create, defunct)

    def test_retrieve_for_failure(self):
        pass

    def test_update_for_failure(self):
        defunct = Link()
        defunct.source = 'qwer'
        defunct.source = 'rewq'
        self.assertRaises(AttributeError, self.backend.update, self.link, defunct)

    def test_delete_for_failure(self):
        defunct = Link()
        defunct.source = 'qwer'
        defunct.source = 'rewq'
        self.assertRaises(AttributeError, self.backend.delete, defunct)

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_update_for_sanity(self):
        self.backend.create(self.link)
        self.backend.update(self.link, self.new_link)
        self.assertEquals(self.link.source, self.new_link.source)
        self.assertEquals(self.link.target, self.new_link.target)
        self.assertEquals(self.link.attributes, self.new_link.attributes)

class MixinBackendTest(unittest.TestCase):

    backend = MixinBackend()

    def test_if_all_pass(self):
        self.backend.create(None)
        self.backend.retrieve(None)
        self.backend.update(None, None)
        self.backend.delete(None)
        self.backend.action(None, None)

if __name__ == '__main__':
    unittest.main()
