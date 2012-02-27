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
Module which holds a abstract registry definition class and one simple
implementation.

Created on Aug 22, 2011

@author: tmetsch
'''

# disabling 'Abstract class only ref. once' pylint check (designed for ext.)
# pylint: disable=R0922

from occi.backend import KindBackend, ActionBackend, MixinBackend
from occi.exceptions import HTTPError
from occi.protocol.occi_rendering import Rendering


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

    BACKENDS = {}

    RENDERINGS = {}

    RESOURCES = {}

    HOST = ''

    def get_renderer(self, mime_type):
        parser = None

        for tmp in mime_type.split(','):
            type_str = tmp.strip()
            if type_str.find(';q=') > -1:
                type_str = type_str[:type_str.find(';q=')]

            if type_str in self.RENDERINGS:
                parser = self.RENDERINGS[type_str]
                break
            elif type_str == '*/*':
                parser = self.RENDERINGS[self.get_default_type()]
                break

        if parser is None:
            raise HTTPError(406, 'This service is unable to understand the ' +
                            ' mime type: ' + repr(mime_type))
        else:
            return parser

    def set_renderer(self, mime_type, renderer):
        if not isinstance(renderer, Rendering):
            raise AttributeError('renderer needs to derive from Rendering.')

        self.RENDERINGS[mime_type] = renderer

    def get_backend(self, category):
        try:
            back = self.BACKENDS[category]
            if repr(category) == 'kind' and isinstance(back, KindBackend):
                return back
            if repr(category) == 'action' and isinstance(back,
                                                       ActionBackend):
                return back
            if repr(category) == 'mixin' and isinstance(back, MixinBackend):
                return back
        except KeyError:
            raise AttributeError('Cannot find corresponding Backend.')

    def get_all_backends(self, entity):
        res = []
        res.append(self.get_backend(entity.kind))
        for mixin in entity.mixins:
            res.append(self.get_backend(mixin))
        # remove duplicates - only need to call backs once - right?
        return list(set(res))

    def set_backend(self, category, backend):
        self.BACKENDS[category] = backend

    def delete_mixin(self, mixin):
        self.BACKENDS.pop(mixin)

    def get_category(self, path):
        for category in self.BACKENDS.keys():
            if category.location == path:
                return category
        return None

    def get_categories(self):
        return self.BACKENDS.keys()

    def get_resource(self, key):
        return self.RESOURCES[key]

    def add_resource(self, key, resource):
        self.RESOURCES[key] = resource

    def delete_resource(self, key):
        self.RESOURCES.pop(key)

    def get_resource_keys(self):
        return self.RESOURCES.keys()

    def get_resources(self):
        return self.RESOURCES.values()
