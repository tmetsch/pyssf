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
A simple key value backend.

Created on Nov 25, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.backends import Backend
from pyocci.core import Action, Kind, Resource, Link, Category
from pyocci.service import LinkBackend

class KeyValueBackend(Backend):
    '''
    A simple class which functions as a demo to show the capabilities of this
    package.
    '''

    terminate_action = Action()
    terminate_category = Category()
    terminate_category.term = 'flip'
    terminate_category.scheme = 'http://example.com/occi/keyvalue'
    terminate_category.attributes = ['foo', 'bar']
    terminate_category.title = 'Flips the key and the value'
    terminate_action.kind = terminate_category

    kind = Kind()
    kind.actions = [terminate_action]
    kind.attributes = ['key', 'value']
    kind.location = '/keyvalues/'
    kind.related = [Resource.category]
    kind.scheme = 'http://example.com/occi/keyvalue'
    kind.title = 'A Resource which holds a Key and a Value'
    kind.term = 'keyvalue'

    def create(self, entity):
        if not 'key' in entity.attributes and not 'value' in entity.attributes:
            raise AttributeError('There needs to be an key and value'
                                 + ' attributes.')
        entity.actions = [self.terminate_action]

    def retrieve(self, entity):
        pass

    def update(self, old, new):
        if 'key' in new.attributes.keys():
            old.attributes['key'] = new.attributes['key']
        if 'value' in new.attributes.keys():
            old.attributes['value'] = new.attributes['value']
        if new.summary is not '':
            old.summary = new.summary

    def delete(self, entity):
        pass

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == self.terminate_category:
            tmp = entity.attributes['key']
            entity.attributes['key'] = entity.attributes['value']
            entity.attributes['value'] = tmp
            entity.actions = []

class KeyValueLink(LinkBackend):
    '''
    A simple link between two key value resources.
    '''

    kind = Kind()
    kind.attributes = ['source', 'target']
    kind.location = '/keyvalues/links/'
    kind.related = [Link.category]
    kind.scheme = 'http://example.com/occi/keyvalue'
    kind.title = 'A link between two Key Value Resources'
    kind.term = 'keyvaluelink'
