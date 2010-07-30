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
from pyrest.backends import JobHandler
from pyrest.myexceptions import MissingActionException, StateException
from pyrest.myexceptions import MissingAttributesException
from pyrest.resource_model import JobResource, Link
import time
import unittest

class JobHandlerTest(unittest.TestCase):

    backend = JobHandler()
    resource = JobResource()
    resource.attributes['occi.drmaa.remote_command'] = '/bin/echo'

    def setUp(self):
        try:
            self.backend.delete(self.resource)
        except:
            pass
        self.resource.id = '123'
        self.resource.attributes = {}
        self.resource.attributes['occi.drmaa.remote_command'] = '/bin/echo'
        self.resource.links = []
        link = Link()
        link.link_class = 'action'
        link.rel = 'http://purl.org/occi/ drmaa/action#terminate'
        link.target = '/' + self.resource.id + ';terminate'
        link.title = 'Terminate Job'
        self.resource.links = [link]

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
        # we expect a link
        self.assertTrue(len(self.resource.links) > 0)

    def test_update_for_success(self):
        # doesn't do anything
        pass

    def test_delete_for_success(self):
        self.backend.create(self.resource)
        self.backend.delete(self.resource)
        # job list should be empty again...
        self.assertEquals(len(self.backend.jobs), 0)

    def test_action_for_success(self):
        self.setUp()
        self.backend.create(self.resource)
        self.backend.action(self.resource, 'terminate')
        # no more links should be there
        self.assertEquals(len(self.resource.links), 0)

    # --------
    # TEST FOR FAILURE
    # --------

    def test_create_for_failure(self):
        # test create without arg.
        self.resource.attributes = []
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
        self.backend.create(self.resource)
        self.assertRaises(MissingActionException, self.backend.action, self.resource, 'blabber')

        # non existent resource
        self.setUp()
        self.assertRaises(StateException, self.backend.action, self.resource, 'terminate')

    # --------
    # TEST FOR SANITY
    # --------

    def test_create_for_sanity(self):
        # test if right links are there
        self.resource.links = []
        self.backend.create(self.resource)
        # release should be added
        self.assertEquals(self.resource.links[0].target, '/123;terminate')

        # check if state changes when done...wait for LSF
        time.sleep(20)
        self.backend.retrieve(self.resource)
        self.assertEquals(self.resource.attributes['occi.drmaa.job_state'], 'done')

    def test_retrieve_for_sanity(self):
        self.resource.attributes['occi.drmaa.remote_command'] = '/bin/sleep'
        self.resource.attributes['occi.drmaa.args'] = '10000'
        self.backend.create(self.resource)

        # check if terminate action got added to a running job
        self.resource.links = []
        time.sleep(20)
        self.backend.retrieve(self.resource)
        self.assertEquals(self.resource.attributes['occi.drmaa.job_state'], 'running')
        self.assertTrue(len(self.resource.links) == 1)
        self.assertEquals(self.resource.links[0].target, '/123;terminate')

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
        self.backend.action(self.resource, 'terminate')
        # no more links should be there
        self.assertEquals(len(self.resource.links), 0)

if __name__ == "__main__":
    unittest.main()
