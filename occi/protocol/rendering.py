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
Actual mime-type renderings.

Created on Jun 28, 2011

@author: tmetsch
'''

from occi import registry
from occi.core_model import Resource, Link
import parser


class HTTPData(object):
    '''
    Simple class which functions as an adapter between the OCCI model and the
    HTTP rendering. Holds all information in the way an entity is rendered.
    '''

    # disabling 'Too few public methods' pylint check (just a data model)
    # pylint: disable=R0903

    def __init__(self):
        self.categories = []
        self.links = []
        self.attributes = []
        self.locations = []


class Rendering(object):
    '''
    All renderings should derive from this class.
    '''

    def to_entity(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an entity representation. Must return Resource or Link
        instances.

        @param headers: The HTTP headers.
        @param body: The HTTP body.
        '''
        raise NotImplementedError()

    def from_entity(self, entity):
        '''
        Given an entity it will return a HTTP body an header.

        @param entity: The entity which is to rendered.
        '''
        raise NotImplementedError()

    def to_action(self, headers, body):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an Action.

        @param headers: The HTTP headers.
        @param body: The HTTP body.
        '''
        raise NotImplementedError()

#==============================================================================
# text/occi rendering
#==============================================================================


class TextOcciRendering(Rendering):
    '''
    This is a rendering which will use the HTTP body to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'text/occi'

    def extract_data(self, headers):
        '''
        Simple method to split out the information from the HTTP headers.

        @param headers: The HTTP headers.
        '''
        # split out the information
        data = HTTPData()
        if 'Category' in headers.keys():
            data.categories = headers['Category'].split(',')
        if 'X-OCCI-Attribute' in headers.keys():
            data.attributes = headers['X-OCCI-Attribute'].split(',')
        if 'X-OCCI-Location' in headers.keys():
            data.locations = headers['X-OCCI-Location'].split(',')
        if 'Link' in headers.keys():
            data.links = headers['Link'].split(',')
        return data

    def to_entity(self, headers, body):
        data = self.extract_data(headers)

        kind = None
        mixins = []

        # first kind & mixins
        kind_found = False
        for category_string in data.categories:
            category = parser.get_category(category_string.strip())
            if repr(category) == 'kind' and not kind_found:
                kind = category
                kind_found = True
            else:
                mixins.append(category)

        # the attributes
        attributes = {}
        for attr_string in data.attributes:
            key, value = parser.get_attributes(attr_string)
            attributes[key] = value

        # now create the entity
        if kind_found is False:
            raise AttributeError('Could not find a valid kind.')

        if Resource.kind in kind.related:
            # links
            entity = Resource(None, kind, mixins, links=[])
            for link_string in data.links:
                entity.links.append(parser.get_link(link_string.strip(),
                                                    entity))
        elif Link.kind in kind.related:
            try:
                source = registry.RESOURCES[attributes['occi.core.source']]
                target = registry.RESOURCES[attributes['occi.core.target']]
            except KeyError:
                raise AttributeError('Both occi.core.[source, target]'
                                     + ' attributes need to be resources.')
            entity = Link(None, kind, mixins, source, target)
            source.links.append(entity)
        else:
            raise AttributeError('This kind seems not to be related to either'
                                 + ' resource or link.')

        entity.attributes = attributes
        return entity

    def from_entity(self, entity):
        headers = {}

        # categories
        cat_str_list = []
        cat_str_list.append(parser.get_category_str(entity.kind))

        for category in entity.mixins:
            cat_str_list.append(parser.get_category_str(category))

        headers['Category'] = ', '.join(cat_str_list)

        attributes = []
        entity.attributes['occi.core.id'] = entity.identifier

        link_str_list = []
        # actions
        for action in entity.actions:
            act = '<' + entity.identifier + '?action=' + action.term + '>'
            act = act + '; rel="' + str(action) + '"'
            link_str_list.append(act)

        # links
        if isinstance(entity, Resource):
            # links
            for link in entity.links:
                link_str_list.append(parser.get_link_str(link))

        elif isinstance(entity, Link):
            entity.attributes['occi.core.source'] = entity.source.identifier
            entity.attributes['occi.core.target'] = entity.target.identifier

        headers['Link'] = ', '.join(link_str_list)

        # attributes
        for attribute in entity.attributes:
            attributes.append(attribute + '="'
                              + entity.attributes[attribute] + '"')

        headers['X-OCCI-Attribute'] = ', '.join(attributes)

        return headers, 'OK'

    def to_action(self, headers, body):
        data = self.extract_data(headers)

        action = parser.get_category(data.categories[0].strip())

        return action
