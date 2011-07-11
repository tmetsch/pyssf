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

# TODO: remove this one:
# pylint: disable=W0223

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

    def from_entities(self, entity, key):
        '''
        Given an set of entities it will return a HTTP body an header.

        @param entity: The entity which is to rendered.
        @param key: Needed for uri-list (see RFC) and html rendering.
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


def _extract_data_from_headers(headers):
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
#        if 'X-OCCI-Location' in headers.keys():
#            data.locations = headers['X-OCCI-Location'].split(',')
    if 'Link' in headers.keys():
        data.links = headers['Link'].split(',')
    return data


def _set_data_to_headers(data):
    '''
    Simple method to set all information in the HTTP header.

    @param data: The data to set.
    '''
    headers = {}
    body = 'OK'

    headers['Category'] = ', '.join(data.categories)
    headers['Link'] = ', '.join(data.links)
    headers['Attributes'] = ', '.join(data.attributes)

    return headers, body


def _to_entity(data):
    '''
    Extract an entity from the HTTP data object.
    '''
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
        entity = Resource(None, kind, mixins, [])
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
    else:
        raise AttributeError('This kind seems not to be related to either'
                             + ' resource or link.')

    entity.attributes = attributes
    return entity


def _from_entity(entity):
    '''
    Create a HTTP data object from an entity.
    '''
    data = HTTPData()

    # categories
    cat_str_list = []
    cat_str_list.append(parser.get_category_str(entity.kind))

    for category in entity.mixins:
        cat_str_list.append(parser.get_category_str(category))

    data.categories = cat_str_list

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

    data.links = link_str_list

    # attributes
    for attribute in entity.attributes:
        attributes.append(attribute + '="'
                          + entity.attributes[attribute] + '"')

    data.attributes = attributes

    return data


def _to_action(data):
    '''
    Create an action from an HTTP data object.
    '''
    action = parser.get_category(data.categories[0].strip())

    return action


class TextOcciRendering(Rendering):
    '''
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'text/occi'

    def to_entity(self, headers, body):
        data = _extract_data_from_headers(headers)
        entity = _to_entity(data)
        return entity

    def from_entity(self, entity):
        data = _from_entity(entity)
        headers, body = _set_data_to_headers(data)
        return headers, body

    def to_action(self, headers, body):
        data = _extract_data_from_headers(headers)
        action = _to_action(data)
        return action


class TextPlainRendering(Rendering):
    '''
    This is a rendering which will use the HTTP body to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'text/plain'


class HTMLRendering(Rendering):
    '''
    A simple HTML website rendering for monitoring the service...
    '''

    mime_type = 'text/html'

    css = "body { \
            font-family: sans-serif; \
            font-size: 0.9em; \
            margin: 0; \
            padding: 0; \
           } \
           #header { \
            background: #444; \
            border-top: 5px solid #73c167; \
           }  \
           #header ul { \
            list-style-type: none; \
            list-style-image: none; \
            margin: 0; \
            padding: 0; \
            height: 2em; \
           } \
           #header li { \
            margin: 0.3em 0.5em 0.3em 0.5em; \
            font-weight: bold; \
            display: inline-block; \
           } \
           #header li a { \
            padding: 0.3em; \
            text-decoration: none; \
            color: #fff; \
           } \
           #header li a:hover { \
            background: #73c167;\
            border-bottom: 2px solid #73c167; \
           } \
           #breadcrumb { \
            background: #efefea; \
            padding: 1em; \
            border-bottom: 1px solid #888; \
           } \
           a { \
            color: #73c167; \
           } \
           #entity { \
            margin: 1em; \
           }"

    def from_entity(self, entity):
        tmp = '<html>\n\t<head>\n'
        tmp += '\t\t<title>Resource: ' + entity.identifier + '</title>\n'
        tmp += '\t\t<style type="text/css"><!-- ' + self.css + ' --></style>\n'
        tmp += '\t</head>\n'
        tmp += '\t<body>\n'

        # header
        tmp += '\t\t<div id="header"><ul><li><a href="/">Home</a></li>'
        tmp += '<li><a href="/-/">Query Interface</a></li></ul></div>\n'

        # breadcrumb
        tmp += '\t\t<div id="breadcrumb"><a href="/">&raquo;</a> /'
        path = '/'
        for item in entity.identifier.split('/')[1:-1]:
            path += item + '/'
            tmp += ' <a href="' + path + '">' + item + "</a> / "
        tmp += entity.identifier.split('/')[-1]
        tmp += '</div>\n'

        # body
        tmp += '\t\t<div id="entity">\n'
        tmp += '\t\t\t<strong>Kind</strong>: ' + str(entity.kind) + '\n'
        tmp += '\t\t\t<strong>Mixins</strong>: ' + str(entity.mixins) + '\n'
        tmp += '\t\t\t<strong>Links</strong>: ' + str(entity.links) + '\n'
        tmp += '\t\t\t<strong>Attributes</strong>: '
        tmp += str(entity.attributes) + '\n'
        tmp += '\t\t\t<strong>Actions</strong>: ' + str(entity.actions) + '\n'
        tmp += '\t\t</div>\n'
        tmp += '\t</body>\n</html>'
        return {}, tmp

    def from_entities(self, entities, key):
        tmp = '<html>\n\t<head>\n'
        tmp += '\t\t<title>' + key + '</title>\n'
        tmp += '\t\t<style type="text/css"><!-- ' + self.css + ' --></style>\n'
        tmp += '\t</head>\n'
        tmp += '\t<body>\n'

        # header
        tmp += '\t\t<div id="header"><ul><li><a href="/">Home</a></li>'
        tmp += '<li><a href="/-/">Query Interface</a></li></ul></div>\n'

        # breadcrumb
        tmp += '\t\t<div id="breadcrumb"><a href="/">&raquo;</a> /'
        path = '/'
        for item in key.split('/')[1:]:
            path += item + '/'
            tmp += ' <a href="' + path + '">' + item + "</a> /"
        tmp += '</div>\n'

        # body
        tmp += '\t\t<div id="entity"><ul>\n'
        if len(entities) == 0:
            tmp += '\t\t\t<li>No resources found</li>\n'
        for item in entities:
            tmp += '\t\t\t<li><a href="' + item.identifier + '">'
            tmp += item.identifier + '</a></li>\n'
        tmp += '\t\t</ul></div>\n'
        tmp += '\t</body>\n</html>'
        return {}, tmp
