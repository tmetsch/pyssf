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
'''
Created on Jul 12, 2010

@author: tmetsch
'''
from pyrest import backends
from pyrest.backends import Handler
from pyrest.resource_model import Resource
from tests import mocks
import unittest

class BackendTest(unittest.TestCase):

    dummy = mocks.DummyBackend()

    def setUp(self):
        backends.registered_backends = {}

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_register_for_success(self):
        backends.register([self.dummy.category], self.dummy)
        self.assertTrue(len(backends.registered_backends) > 0)

    def test_find_handler_for_success(self):
        backends.register([self.dummy.category], self.dummy)
        handler = backends.find_right_backend([self.dummy.category])
        self.assertTrue(isinstance(handler, mocks.DummyBackend))

    # --------
    # TEST FOR FAILURE
    # --------

    def test_register_for_failure(self):
        # register invalid handler
        self.assertRaises(AttributeError, backends.register, [self.dummy.category], self)

        # register prev register
        backends.register([self.dummy.category], self.dummy)
        self.assertRaises(AttributeError, backends.register, [self.dummy.category], self.dummy)

    def test_find_handler_for_failure(self):
        # test for non-exit handler should return basic handler!
        backends.register([self.dummy.category], self.dummy)
        handler = backends.find_right_backend([self.dummy.action_category])
        self.assertTrue(isinstance(handler, Handler))

    # --------
    # TEST FOR SANITY
    # --------

    def test_registering_for_sanity(self):
        backends.register([self.dummy.category], self.dummy)
        self.assertEquals(self.dummy, backends.find_right_backend([self.dummy.category]))


class AbstractHandlerTest(unittest.TestCase):

    handler = Handler()
    resource = Resource()

    # --------
    # TEST FOR FAILURE
    # --------

    def test_not_implemented_throws_for_failure(self):
        self.assertRaises(NotImplementedError, self.handler.create, self.resource)
        self.assertRaises(NotImplementedError, self.handler.retrieve, self.resource)
        self.assertRaises(NotImplementedError, self.handler.update, self.resource)
        self.assertRaises(NotImplementedError, self.handler.delete, self.resource)
        self.assertRaises(NotImplementedError, self.handler.action, self.resource, "bla")

if __name__ == "__main__":
    unittest.main()
