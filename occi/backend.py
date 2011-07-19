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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
Backends should derive from this class.

Created on Jun 27, 2011

@author: tmetsch
'''

# TODO: add routine to check that link rel and target.kind match...
# TODO: add routine to check for mutability of attributes...
# TODO: add routine to check if action is applicable...
# TODO: add routine to automatically register a backend...
# TODO: add routine to create OCCI compatible service...


class Backend(object):
    '''
    A prototype backend which essentially does nothing. Backends are only
    needed for resources. So even when a link is updated the according backends
    are called. It can happen that an entity has more than one backend assigned
    (this is the case when it has a couple of mixins). But you can assign
    multiple kinds to one backend.
    '''

    def create(self, entity):
        '''
        Call the Resource Management and create this entity.

        @param entity: The entity which is to be created.
        '''
        pass

    def retrieve(self, entity):
        '''
        Call the Resource Management and refresh this entity so the client gets
        up to date information.

        @param entity: The entity which is to be retrieved.
        '''
        pass

    def update(self, old, new):
        '''
        Call the Resource Management and update this entity.

        It is up to the backend implementation to decide which information from
        new if copied into old.

        @param old: The old entity which is to be updated.
        @param new: The new entity holding the updated information.
        '''
        pass

    def replace(self, old, new):
        '''
        Call the Resource Management and update this entity. This is
        essentially a full update (Which allows removal of attribtues for
        example).

        It is up to the backend implementation to decide which information from
        new if copied into old. So if you really want to replace old with new
        you need to have an old = new somewhere here.

        @param old: The old entity which is to be updated.
        @param new: The new entity holding the updated information.
        '''
        pass

    def delete(self, entity):
        '''
        Call the Resource Management and delete this entity.

        @param entity: The entity which is to be deleted.
        '''
        pass

    def action(self, entity, action):
        '''
        Call the Resource Management and perform this action.

        @param entity: The entity on which the action is going to be performed.
        @param action: The action category definition.
        '''
        pass
