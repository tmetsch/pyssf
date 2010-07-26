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
from resource_model import JobResource, Link

#def check_resource_type(func):
#    def wrapper(*args):
#        if isinstance(args[1], JobResource):
#            print 'OK - calling', func.__name__ , 'with', args[1]
#            return func(*args)
#        else:
#            print 'NO - calling', func.__name__ , 'with', args[1]
#            raise AttributeError('not a job resource')
#    return wrapper

class Handler(object):

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
        """
        # trigger action & update state/attributes
        raise NotImplementedError

    def _action_is_in_resource_description(self, resource, action):
        """
        Tests whether an given action is indeed currently defined by a link in
        a resource.
        
        resource -- the resource.
        action -- the action to test.
        """
        links = resource.get_action_links()
        for item in links:
            if item.target.split(';')[-1:].pop() == str(action):
                return True
        return False

class JobHandler(Handler):
    """
    Job Handler is in charge of updating the states/link of a job resource. It
    ensures that the state model is not broken. Class whichh handle the
    management of the Jobs in DRMs should derive from this class.
    """

    jobs = {}

    # @check_resource_type
    def create(self, resource):
        if isinstance(resource, JobResource):
            if not 'occi.drmaa.remote_command' in resource.attributes:
                raise AttributeError('Missing command argument')

            command = resource.attributes['occi.drmaa.remote_command']
            if 'occi.drmaa.args' in resource.attributes:
                args = resource.attributes['occi.drmaa.args'].split(' ')
            else:
                args = None
            job = JobFactory().create_job(command, args)

            # update links & attributes
            link = Link()
            link.link_class = 'action'
            link.rel = 'http://purl.org/occi/drmaa/action#terminate'
            link.target = '/' + resource.id + ';terminate'
            link.title = 'Terminate Job'
            # I can append because not action links could be added previously
            # because parsers take care of that...
            resource.links.append(link)
            resource.attributes['occi.drmaa.job_id'] = job.job_id

            self.jobs[job.job_id] = job
        else:
            pass

    def retrieve(self, resource):
        if isinstance(resource, JobResource):
            if not 'occi.drmaa.job_id' in resource.attributes:
                raise AttributeError('Something is wrong here - running job '
                                     + 'resource should have an id.')
            job = self.jobs[resource.attributes['occi.drmaa.job_id']]
            state = job.get_state()
            resource.attributes['occi.drmaa.job_state'] = state
            if state == 'running':
                link = Link()
                link.link_class = 'action'
                link.rel = 'http://purl.org/occi/drmaa/action#terminate'
                link.target = '/' + resource.id + ';terminate'
                link.title = 'Terminate Job'
                # drop old links - when running cannot change links!
                resource.links = [link]
            if state == 'done' or state == 'failed':
                resource.links = []
        else:
            pass

    def update(self, resource):
        # not allowing the update :-D
        pass

    def delete(self, resource):
        if isinstance(resource, JobResource):
            if not 'occi.drmaa.job_id' in resource.attributes:
                raise AttributeError('Something is wrong here - running job '
                                     + 'resource should have an id.')
            job = self.jobs[resource.attributes['occi.drmaa.job_id']]
            state = job.get_state()
            if state != 'done' and state != 'failed':
                job.terminate()
            del self.jobs[resource.attributes['occi.drmaa.job_id']]
        else:
            pass

    def action(self, resource, action):
        if isinstance(resource, JobResource):
            # update attributes and links if needed and trigger action
            if self._action_is_in_resource_description(resource, action):
                try:
                    job = self.jobs[resource.attributes['occi.drmaa.job_id']]
                except:
                    raise AttributeError('Trying to run an action on non'
                                         + 'active resource.')
                if action == 'terminate':
                    job.terminate()
                    resource.links = []
                resource.attributes['occi.drmaa.job_state'] = job.get_state()
            else:
                raise AttributeError('Non existing action called!')
        else:
            pass
