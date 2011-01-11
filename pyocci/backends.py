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
This module holds a simple set of basic backends which are needed to operate on
the OCCI model.

Created on Nov 11, 2010

@author: tmetsch
'''

class Backend(object):
    '''
    Backends are the integration point between the service and the resource
    management framework (aka your application). The following methods therefore
    need to be implemented. Backends can not only be defined for Kinds and their
    resource instances, but also for Mixins. Doing this Mixins can be used as
    templates.
    '''

    def create(self, entity):
        '''
        Create a resource in the resource management layer.
        
        @param entity: A complete entity representation in the OCCI framework.
        @type entity: Entity
        '''
        raise NotImplementedError('Backend does not implement create'
                                  + ' operation')

    def retrieve(self, entity):
        '''
        Retrieve a resource in the resource management layer. This is used to
        update the entity representation before it is send to the client.
        
        @param entity: A complete entity representation in the OCCI framework.
        @type entity: Entity
        '''
        raise NotImplementedError('Backend does not implement retrieve'
                                  + ' operation')

    def update(self, old_entity, new_entity):
        '''
        Update a resource in the resource management layer. The backends should
        decide which information is passed from the new representation to the
        old one.
        
        @param old_entity: A entity representation in the OCCI framework.
        @type old_entity: Entity
        @param new_entity: A entity representation in the OCCI framework.
        @type new_entity: Entity
        '''
        raise NotImplementedError('Backend does not implement update'
                                  + ' operation')

    def delete(self, entity):
        '''
        Delete a resource in the resource management layer. This is used to
        delete the entity representation in the underlying application.
        
        @param entity: A entity representation in the OCCI framework.
        @type entity: Entity
        '''
        raise NotImplementedError('Backend does not implement delete'
                                  + ' operation')

    def action(self, entity, action):
        '''
        Perform an action on an resource or link.
        
        @param entity: The resource or link the action should be performed on.
        @type entity: Entity
        @param action: Action which should be performed
        @type action: Action
        '''
        raise NotImplementedError('Backend does not implement action'
                                  + ' operation')
