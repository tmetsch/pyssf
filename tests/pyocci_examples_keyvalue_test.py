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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
'''
Created on Nov 26, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.core import Resource, Action
from pyocci.examples.keyvalue import KeyValueBackend
import unittest

class KeyValueBackendTest(unittest.TestCase):

    backend = KeyValueBackend()
    action = Action()
    kv = Resource()
    new_kv = Resource()

    def setUp(self):
        self.action.kind = KeyValueBackend.terminate_category

        self.kv.identifier = '123'
        self.kv.kind = KeyValueBackend.kind
        self.kv.attributes['key'] = 'foo'
        self.kv.attributes['value'] = 'bar'
        self.kv.actions = [self.action]

        self.new_kv.kind = KeyValueBackend.kind
        self.new_kv.summary = 'Jeeha'
        self.new_kv.attributes['key'] = 'foo'
        self.new_kv.attributes['value'] = 'bar'

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_create_for_success(self):
        self.backend.create(self.kv)

    def test_retrieve_for_success(self):
        self.backend.retrieve(self.kv)

    def test_update_for_success(self):
        self.backend.update(self.kv, self.new_kv)

    def test_delete_for_success(self):
        self.backend.delete(self.kv)

    def test_action_for_success(self):
        self.backend.action(self.kv, self.action)

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_create_for_failure(self):
        self.kv.attributes = {}
        self.assertRaises(AttributeError, self.backend.create, self.kv)

    def test_retrieve_for_failure(self):
        pass

    def test_update_for_failure(self):
        pass

    def test_delete_for_failure(self):
        pass

    def test_action_for_failure(self):
        self.assertRaises(AttributeError, self.backend.action, self.new_kv, self.action)

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_update_for_sanity(self):
        self.backend.update(self.kv, self.new_kv)
        self.assertEquals(self.kv.summary, self.new_kv.summary)
        self.assertEquals(self.kv.attributes['key'], self.new_kv.attributes['key'])
        self.assertEquals(self.kv.attributes['value'], self.new_kv.attributes['value'])

    def test_action_for_sanity(self):
        self.backend.action(self.kv, self.action)
        self.assertRaises(AttributeError, self.backend.action, self.kv, self.action)

if __name__ == "__main__":
    unittest.main()
