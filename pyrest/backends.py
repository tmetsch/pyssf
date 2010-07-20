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
from resource_model import JobResource, Link
from job import JobFactory, Job

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
        
        resource -- the new resource.
        """
        # add links to resource
        raise NotImplementedError

    def update(self, resource):
        """
        An update on the resource has occurred - map it to the backend.
        
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
        pass

    def action(self, resource, action):
        """
        An action was called upon an resource - handle it.
        
        resource -- the resource.
        """
        # trigger action & update state/attributes
        pass

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

    scheme = ''

    # @check_resource_type
    def create(self, resource):
        if isinstance(resource, JobResource):
            link = Link()
            link.link_class = 'action'
            link.rel = 'http://purl.org/occi/job/action#kill'
            link.target = '/' + resource.id + ';kill'
            link.title = 'Kill Job'
            resource.links.append(link)
        else:
            pass

    def action(self, resource, action):
        if isinstance(resource, JobResource):
            # update attributes and links if needed and trigger action
            if self._action_is_in_resource_description(resource, action):
                resource.links = []
                resource.attributes = {'occi.drmaa.state': 'killed'}
            else:
                raise AttributeError('Non existing action called!')
        else:
            pass
