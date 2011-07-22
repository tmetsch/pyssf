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

XXX: Would be cool to improve with so lookup loops get minimized.

Created on Jun 28, 2011

@author: tmetsch
'''

from occi.backend import KindBackend, ActionBackend, MixinBackend
from tornado.web import HTTPError

BACKENDS = {}

RENDERINGS = {}

RESOURCES = {}

DEFAULT_MIME_TYPE = 'text/plain'

HOST = ''


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
    # need to lookup because category should not have __hash__ func.
    for re_cat in BACKENDS.keys():
        if category == re_cat:
            back = BACKENDS[re_cat]
            if repr(re_cat) == 'kind' and isinstance(back, KindBackend):
                return back
            elif repr(re_cat) == 'action' and isinstance(back, ActionBackend):
                return back
            if repr(re_cat) == 'mixin' and isinstance(back, MixinBackend):
                return back
    raise AttributeError('Cannot find corresponding Backend.')


def get_category(path):
    '''
    Return the category which is associated with an Location.

    @param path: The location which the category should define.
    '''
    for category in BACKENDS.keys():
        if category.location == path:
            return category
    return None


def get_renderer(mime_type):
    '''
    Retrieve a rendering for a given mime type.

    @param mime_type: The mime type you a looking for.
    '''
    parser = None

    for tmp in mime_type.split(','):
        type_str = tmp.strip()
        if type_str.find(';q=') > -1:
            # XXX: dropping those ;q=x.x values...
            type_str = type_str[:type_str.find(';q=')]

        if type_str in RENDERINGS:
            parser = RENDERINGS[type_str]
            break
        elif type_str == '*/*':
            parser = RENDERINGS[DEFAULT_MIME_TYPE]
            break

    if parser is None:
        raise HTTPError(406, 'This service is unable to understand the mime' +
                        ' type: ' + repr(mime_type))
    else:
        return parser
