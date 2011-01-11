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

from drmaa.const import JobControlAction
from drmaa.errors import InvalidJobException
from pyocci.backends import Backend
from pyocci.core import Action, Kind, Resource, Category
import drmaa

class DRMAAJob():
    """
    A DRMAAv1 job.
    """

    s = drmaa.Session()

    try:
        s.initialize()
        print 'A session was started successfully'
    except:
        pass

    def __init__(self, command, args):
        self.remote_command = command
        self.args = args

        self.job_template = self.s.createJobTemplate()
        self.job_template.remoteCommand = command
        self.job_template.args = args
        self.job_template.joinFiles = True

        self.job_id = self.s.runJob(self.job_template)

    def __del__(self):
        self.s.deleteJobTemplate(self.job_template)

    def terminate(self):
        self.s.control(self.job_id, JobControlAction.TERMINATE)

    def get_state(self):
        return self.s.jobStatus(self.job_id)

class DRMAABackend(Backend):
    '''
    A very simply backend for job submission using DRMAA.
    '''

    jobs = {}

    terminate_action = Action()
    terminate_category = Category()
    terminate_category.term = 'terminate'
    terminate_category.scheme = 'http://example.com/occi/drmaa'
    terminate_category.attributes = []
    terminate_category.title = 'Terminates a job'
    terminate_category.related = [Action.category]
    terminate_action.kind = terminate_category

    kind = Kind()
    kind.actions = [terminate_action]
    kind.attributes = ['remote_command', 'args']
    kind.location = '/jobs/'
    kind.related = [Resource.category]
    kind.scheme = 'http://example.com/occi/drmaa'
    kind.title = 'A simple DRMAA job.'
    kind.term = 'job'

    def create(self, entity):
        if not 'remote_command' in entity.attributes and not 'args' in entity.attributes:
            raise AttributeError('There needs to be an remote_command and args attributes.')
        entity.actions = [self.terminate_action]
        # create job...
        command = entity.attributes['remote_command']
        args = entity.attributes['args'].split(' ')

        job = DRMAAJob(command, args)
        entity.attributes['job_id'] = job.job_id

        self.jobs[job.job_id] = job

    def retrieve(self, entity):
        # update job status
        if not 'job_id' in entity.attributes:
            raise AttributeError('Something is wrong here'
                                             + ' running job resource'
                                             + ' should have an id.')
        job = self.jobs[entity.attributes['job_id']]
        try:
            state = job.get_state()
            entity.attributes['job_state'] = state
            if state == 'running':
                action = Action()
                action.categories = [self.terminate_category]
                # drop old links - when running cannot change links!
                entity.action = [action]
            if state == 'done' or state == 'failed':
                entity.actions = []
        except InvalidJobException:
            entity.actions = []

    def update(self, old, new):
        pass

    def delete(self, entity):
        if not 'job_id' in entity.attributes:
            raise AttributeError('Something is wrong here'
                                             + ' running job resource'
                                             + ' should have an id.')
        job = self.jobs[entity.attributes['job_id']]
        state = job.get_state()
        if state != 'done' and state != 'failed':
            job.terminate()
        del self.jobs[entity.attributes['job_id']]

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == self.terminate_category:
            # terminate job
            self.retrieve(entity)
            try:
                job = self.jobs[entity.attributes['job_id']]
            except:
                raise AttributeError('Trying to run an action on non active resource.')
            job.terminate()
            entity.actions = []
        else:
            raise AttributeError('Non existing action called!')
