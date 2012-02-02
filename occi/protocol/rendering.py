#
# Copyright (C) 2010-2012 Platform Computing
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
A empty rendering class.

Created on Feb 2, 2012

@author: tmetsch
'''


class Rendering(object):
    '''
    All renderings should derive from this class.
    '''

    def __init__(self, registry):
        '''
        Constructor.

        registry -- The registry used for this process.
        '''
        self.registry = registry

    def to_entity(self, headers, body, def_kind):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an entity representation. Must return Resource or Link
        instances.

        headers -- The HTTP headers.
        body -- The HTTP body.
        def_kind -- If provided this kind is taken (Needed for update).
        '''
        raise NotImplementedError()

    def from_entity(self, entity):
        '''
        Given an entity it will return a HTTP body an header.

        If it's a link make sure source, target attributes are set. If it's a
        Resource make sure Links are presented properly.

        entity -- The entity which is to rendered.
        '''
        raise NotImplementedError()

    def to_entities(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into a set of entity representations. Must return a set of
        Resource or Link instances.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

    def from_entities(self, entities, key):
        '''
        Given an set of entities it will return a HTTP body an header.

        entities -- The entities which will be rendered.
        key -- Needed for uri-list (see RFC) and html rendering.
        '''
        raise NotImplementedError()

    def from_categories(self, categories):
        '''
        Given an set of categories it will return a HTTP body an header.

        categories -- The list of categories which is to be rendered.
        '''
        raise NotImplementedError()

    def to_action(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an Action.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

    def to_mixins(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into a Mixins. Must return a list with Mixin instances.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()

    def get_filters(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into a list of categories and attributes.

        headers -- The HTTP headers.
        body -- The HTTP body.
        '''
        raise NotImplementedError()
