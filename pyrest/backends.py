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
This module contains all backends.

Created on Jul 9, 2010

@author: tmetsch
'''
from pydrmaa.job import JobFactory
from pyrest.myexceptions import MissingActionException, \
    MissingAttributesException, StateException
from pyrest.resource_model import Resource, Category, Action

class Handler(object):
    """
    A backend should support the routines described below. It triggers actions
    and is in charge of dealing/manipulating/maintainig the data of the
    Resources.
    """

    def create(self, resource):
        """
        Do something with the newly created resource.
        NOTE: Within this method assure the mutability of links, attributes and
        categories!
        
        resource -- the new resource.
        """
        # add links to resource
        raise NotImplementedError

    def update(self, resource):
        """
        An update on the resource has occurred - map it to the backend.
        NOTE: Within this method assure the mutability of links, attributes and
        categories!
        
        resource -- the updated resource
        """
        # update attributes
        raise NotImplementedError

    def retrieve(self, resource):
        """
        A get was called - return new values if needed.
        
        resource -- the resource which wants to be updated.
        """
        # return updated attributes & links
        raise NotImplementedError

    def delete(self, resource):
        """
        Also delete the resource in the backend
        
        resource -- the resource which should be deleted.
        """
        # update attributes & cleanup
        raise NotImplementedError

    def action(self, resource, action):
        """
        An action was called upon an resource - handle it.
        
        resource -- the resource.
        action -- the desired action.
        """
        # trigger action & update state/attributes
        raise NotImplementedError

class JobHandler(Handler):
    """
    Job Handler is in charge of updating the states/link of a job resource. It
    ensures that the state model is not broken. Class whichh handle the
    management of the Jobs in DRMs should derive from this class.
    """

    jobs = {}

    category = Category()
    category.attributes = ['occi.drmaa.remote_command', 'occi.drmaa.args',
                           'occi.drmaa.job_id']
    category.related = [Resource.category]
    category.scheme = 'http://schemas.ogf.org/occi/drmaa#'
    category.term = 'job'
    category.title = 'A Job Resource'

    terminate_category = Category()
    terminate_category.related = [Action.category]
    terminate_category.scheme = 'http://schemas.ogf.org/occi/drmaa/action#'
    terminate_category.term = 'terminate'
    terminate_category.title = 'Terminate a Job'

    def __init__(self):
        """
        Registers the category this backend can handle.
        """
        print self.category

    def create(self, resource):
        if self.category in resource.categories:
            if not 'occi.drmaa.remote_command' in resource.attributes:
                raise MissingAttributesException('Missing command argument')

            command = resource.attributes['occi.drmaa.remote_command']
            if 'occi.drmaa.args' in resource.attributes:
                args = resource.attributes['occi.drmaa.args'].split(' ')
            else:
                args = None
            job = JobFactory().create_job(command, args)

            # update links & attributes
            action = Action()
            action.categories = [self.terminate_category]

            # I can append because not action links could be added previously
            # because parsers take care of that...
            resource.actions.append(action)
            resource.attributes['occi.drmaa.job_id'] = job.job_id

            self.jobs[job.job_id] = job
        else:
            pass

    def retrieve(self, resource):
        if self.category in resource.categories:
            if not 'occi.drmaa.job_id' in resource.attributes:
                raise MissingAttributesException('Something is wrong here'
                                                 + ' running job resource'
                                                 + ' should have an id.')
            job = self.jobs[resource.attributes['occi.drmaa.job_id']]
            state = job.get_state()
            resource.attributes['occi.drmaa.job_state'] = state
            if state == 'running':
                action = Action()
                action.categories = [self.terminate_category]
                # drop old links - when running cannot change links!
                resource.action = [action]
            if state == 'done' or state == 'failed':
                resource.actions = []
        else:
            pass

    def update(self, resource):
        # not allowing the update :-D
        pass

    def delete(self, resource):
        if self.category in resource.categories:
            if not 'occi.drmaa.job_id' in resource.attributes:
                raise MissingAttributesException('Something is wrong here'
                                                 + ' running job resource'
                                                 + ' should have an id.')
            job = self.jobs[resource.attributes['occi.drmaa.job_id']]
            state = job.get_state()
            if state != 'done' and state != 'failed':
                job.terminate()
            del self.jobs[resource.attributes['occi.drmaa.job_id']]
        else:
            pass

    def action(self, resource, action):
        if self.category in resource.categories:
            # update attributes and links if needed and trigger action
            # check if action is in current available actions
            if action in resource.actions:
                try:
                    job = self.jobs[resource.attributes['occi.drmaa.job_id']]
                except:
                    raise StateException('Trying to run an action on non'
                                         + 'active resource.')
                # test which action to trigger and run it...
                if self.terminate_category in action.categories:
                    job.terminate()
                    resource.actions = []
                resource.attributes['occi.drmaa.job_state'] = job.get_state()
            else:
                raise MissingActionException('Non existing action called!')
        else:
            pass

