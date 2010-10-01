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
This module contains the basic classes for backend development.

Created on Jul 9, 2010

@author: tmetsch
'''

REGISTERED_BACKENDS = {}

def register(categories, handler):
    """
    Register a job handler for the service - the categories the handler
    can deal with need to be specified.
    
    If two handlers can deal with the same categories - the more recent
    registered one is taken!
    
    categories -- list of categories (for resource, links and actions).
    handler -- the handler. 
    """
    if not isinstance(handler, Handler):
        raise AttributeError("Second argument needs to derive from Handler"
                           + " class.")
    else:
        for category in categories:
            if REGISTERED_BACKENDS.has_key(category):
                raise AttributeError("A handler for this category is already"
                                   + "registered.")
            else:
                REGISTERED_BACKENDS[category] = handler

def find_right_backend(categories):
    """
    Retrieve a backend which is able to deal with the first given category.
    
    categories -- The category a backend is needed for.
    """
    for re_cat in REGISTERED_BACKENDS.keys():
        for category in categories:
            if category == re_cat:
                return REGISTERED_BACKENDS[re_cat]
    return Handler()

class Handler(object):
    """
    A backend should support the routines described below. It triggers actions
    and is in charge of dealing/manipulating/maintaining the data of the
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
        raise NotImplementedError("No backend implemented.")

    def update(self, resource, updated_resource):
        """
        An update on the resource has occurred - map it to the backend.
        NOTE: Within this method assure the mutability of links, attributes and
        categories!
        
        resource -- the original resource
        updated_resource -- the updated resource
        """
        # update attributes
        raise NotImplementedError("No backend implemented.")

    def retrieve(self, resource):
        """
        A get was called - return new values if needed.
        
        resource -- the resource which wants to be updated.
        """
        # return updated attributes & links
        raise NotImplementedError("No backend implemented.")

    def delete(self, resource):
        """
        Also delete the resource in the backend
        
        resource -- the resource which should be deleted.
        """
        # update attributes & cleanup
        raise NotImplementedError("No backend implemented.")

    def action(self, resource, action):
        """
        An action was called upon an resource - handle it.
        
        resource -- the resource.
        action -- the desired action.
        """
        # trigger action & update state/attributes
        raise NotImplementedError("No backend implemented.")
