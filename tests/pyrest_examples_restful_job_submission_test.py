'''
Created on Sep 20, 2010

@author: tmetsch
'''
from pyrest import backends
from pyrest.examples.restful_job_submission import JobHandler
from pyrest.myexceptions import MissingActionException, StateException, \
    MissingAttributesException
from pyrest.resource_model import Resource, Action
import time
import unittest

class JobHandlerTest(unittest.TestCase):

    backends.REGISTERED_BACKENDS = {}
    backend = JobHandler()
    resource = Resource()
    action = Action()

    def setUp(self):
        try:
            self.backend.delete(self.resource)
        except:
            # cleanup so no need to check ex.
            # pylint: disable=W0702
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
        self.backend.update(self.resource, self.resource)
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
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
