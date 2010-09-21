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
This example shows how to use the pyrest package to create a RESTful interface
to submit jobs to a cluster using DRMAAv1. It has been tested with Platform
LSF and Sun/Oracle Grid Engine.

It demonstrates the following pyrest features:

  - Binding DRMAA to a RESTful OCCI compliant interface
  - RESTifying an existing application
  - Writing a backend for the pyrest service
  - Using the build-in web server to demo the service

It does NOT make use of the following features:

  - SSL or X509 certificate support
  - deployment with mod_wsgi inside of Apache
  - Security
  - Links
  - Update Verb

Created on Sep 20, 2010

@author: tmetsch
'''
from pydrmaa.job import JobFactory

from pyrest import backends
from pyrest.backends import Handler
from pyrest.myexceptions import MissingAttributesException, StateException, MissingActionException
from pyrest.resource_model import Category, Resource, Action
from pyrest.service import ResourceHandler

import web

# create a backend
class JobHandler(Handler):
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
        Registers the categories this backend can handle.
        """
        backends.register([self.category, self.terminate_category], self)

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

    def update(self, resource, updated_resource):
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

# setup the service
urls = ('/(.*)', 'ResourceHandler')
web.config.debug = False

# register the backend
JobHandler()

# create the app...
application = web.application(urls, globals())

# run...
if __name__ == "__main__":
    application.run()

