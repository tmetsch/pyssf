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

class JsonRendering(Rendering):
    '''
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    mime_type = 'application/occi+json'

    def from_entity(self, entity):
        data = {}
        # kind
        kind = {}
        kind['term'] = entity.kind.scheme
        kind['scheme'] = entity.kind.scheme
        # TODO: add rest...
        data['kind'] = kind

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
