'''
Created on Jul 5, 2010

@author: tmetsch
'''
from nose.tools import *
from paste.fixture import TestApp
from pyrest import service
import unittest
import sys

class TestCode(unittest.TestCase):
    def test_index(self):
        middleware = []
        testApp = TestApp(service.app.wsgifunc(*middleware))
        r = testApp.get('/')
        assert_equal(r.status, 200)
        r.mustcontain('Hello, world!')

if __name__ == "__main__":
    print(sys.path)
    unittest.main()
