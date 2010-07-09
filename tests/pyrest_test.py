# 
# Copyright (C) 2010  Platform Computing
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
'''
Created on Jul 5, 2010

@author: tmetsch
'''
from pyrest import service
import unittest

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
        heads = {'Category': 'compute;scheme="http://purl.org/occi/kind#";label="Compute Resource", myimage;scheme="http://example.com/user/categories/templates#"; label="My very special server"'}
        response = service.app.request("/", method = "POST", headers = heads)
        self.assertEquals(response.status, '200 OK')

        #response = service.app.request("/job/", method = "POST")
        #self.assertEquals(response.status, '200 OK')

    def test_get_for_success(self):
        # simple post and get on the returned location should return 200 OK
        response = service.app.request("/", method = "POST")
        loc = response.headers['Location']
        response = service.app.request(loc)
        self.assertEquals(response.status, '200 OK')

        # get on */ should return listing
        response = service.app.request("/")
        self.assertEquals(response.status, '200 OK')
        self.assertEquals(response.data, 'TODO: Listing sub resources...')

    def test_put_for_success(self):
        # Put on specified resource should return 200 OK (non-existent)
        response = service.app.request("/123", method = "PUT")
        self.assertEquals(response.status, '200 OK')

        # put on existent should update
        response = service.app.request("/123", method = "PUT", data = "hello")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_success(self):
        # Del on created resource should return 200 OK
        response = service.app.request("/", method = "POST")
        loc = response.headers['Location']
        response = service.app.request(loc, method = "DELETE")
        self.assertEquals(response.status, '200 OK')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_post_for_failure(self):
        # post to non-existent resource should return 404
        response = service.app.request("/123", method = "POST")
        self.assertEquals(response.status, '404 Not Found')

    def test_get_for_failure(self):
        # get on non existent should return 404
        response = service.app.request("/123")
        self.assertEquals(response.status, '404 Not Found')

    def test_put_for_failure(self):
        # maybe test invalid data ?
        pass

    def test_delete_for_failure(self):
        # delete of non existent should return 404
        response = service.app.request("/123", method = "DELETE")
        self.assertEquals(response.status, '404 Not Found')

    # --------
    # TEST FOR SANITY
    # --------

    def test_post_for_sanity(self):
        # first create (post) then get
        response = service.app.request("/", method = "POST", data = "occi.job.executable=/bin/sleep")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.app.request(loc)
        self.assertEquals(response.data, 'occi.job.executable=/bin/sleep')

        # post to existent url should create sub resource 
        # TODO

    def test_get_for_sanity(self):
        # first create (put) than test get on parent for listing
        service.app.request("/job/123", method = "PUT", data = "hello")
        response = service.app.request("/job/")
        self.assertEquals(response.data, 'TODO: Listing sub resources...')

    def test_put_for_sanity(self):
        # put on existent should update
        response = service.app.request("/", method = "POST", data = "occi.job.executable=/bin/sleep")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        response = service.app.request(loc)
        self.assertEquals(response.data, "occi.job.executable=/bin/sleep")
        response = service.app.request(loc, method = "PUT", data = "occi.job.executable=/bin/echo")
        self.assertEquals(response.status, '200 OK')
        response = service.app.request(loc)
        self.assertEquals(response.data, "occi.job.executable=/bin/echo")

        # put on non-existent should create
        response = service.app.request("/abc", method = "PUT", data = "occi.job.executable=/bin/sleep")
        self.assertEquals(response.status, '200 OK')
        response = service.app.request("/abc")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_sanity(self):
        # create and delete an entry than try get
        response = service.app.request("/", method = "POST", data = "occi.job.executable=/bin/sleep")
        self.assertEquals(response.status, '200 OK')
        loc = response.headers['Location']
        service.app.request(loc, method = "DELETE")
        response = service.app.request(loc)
        self.assertEquals(response.status, "404 Not Found")

class SecurityTests(unittest.TestCase):
    pass

class CategoriesTests(unittest.TestCase):
    pass

class ActionsTests(unittest.TestCase):
    pass

class LinkTests(unittest.TestCase):
    pass

class QueryTests(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
