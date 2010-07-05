'''
Created on Jul 5, 2010

@author: tmetsch
'''
from pyrest import service
import unittest

class BasicRestTest(unittest.TestCase):

    # request("/hello",
    #        method = 'GET',
    #        data = None,
    #        host = '0.0.0.0:8080',
    #        headers = None,
    #        https = False)

    def test_post_for_success(self):
        response = service.app.request("/123", method = "POST")
        self.assertEquals(response.status, '200 OK')

    def test_get_for_success(self):
        response = service.app.request("/123")
        self.assertEquals(response.status, '200 OK')

    def test_put_for_success(self):
        response = service.app.request("/123", method = "PUT")
        self.assertEquals(response.status, '200 OK')

    def test_delete_for_success(self):
        response = service.app.request("/123", method = "DELETE")
        self.assertEquals(response.status, '200 OK')

if __name__ == "__main__":
    unittest.main()
