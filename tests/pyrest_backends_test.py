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
from pyrest.backends import Handler, JobHandler
from pyrest.myexceptions import MissingActionException, StateException, \
    MissingAttributesException
from pyrest.resource_model import Resource, Action
from tests import mocks
import time
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

class JobHandlerTest(unittest.TestCase):

    backend = JobHandler()
    resource = Resource()
    action = Action()

    def setUp(self):
        try:
            self.backend.delete(self.resource)
        except:
            pass
        self.resource.id = '123'
        self.resource.attributes = {}
        self.resource.attributes['occi.drmaa.remote_command'] = '/bin/echo'
        self.resource.categories = [JobHandler.category]
        self.action.categories = [JobHandler.terminate_category]

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_create_for_success(self):
        self.backend.create(self.resource)
        # there should be a job id.
        self.assertTrue(self.resource.attributes['occi.drmaa.job_id'] > 0)

    def test_retrieve_for_success(self):
        self.backend.create(self.resource)
        self.backend.retrieve(self.resource)
        # we expect a state
        self.assertFalse(self.resource.attributes['occi.drmaa.job_state'] == '')

    def test_update_for_success(self):
        # doesn't do anything
        self.backend.update(self.resource)
        self.assertTrue(True)

    def test_delete_for_success(self):
        self.backend.create(self.resource)
        self.backend.delete(self.resource)
        # job list should be empty again...
        self.assertEquals(len(self.backend.jobs), 0)

    def test_action_for_success(self):
        self.setUp()
        self.backend.create(self.resource)
        self.backend.action(self.resource, self.action)
        # no more links should be there
        self.assertEquals(len(self.resource.actions), 0)

    # --------
    # TEST FOR FAILURE
    # --------

    def test_create_for_failure(self):
        # test create without arg.
        self.resource.attributes = {}
        self.assertRaises(MissingAttributesException, self.backend.create, self.resource)

    def test_retrieve_for_failure(self):
        # test retrieving non existent
        self.assertRaises(MissingAttributesException, self.backend.retrieve, self.resource)

    def test_update_for_failure(self):
        # doesn't do anything
        pass

    def test_delete_for_failure(self):
        # delete non-existent
        self.assertRaises(MissingAttributesException, self.backend.delete, self.resource)

    def test_action_for_failure(self):
        # non existent action...
        non_existing_action = Action()

        self.backend.create(self.resource)
        self.assertRaises(MissingActionException, self.backend.action, self.resource, non_existing_action)

        # non existent resource
        self.setUp()
        self.assertRaises(StateException, self.backend.action, self.resource, self.resource.actions[0])

    # --------
    # TEST FOR SANITY
    # --------

    def test_create_for_sanity(self):
        # test if right links are there
        self.resource.links = []
        self.backend.create(self.resource)
        # terminate action should be added
        self.assertTrue(JobHandler.terminate_category in self.resource.actions[0].categories)

        # check if state changes when done...wait for LSF
        time.sleep(20)
        self.backend.retrieve(self.resource)
        self.assertEquals(self.resource.attributes['occi.drmaa.job_state'], 'done')

    def test_retrieve_for_sanity(self):
        self.resource.attributes['occi.drmaa.remote_command'] = '/bin/sleep'
        self.resource.attributes['occi.drmaa.args'] = '10000'
        self.backend.create(self.resource)

        # check if terminate action got added to a running job
        time.sleep(20)
        self.backend.retrieve(self.resource)
        self.assertTrue(JobHandler.terminate_category in self.resource.actions[0].categories)
        self.assertEquals(self.resource.attributes['occi.drmaa.job_state'], 'running')

    def test_update_for_sanity(self):
        # doesn't do anything
        pass

    def test_delete_for_sanity(self):
        # check if job has been terminated...
        self.backend.create(self.resource)
        self.backend.delete(self.resource)
        self.assertEquals(len(self.backend.jobs), 0)

    def test_action_for_sanity(self):
        # check if links/state have been set right...
        self.backend.create(self.resource)
        self.backend.action(self.resource, self.resource.actions[0])
        # no more links should be there
        self.assertEquals(len(self.resource.links), 0)

if __name__ == "__main__":
    unittest.main()
