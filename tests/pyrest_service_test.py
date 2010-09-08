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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 
from pyrest.myexceptions import SecurityException
'''
Created on Jul 5, 2010

@author: tmetsch
'''
from mocks import DummyBackend, SecurityHandler, SimpleSecurityHandler
from pyrest.service import ResourceHandler
import base64
import pyrest.service as service
import string
import unittest
import web

class AbstractClassTests(unittest.TestCase):

    sh = SecurityHandler()

    # --------
    # TEST FOR FAILURE
    # --------

    def test_if_not_implemeted_is_raised(self):
        self.assertRaises(SecurityException, self.sh.authenticate, '', '')

class ResourceCreationTests(unittest.TestCase):

    # request("/hello",
    #        method = 'GET',
    #        data = None,
    #        host = '0.0.0.0:8080',
    #        headers = None,
    #        https = False)

    # --------
    # TEST FOR SUCCESS
    # --------

    service.APPLICATION = web.application(('/(.*)', 'ResourceHandler'), globals())
    service.ResourceHandler.backend = DummyBackend()
    heads = {'Category': 'compute;scheme="http://schemas.ogf.org/occi/resource#";label="Compute Resource"'}

    def test_post_for_success(self):
        # simple post on entry point should return 200 OK
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        #response = service.APPLICATION.request("/job/", method = "POST")
        #self.assertEquals(response.status, '200 OK')

    def test_get_for_success(self):
        # simple post and get on the returned location should return 200 OK
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.status, '200 OK')

        # get on */ should return listing
        response = service.APPLICATION.request("/")
        self.assertEquals(response.status, '200 OK')
        self.assertEquals(response.data, 'Listing sub resources...')

    def test_put_for_success(self):
        # Put on specified resource should return 200 OK (non-existent)
        response = service.APPLICATION.request("/123", method = "PUT", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        # put on existent should update
        response = service.APPLICATION.request("/123", method = "PUT", headers = self.heads, data = "hello")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_success(self):
        # Del on created resource should return 200 OK
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc, method = "DELETE")
        self.assertEquals(response.status, '200 OK')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_post_for_failure(self):
        # post to non-existent resource should return 404
        response = service.APPLICATION.request("/123", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '404 Not Found')

    def test_get_for_failure(self):
        # get on non existent should return 404
        response = service.APPLICATION.request("/123")
        self.assertEquals(response.status, '404 Not Found')

    def test_put_for_failure(self):
        # maybe test invalid data ?
        pass

    def test_delete_for_failure(self):
        # delete of non existent should return 404
        response = service.APPLICATION.request("/123", method = "DELETE")
        self.assertEquals(response.status, '404 Not Found')

    # --------
    # TEST FOR SANITY
    # --------

    def test_post_for_sanity(self):
        # first create (post) then get
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.data, 'some data')

        # post to existent url should create sub resource 
        # TODO

    def test_get_for_sanity(self):
        # first create (put) than test get on parent for listing
        service.APPLICATION.request("/job/123", method = "PUT", headers = self.heads, data = "hello")
        response = service.APPLICATION.request("/job/")
        self.assertEquals(response.data, 'Listing sub resources...')

    def test_put_for_sanity(self):
        # put on existent should update
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.data, "some data")
        response = service.APPLICATION.request(loc, method = "PUT", headers = self.heads, data = "other data")
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request(loc)
        # TODO needs proper backend!
        #self.assertEquals(response.data, "other data")

        # put on non-existent should create
        response = service.APPLICATION.request("/abc", method = "PUT", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request("/abc")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_sanity(self):
        # create and delete an entry than try get
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.APPLICATION.request(loc, method = "DELETE")
        response = service.APPLICATION.request(loc)
        self.assertEquals(response.status, "404 Not Found")

class CategoriesTests(unittest.TestCase):

    # Note: more tests are done in the parser tests
    heads = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'occi.drmaa.remote_command':'/bin/sleep'}

    def test_categories_for_failure(self):
        # if a post is done without category -> Fail
        response = service.APPLICATION.request("/", method = "POST")
        self.assertEquals('400 Bad Request', str(response.status))

    def test_categories_for_sanity(self):
        # if a post is done and later a get should return same category
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        cat = response.headers['Category'].split(';')
        self.assertEquals(cat[0], 'job')
        self.assertEquals(cat[1].split('=')[-1:].pop(), 'http://schemas.ogf.org/occi/resource#')

class AttributeTests(unittest.TestCase):

    # Note: more tests are done in the parser tests

    heads = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'Attribute': 'occi.drmaa.remote_command = /bin/sleep'}

    def test_attributes_for_sanity(self):
        # pass along some attributes and see if they can be retrieved
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        #print response
        self.assertEquals(response.headers['Attribute'], 'occi.drmaa.remote_command=/bin/sleep')

class LinkTests(unittest.TestCase):

    # Note: more test are done in the parser tests
    heads = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'Link': '</123>;class="test";rel="http://example.com/next/job";title="Next job"', 'occi.drmaa.remote_command':'/bin/sleep'}

    def test_links_for_sanity(self):
        pass

    def test_links_in_header_for_success(self):
        # test if a terminate link is added
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        self.assertEquals(response.headers['Link'].split(';')[1], 'action=terminate>')

