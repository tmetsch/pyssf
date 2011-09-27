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
Module which holds a abstract registry definition class and one simple
implementation.

Created on Aug 22, 2011

@author: tmetsch
'''

# disabling 'Abstract class only ref. once' pylint check (designed for ext.)
# pylint: disable=R0922

from occi.backend import KindBackend, ActionBackend, MixinBackend
from occi.protocol.occi_rendering import Rendering
from tornado.web import HTTPError


class Registry(object):
    '''
    Abstract class so users can implement registries themselves.
    '''

    hostname = ''

    default_mime_type = 'text/plain'

    def get_hostname(self):
        '''
        Returns the hostname of the service.
        '''
        return self.hostname

    def set_hostname(self, hostname):
        '''
        Set the hostname of the service.
        '''
        self.hostname = hostname

    def get_default_type(self):
        '''
        Returns the default mime type.
        '''
        return self.default_mime_type

    def get_renderer(self, mime_type):
        '''
        Retrieve a rendering for a given mime type.

        mime_type -- The mime type you a looking for.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def set_renderer(self, mime_type, renderer):
        '''
        Retrieve a rendering for a given mime type.

        mime_type -- The mime type you want to add a rendering for.
        renderer -- Instance of an Rendering class.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_backend(self, category):
        """
        Retrieve a backend which is able to deal with the given category.

        category -- The category a backend is needed for.
        """
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_all_backends(self, entity):
        """
        Retrieve all backends associated with a resource instance

        entity -- The resource instance.
        """
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def set_backend(self, category, backend):
        """
        Set a backend which is able to deal with the given category.

        category -- The category a backend is needed for.
        backend -- The backend which should handle this category.
        """
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def delete_mixin(self, mixin):
        '''
        Remove a mixin from the service.

        mixin -- The mixin
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_category(self, path):
        '''
        Return the category which is associated with an Location.

        path -- The location which the category should define.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_categories(self):
        '''
        Return all registered categories.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_resource(self, key):
        '''
        Return a certain resource.

        key -- Unique identifier of the resource.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def add_resource(self, key, entity):
        '''
        Add a resource.

        key -- the unique identifier.
        entity -- the OCCI representation.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def delete_resource(self, key):
        '''
        Delete a resource.

        key -- Unique identifier of the resource.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_resource_keys(self):
        '''
        Return all keys of all resources.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_resources(self):
        '''
        Return all resources.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')


class NonePersistentRegistry(Registry):
    '''
    None optimized/persistent registry for the OCCI service.

    It is encouraged to write an own registry with e.g. DB lookups.

    Created on Jun 28, 2011

    @author: tmetsch
    '''

    BACKENDS2 = {}

    RENDERINGS2 = {}

    RESOURCES2 = {}

    HOST2 = ''

    def get_renderer(self, mime_type):
        parser = None

        for tmp in mime_type.split(','):
            type_str = tmp.strip()
            if type_str.find(';q=') > -1:
                type_str = type_str[:type_str.find(';q=')]

            if type_str in self.RENDERINGS2:
                parser = self.RENDERINGS2[type_str]
                break
            elif type_str == '*/*':
                parser = self.RENDERINGS2[self.get_default_type()]
                break

        if parser is None:
            raise HTTPError(406, 'This service is unable to understand the ' +
                            ' mime type: ' + repr(mime_type))
        else:
            return parser

    def set_renderer(self, mime_type, renderer):
        if not isinstance(renderer, Rendering):
            raise AttributeError('renderer needs to derive from Rendering.')

        self.RENDERINGS2[mime_type] = renderer

    def get_backend(self, category):
        # need to lookup because category should not have __hash__ func.
        for re_cat in self.BACKENDS2.keys():
            if category == re_cat:
                back = self.BACKENDS2[re_cat]
                if repr(re_cat) == 'kind' and isinstance(back, KindBackend):
                    return back
                if repr(re_cat) == 'action' and isinstance(back,
                                                           ActionBackend):
                    return back
                if repr(re_cat) == 'mixin' and isinstance(back, MixinBackend):
                    return back
        raise AttributeError('Cannot find corresponding Backend.')

    def get_all_backends(self, entity):
        res = []
        res.append(self.get_backend(entity.kind))
        for mixin in entity.mixins:
            res.append(self.get_backend(mixin))
        return res

    def set_backend(self, category, backend):
        self.BACKENDS2[category] = backend

    def delete_mixin(self, mixin):
        self.BACKENDS2.pop(mixin)

    def get_category(self, path):
        for category in self.BACKENDS2.keys():
            if category.location == path:
                return category
        return None

    def get_categories(self):
        return self.BACKENDS2.keys()

    def get_resource(self, key):
        return self.RESOURCES2[key]

    def add_resource(self, key, resource):
        self.RESOURCES2[key] = resource

    def delete_resource(self, key):
        self.RESOURCES2.pop(key)

    def get_resource_keys(self):
        return self.RESOURCES2.keys()

    def get_resources(self):
        return self.RESOURCES2.values()
