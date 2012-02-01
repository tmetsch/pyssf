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
JSON based rendering.

Created on 01.02.2012

@author: tmetsch
'''

from occi.handlers import CONTENT_TYPE
from occi.protocol.occi_rendering import Rendering
import json


def _from_category(category):
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
    if hasattr(category, 'attributes') and len(category.attributes) > 0:
        attr_list = []
        for item in category.attributes:
            if category.attributes[item] == 'required':
                attr_list.append(item + '{required}')
            elif category.attributes[item] == 'immutable':
                attr_list.append(item + '{immutable}')
            else:
                attr_list.append(item)
        data['attributes'] = attr_list
    if hasattr(category, 'actions') and len(category.actions) > 0:
        action_list = []
        for item in category.actions:
            action_list.append(str(item))
        data['actions'] = action_list
    return data

class JsonRendering(Rendering):
    '''
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'application/occi+json'

    def from_entity(self, entity):
        data = {}
        # kind
        data['kind'] = _from_category(entity.kind)

        # mixins
        mixins = []
        for mixin in entity.mixins:
            tmp = {}
            tmp['term'] = mixin.term
            tmp['scheme'] = mixin.scheme
            mixins.append(tmp)
        data['mixins'] = mixins

        # actions
        actions = []
        for action in entity.actions:
            tmp = {}
            tmp['term'] = action.term
            tmp['scheme'] = action.scheme
            actions.append(tmp)
        data['actions'] = actions

        # links
        links = []
        for link in entity.links:
            tmp = {}
            tmp['source'] = link.source
            tmp['target'] = link.target
            tmp['category'] = str(link.kind)
        data['links'] = links

        # attributes
        attr = {}
        print entity.attributes
        for attribute in entity.attributes:
            attr[attribute] = entity.attributes[attribute]
        data['attributes'] = attr

        # , sort_keys=True
        body = json.dumps(data, indent=2)
        return {CONTENT_TYPE: self.mime_type}, body