class ActionsTests(unittest.TestCase):

    heads = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'occi.drmaa.remote_command':'/bin/sleep'}

    def test_trigger_action_for_success(self):
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(kill_url, method = "POST")
        self.assertEquals(response.status, '200 OK')

    def test_trigger_action_for_failure(self):
        # only post allowed!
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(kill_url, method = "PUT")
        self.assertEquals('400 Bad Request', str(response.status))

        # trigger not existing action!
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(kill_url + 'all', method = "POST")
        self.assertEquals(str(response.status), '400 Bad Request')

        # trigger action on non existing resource
        response = service.APPLICATION.request('http://abc.com/all;kill', method = "POST")
        self.assertEquals(response.status, '404 Not Found')

    def test_trigger_action_for_sanity(self):
        # check if result is okay :-)
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        url = response.headers['Location']
        response = service.APPLICATION.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        service.APPLICATION.request(kill_url, method = "POST")
        response = service.APPLICATION.request(url)
        self.assertEquals(response.headers['Attribute'], 'occi.drmaa.job_state=EXIT')

class QueryTests(unittest.TestCase):
    pass

class SecurityTests(unittest.TestCase):

    heads = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'occi.drmaa.remote_command':'/bin/sleep', 'Authorization': 'Basic ' + string.strip(base64.encodestring('foo' + ':' + 'ssf'))}
    heads2 = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'occi.drmaa.remote_command':'/bin/sleep', 'Authorization': 'Basic ' + string.strip(base64.encodestring('bar' + ':' + 'ssf'))}

    heads_apache = heads.copy()
    heads_apache.pop("Authorization")
    heads_apache['SSL_CLIENT_CERT_DN'] = '/C=DE/L=Munich/O=Sun/OU=Staff/CN=Foo'
    heads_apache2 = heads_apache.copy()
    heads_apache2['SSL_CLIENT_CERT_DN'] = '/C=DE/L=Munich/O=Sun/OU=Staff/CN=Bar'

    def_heads = {'Authorization': 'Basic ' + string.strip(base64.encodestring('foo' + ':' + 'asd'))}
    def_heads2 = {'Category': 'job;scheme="http://schemas.ogf.org/occi/resource#";label="Job Resource"', 'occi.drmaa.remote_command':'/bin/sleep'}

    def setUp(self):
        service.AUTHENTICATION_ENABLED = True
        service.SECURITY_HANDLER = SimpleSecurityHandler()

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_authenticate_for_success(self):
        # test login
        response = service.APPLICATION.request("/", method = "GET", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

    def test_authorization_for_success(self):
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']
        response = service.APPLICATION.request(url, method = "GET", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        tmp = response.headers['Link'].split(',').pop()
        action_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(action_url, method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        response = service.APPLICATION.request(url, method = "PUT", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request(url, method = "DELETE", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        # PKI cert & mod_wsgi testing...
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']
        response = service.APPLICATION.request(url, method = "GET", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request(url, method = "PUT", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        response = service.APPLICATION.request(url, method = "DELETE", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_authenticate_for_failure(self):
        # auth enabled but no security handler...
        service.SECURITY_HANDLER = None
        response = service.APPLICATION.request("/", method = "GET", headers = self.heads)
        self.assertEquals(response.status, '401 Unauthorized')
        service.SECURITY_HANDLER = SimpleSecurityHandler()

        # test wrong password
        response = service.APPLICATION.request("/", method = "GET", headers = self.def_heads)
        self.assertEquals(response.status, '401 Unauthorized')

    def test_authorization_for_failure(self):
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']

        response = service.APPLICATION.request(url, method = "GET", headers = self.heads)
        tmp = response.headers['Link'].split(',').pop()
        action_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = service.APPLICATION.request(action_url, method = "POST", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')

        response = service.APPLICATION.request(url, method = "GET", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = service.APPLICATION.request(url, method = "PUT", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = service.APPLICATION.request(url, method = "DELETE", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')

        # PKI cert & mod_wsgi testing...
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']
        response = service.APPLICATION.request(url, method = "GET", headers = self.heads_apache2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = service.APPLICATION.request(url, method = "PUT", headers = self.heads_apache2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = service.APPLICATION.request(url, method = "DELETE", headers = self.heads_apache2)
        self.assertEquals(response.status, '401 Unauthorized')

        # auth enabled but no user info
        response = service.APPLICATION.request("/", method = "POST", headers = self.def_heads2)
        self.assertEquals(response.status, '401 Unauthorized')

    # --------
    # TEST FOR SANITY
    # --------

    def test_authenticate_for_sanity(self):
        # test post, get, put and delete authentication for sanity...
        # post
        response = service.APPLICATION.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        # get
        response = service.APPLICATION.request(loc, headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        # put
        response = service.APPLICATION.request(loc, method = "PUT", headers = self.heads, data = "bla")
        self.assertEquals(response.status, '200 OK')
        # delete
        response = service.APPLICATION.request(loc, method = "DELETE", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

    def test_authorization_for_sanity(self):
        # done on server side - no chances to check it here...
        pass

if __name__ == "__main__":
    unittest.main()
