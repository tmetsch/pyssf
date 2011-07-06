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
Registry for the OCCI service.

Created on Jun 28, 2011

@author: tmetsch
'''

from occi.backend import Backend

BACKENDS = {}

RENDERINGS = {}

RESOURCES = {}

DEFAULT_MIME_TYPE = 'text/plain'


def get_all_backends(entity):
    """
    Retrieve all backends associated with a resource instance

    entity -- The resource instance.
    """
    res = []
    res.append(get_backend(entity.kind))
    for mixin in entity.mixins:
        res.append(get_backend(mixin))
    return res


def get_backend(category):
    """
    Retrieve a backend which is able to deal with the given category.

    category -- The category a backend is needed for.
    """
    for re_cat in BACKENDS.keys():
        if category == re_cat:
            return BACKENDS[re_cat]
    return Backend()


def get_parser(mime_type):
    '''
    Retrieve a parser for a given mime type.

    @param mime_type: The mime type you a looking for.
    '''
    parser = None
    for tmp in mime_type.split(','):
        type_str = tmp.strip()
        if type_str.find(';q=') > -1:
            # FIXME: dropping those ;q=x.x values...
            type_str = type_str[:type_str.find(';q=')]

        if type_str in RENDERINGS:
            parser = RENDERINGS[type_str]
            break
        elif type_str == '*/*':
            parser = RENDERINGS[DEFAULT_MIME_TYPE]
            break
    if parser is None:
        raise AttributeError('This service is unable to understand the mime'
                             + ' type: ' + repr(mime_type))
    else:
        return parser
