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
Created on Jul 19, 2010

@author: tmetsch
'''
from pydrmaa.job import JobFactory, Job, LSFJob, DRMAAJob
import time
import unittest

class AbstractJobTest(unittest.TestCase):

    job = Job()

    # --------
    # TEST FOR FAILURE
    # --------

    def test_not_implemented_throws_for_failure(self):
        self.assertRaises(NotImplementedError, self.job.terminate)
        self.assertRaises(NotImplementedError, self.job.get_state)

class JobFactoryTest(unittest.TestCase):

    # --------
    # TEST FOR SUCCESS
    # --------

    factory = JobFactory()

    def test_create_job_for_success(self):
        # without arguments
        job = self.factory.create_job('/bin/echo')
        self.assertTrue(isinstance(job, Job))
        job.terminate()

        # with args
        args = ['100', '123']
        job = self.factory.create_job('/bin/echo', args)
        self.assertTrue(isinstance(job, Job))
        job.terminate()

    # --------
    # TEST FOR FAILURE
    # --------

    def test_create_job_for_failure(self):
        #...maybe test when LSF not available...
        pass

    # --------
    # TEST FOR SANITY
    # --------

    def test_create_job_for_sanity(self):
        job = self.factory.create_job('/bin/echo')
        self.assertEquals(job.remote_command, '/bin/echo')
        job.terminate()

class LSFJobTest(unittest.TestCase):

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_init_for_success(self):
        job = LSFJob('/bin/echo', [])
        self.assertTrue(isinstance(job, LSFJob))
        job.terminate()

    def test_terminate_for_success(self):
        job = LSFJob('/bin/sleep', ['1000'])
        job.terminate()
        self.assertEquals(job.get_state(), 'EXIT')

    # --------
    # TEST FOR FAILURE
    # --------

    def test_init_for_failure(self):
        # not sure what to test here...
        pass

    def test_terminate_for_failure(self):
        job = LSFJob('/bin/echo', ['hello', 'world'])
        time.sleep(10)
        self.assertRaises(AttributeError, job.terminate)

    # --------
    # TEST FOR SANITY
    # --------

    def test_init_for_sanity(self):
        job = LSFJob('/bin/echo', [])
        self.assertNotEquals(job.job_id, 0)
        job.terminate()

    def test_terminate_for_sanity(self):
        job = LSFJob('/bin/sleep', ['100'])
        job.terminate()
        self.assertEquals(job.get_state(), 'EXIT')

class DRMAAJobTest(unittest.TestCase):

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_init_for_success(self):
        job = DRMAAJob('/bin/echo', [])
        self.assertTrue(isinstance(job, DRMAAJob))
        job.terminate()

    def test_terminate_for_success(self):
        job = DRMAAJob('/bin/sleep', ['1000'])
        job.terminate()
        time.sleep(5)
        self.assertEquals(job.get_state(), 'failed')

if __name__ == "__main__":
    unittest.main()
