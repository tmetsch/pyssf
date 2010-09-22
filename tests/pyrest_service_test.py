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
from mocks import DummyBackend, SecurityHandler, SimpleSecurityHandler
from pyrest.myexceptions import SecurityException
from pyrest.service import ResourceHandler
import base64
import pyrest.service as service
import string
import unittest
import web
'''
Created on Jul 5, 2010

@author: tmetsch
'''

app = web.application(('/(.*)', 'ResourceHandler'), globals())
dummy = DummyBackend()

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

    def test_post_for_success(self):
        # simple post on entry point should return 200 OK
        response = app.request("/", method = "POST", headers = dummy.http_category)
        self.assertEquals(response.status, '200 OK')

        #response = app.request("/job/", method = "POST")
        #self.assertEquals(response.status, '200 OK')

    def test_get_for_success(self):
        # simple post and get on the returned location should return 200 OK
        response = app.request("/", method = "POST", headers = dummy.http_category)
        loc = response.headers['Location']
        response = app.request(loc)
        self.assertEquals(response.status, '200 OK')

        # get on */ should return listing
        response = app.request("/")
        self.assertEquals(response.status, '200 OK')
        self.assertEquals(response.data, 'Listing sub resources...')

    def test_put_for_success(self):
        # Put on specified resource should return 200 OK (non-existent)
        response = app.request("/123", method = "PUT", headers = dummy.http_category)
        self.assertEquals(response.status, '200 OK')

        # put on existent should update
        response = app.request("/123", method = "PUT", headers = dummy.http_category, data = "hello")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_success(self):
        # Del on created resource should return 200 OK
        response = app.request("/", method = "POST", headers = dummy.http_category)
        loc = response.headers['Location']
        response = app.request(loc, method = "DELETE")
        self.assertEquals(response.status, '200 OK')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_post_for_failure(self):
        # post to non-existent resource should return 404
        response = app.request("/123", method = "POST", headers = dummy.http_category)
        self.assertEquals(response.status, '404 Not Found')

    def test_get_for_failure(self):
        # get on non existent should return 404
        response = app.request("/123")
        self.assertEquals(response.status, '404 Not Found')

    def test_put_for_failure(self):
        # maybe test invalid data ?
        pass

    def test_delete_for_failure(self):
        # delete of non existent should return 404
        response = app.request("/123", method = "DELETE")
        self.assertEquals(response.status, '404 Not Found')

    # --------
    # TEST FOR SANITY
    # --------

    def test_post_for_sanity(self):
        # first create (post) then get
        response = app.request("/", method = "POST", headers = dummy.http_category, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = app.request(loc)
        self.assertEquals(response.data, 'some data')

        # post to existent url should create sub resource 
        response = app.request(loc, method = "POST", headers = dummy.http_category, data = "some data")
        self.assertEquals(response.status, '200 OK')
        new_loc = response.headers['Location']
        # look if a / got added and org loc is in new loc.
        self.assertTrue(new_loc[1:].find('/') > -1)
        self.assertTrue(new_loc.find(loc) > -1)

    def test_get_for_sanity(self):
        # first create (put) than test get on parent for listing
        app.request("/job/123", method = "PUT", headers = dummy.http_category, data = "hello")
        response = app.request("/job/")
        self.assertEquals(response.data, 'Listing sub resources...')

    def test_put_for_sanity(self):
        # put on existent should update
        response = app.request("/", method = "POST", headers = dummy.http_category, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = app.request(loc)
        self.assertEquals(response.data, "some data")
        response = app.request(loc, method = "PUT", headers = dummy.http_category, data = "other data")
        self.assertEquals(response.status, '200 OK')
        response = app.request(loc)
        self.assertEquals(response.data, "other data")

        # put on non-existent should create
        response = app.request("/abc", method = "PUT", headers = dummy.http_category, data = "some data")
        self.assertEquals(response.status, '200 OK')
        response = app.request("/abc")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_sanity(self):
        # create and delete an entry than try get
        response = app.request("/", method = "POST", headers = dummy.http_category, data = "some data")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = app.request(loc, method = "DELETE")
        response = app.request(loc)
        self.assertEquals(response.status, "404 Not Found")

class CategoriesTests(unittest.TestCase):

    # Note: more tests are done in the parser tests

    def test_categories_for_failure(self):
        # if a post is done without category -> Fail
        response = app.request("/", method = "POST")
        self.assertEquals('400 Bad Request', str(response.status))

    def test_categories_for_sanity(self):
        # if a post is done and later a get should return same category
        response = app.request("/", method = "POST", headers = dummy.http_category)
        url = response.headers['Location']
        response = app.request(url)
        cat = response.headers['Category'].split(';')
        self.assertEquals(cat[0], dummy.category.term)
        self.assertEquals(cat[1].split('=')[-1:].pop(), dummy.category.scheme)

class AttributeTests(unittest.TestCase):

    # Note: more tests are done in the parser tests

    def test_attributes_for_sanity(self):
        # pass along some attributes and see if they can be retrieved
        response = app.request("/", method = "POST", headers = dummy.http_category_with_attr)
        url = response.headers['Location']
        response = app.request(url)
        self.assertEquals(response.headers['Attribute'], 'occi.pyssf.test=Bar')

class LinkTests(unittest.TestCase):

    # Note: more test are done in the parser tests

    def test_links_for_sanity(self):
        pass

    def test_links_in_header_for_success(self):
        # test if a terminate link is added
        response = app.request("/", method = "POST", headers = dummy.http_category)
        url = response.headers['Location']
        response = app.request(url)
        self.assertEquals(response.headers['Link'].split(';')[1], 'action=' + dummy.action_category.term + '>')

class ActionsTests(unittest.TestCase):

    def test_trigger_action_for_success(self):
        response = app.request("/", method = "POST", headers = dummy.http_category)
        url = response.headers['Location']
        response = app.request(url)
        tmp = response.headers['Link'].split(',').pop()
        action_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = app.request(action_url, method = "POST", headers = dummy.http_action_category)
        self.assertEquals(response.status, '200 OK')

    def test_trigger_action_for_failure(self):
        # only post allowed!
        response = app.request("/", method = "POST", headers = dummy.http_category)
        url = response.headers['Location']
        response = app.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = app.request(kill_url, method = "PUT")
        self.assertEquals('400 Bad Request', str(response.status))

        # trigger not existing action!
        response = app.request("/", method = "POST", headers = dummy.http_category)
        url = response.headers['Location']
        response = app.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = app.request(kill_url + 'all', method = "POST")
        self.assertEquals(str(response.status), '400 Bad Request')

        # trigger action on non existing resource
        response = app.request('http://abc.com/all;kill', method = "POST")
        self.assertEquals(response.status, '404 Not Found')

    def test_trigger_action_for_sanity(self):
        # check if result is okay :-)
        response = app.request("/", method = "POST", headers = dummy.http_category)
        url = response.headers['Location']
        response = app.request(url)
        tmp = response.headers['Link'].split(',').pop()
        kill_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        app.request(kill_url, method = "POST", headers = dummy.http_action_category)
        response = app.request(url)
        self.assertEquals(response.headers['Attribute'], 'occi.pyssf.test=Foo')

class QueryTests(unittest.TestCase):
    pass

class SecurityTests(unittest.TestCase):

    heads = dummy.http_category.copy()
    heads['Authorization'] = 'Basic ' + string.strip(base64.encodestring('foo' + ':' + 'ssf'))
    heads2 = dummy.http_category.copy()
    heads2['Authorization'] = 'Basic ' + string.strip(base64.encodestring('bar' + ':' + 'ssf'))

    action_heads = dummy.http_action_category.copy()
    action_heads['Authorization'] = 'Basic ' + string.strip(base64.encodestring('foo' + ':' + 'ssf'))

    heads_apache = heads.copy()
    heads_apache.pop("Authorization")
    heads_apache['SSL_CLIENT_CERT_DN'] = '/C=DE/L=Munich/O=Sun/OU=Staff/CN=Foo'
    heads_apache2 = heads_apache.copy()
    heads_apache2['SSL_CLIENT_CERT_DN'] = '/C=DE/L=Munich/O=Sun/OU=Staff/CN=Bar'

    def_heads = {'Authorization': 'Basic ' + string.strip(base64.encodestring('foo' + ':' + 'asd'))}
    def_heads2 = dummy.http_category

    def setUp(self):
        service.AUTHENTICATION_ENABLED = True
        service.SECURITY_HANDLER = SimpleSecurityHandler()

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_authenticate_for_success(self):
        # test login
        response = app.request("/", method = "GET", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

    def test_authorization_for_success(self):
        response = app.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']
        response = app.request(url, method = "GET", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        tmp = response.headers['Link'].split(',').pop()
        action_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = app.request(action_url, method = "POST", headers = self.action_heads)
        self.assertEquals(response.status, '200 OK')

        response = app.request(url, method = "PUT", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        response = app.request(url, method = "DELETE", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

        # PKI cert & mod_wsgi testing...
        response = app.request("/", method = "POST", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']
        response = app.request(url, method = "GET", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        response = app.request(url, method = "PUT", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        response = app.request(url, method = "DELETE", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_authenticate_for_failure(self):
        # auth enabled but no security handler...
        service.SECURITY_HANDLER = None
        response = app.request("/", method = "GET", headers = self.heads)
        self.assertEquals(response.status, '401 Unauthorized')
        service.SECURITY_HANDLER = SimpleSecurityHandler()

        # test wrong password
        response = app.request("/", method = "GET", headers = self.def_heads)
        self.assertEquals(response.status, '401 Unauthorized')

    def test_authorization_for_failure(self):
        response = app.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']

        response = app.request(url, method = "GET", headers = self.heads)
        tmp = response.headers['Link'].split(',').pop()
        action_url = tmp[tmp.find('<') + 1:tmp.find('>')]
        response = app.request(action_url, method = "POST", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')

        response = app.request(url, method = "GET", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = app.request(url, method = "PUT", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = app.request(url, method = "DELETE", headers = self.heads2)
        self.assertEquals(response.status, '401 Unauthorized')

        # PKI cert & mod_wsgi testing...
        response = app.request("/", method = "POST", headers = self.heads_apache)
        self.assertEquals(response.status, '200 OK')
        url = response.headers['Location']
        response = app.request(url, method = "GET", headers = self.heads_apache2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = app.request(url, method = "PUT", headers = self.heads_apache2)
        self.assertEquals(response.status, '401 Unauthorized')
        response = app.request(url, method = "DELETE", headers = self.heads_apache2)
        self.assertEquals(response.status, '401 Unauthorized')

        # auth enabled but no user info
        response = app.request("/", method = "POST", headers = self.def_heads2)
        self.assertEquals(response.status, '401 Unauthorized')

    # --------
    # TEST FOR SANITY
    # --------

    def test_authenticate_for_sanity(self):
        # test post, get, put and delete authentication for sanity...
        # post
        response = app.request("/", method = "POST", headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        # get
        response = app.request(loc, headers = self.heads)
        self.assertEquals(response.status, '200 OK')
        # put
        response = app.request(loc, method = "PUT", headers = self.heads, data = "bla")
        self.assertEquals(response.status, '200 OK')
        # delete
        response = app.request(loc, method = "DELETE", headers = self.heads)
        self.assertEquals(response.status, '200 OK')

    def test_authorization_for_sanity(self):
        # done on server side - no chances to check it here...
        pass

if __name__ == "__main__":
    unittest.main()
