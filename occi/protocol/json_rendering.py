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
JSON based rendering.

Created on 01.02.2012

@author: tmetsch
'''

# L8R: check if this can be move partly to occi_rendering (once standardized)
# and rename to a parser class.

# disabling 'Method is abstract' pylint check (currently only support GETs!)
# pylint: disable=W0223

from occi.core_model import Resource
from occi.handlers import CONTENT_TYPE
from occi.protocol.rendering import Rendering
import json


def _from_category(category):
    '''
    Create a JSON struct for a category.
    '''
    data = {}
    data['term'] = category.term
    data['scheme'] = category.scheme
    if hasattr(category, 'title') and category.title is not '':
        data['title'] = category.title
    if hasattr(category, 'related') and len(category.related) > 0:
        rel_list = []
        for item in category.related:
            rel_list.append(str(item))
        data['related'] = rel_list
    if hasattr(category, 'location') and category.location is not None:
        data['location'] = category.location
    if hasattr(category, 'attributes') and len(category.attributes) >= 1:
        attr_list = {}
        for item in category.attributes:
            if category.attributes[item] == 'required':
                attr_list[item] = 'required'
            elif category.attributes[item] == 'immutable':
                attr_list[item] = 'immutable'
            else:
                attr_list[item] = 'muttable'
        data['attributes'] = attr_list
    if hasattr(category, 'actions') and len(category.actions) > 0:
        action_list = []
        for item in category.actions:
            action_list.append(str(item))
        data['actions'] = action_list
    return data


def _from_entity(entity):
    '''
    Create a JSON struct for an entity.
    '''
    data = {}
    # kind
    data['kind'] = _from_category(entity.kind)

    # mixins
    mixins = []
    for mixin in entity.mixins:
        tmp = _from_category(mixin)
        mixins.append(tmp)
    data['mixins'] = mixins

    # actions
    actions = []
    for action in entity.actions:
        tmp = {}
        tmp['kind'] = _from_category(action)
        tmp['link'] = entity.identifier + '?action=' + action.term
        actions.append(tmp)
    data['actions'] = actions

    # links
    if isinstance(entity, Resource):
        links = []
        for link in entity.links:
            tmp = _from_entity(link)
            tmp['source'] = link.source.identifier
            tmp['target'] = link.target.identifier
            links.append(tmp)
        data['links'] = links

    # attributes
    attr = {}
    for attribute in entity.attributes:
        attr[attribute] = entity.attributes[attribute]
    data['attributes'] = attr

    return data


class JsonRendering(Rendering):
    '''
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'application/occi+json'

    def from_entity(self, entity):
        data = _from_entity(entity)

        body = json.dumps(data, sort_keys=True, indent=2)
        return {CONTENT_TYPE: self.mime_type}, body

    def from_entities(self, entities, key):
        data = []
        for item in entities:
            data.append(_from_entity(item))

        body = json.dumps(data, sort_keys=True, indent=2)
        return {CONTENT_TYPE: self.mime_type}, body

    def from_categories(self, categories):
        data = []
        for item in categories:
            data.append(_from_category(item))

        body = json.dumps(data, sort_keys=True, indent=2)
        return {CONTENT_TYPE: self.mime_type}, body
