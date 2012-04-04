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
# disabling 'Unsued argument' pylint check (is there to be overwritten)
# disabling 'Method could be function' pylint check (see above)
# pylint: disable=R0922,W0613,R0201

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

    def get_backend(self, category, extras):
        """
        Retrieve a backend which is able to deal with the given category.

        category -- The category a backend is needed for.
        extras -- Extras object - same as the one passed on to the backends.
        """
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_all_backends(self, entity, extras):
        """
        Retrieve all backends associated with a resource instance

        entity -- The resource instance.
        extras -- Extras object - same as the one passed on to the backends.
        """
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def set_backend(self, category, backend, extras):
        """
        Set a backend which is able to deal with the given category.

        category -- The category a backend is needed for.
        backend -- The backend which should handle this category.
        extras -- Extras object - same as the one passed on to the backends.
        """
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def delete_mixin(self, mixin, extras):
        '''
        Remove a mixin from the service.

        mixin -- The mixin
        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_category(self, path, extras):
        '''
        Return the category which is associated with an Location.

        path -- The location which the category should define.
        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_categories(self, extras):
        '''
        Return all registered categories.

        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_resource(self, key, extras):
        '''
        Return a certain resource.

        key -- Unique identifier of the resource.
        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def add_resource(self, key, entity, extras):
        '''
        Add a resource.

        key -- the unique identifier.
        entity -- the OCCI representation.
        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def delete_resource(self, key, extras):
        '''
        Delete a resource.

        key -- Unique identifier of the resource.
        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_resource_keys(self, extras):
        '''
        Return all keys of all resources.

        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_resources(self, extras):
        '''
        Return all resources.

        extras -- Extras object - same as the one passed on to the backends.
        '''
        raise NotImplementedError('Registry implementation seems to be' \
                                  ' incomplete.')

    def get_extras(self, extras):
        '''
        Will return what goes into the extras attribute of the entity and
        category.
        '''
        return None


class NonePersistentRegistry(Registry):
    '''
    None optimized/persistent registry for the OCCI service.

    It is encouraged to write an own registry with e.g. DB lookups.

    Created on Jun 28, 2011

    @author: tmetsch
    '''

    def __init__(self):
        self.backends = {}
        self.renderings = {}
        self.resources = {}
        self.host = ''
        super(NonePersistentRegistry, self).__init__()

    def get_renderer(self, mime_type):
        parser = None

        for tmp in mime_type.split(','):
            type_str = tmp.strip()
            if type_str.find(';q=') > -1:
                type_str = type_str[:type_str.find(';q=')]

            if type_str in self.renderings:
                parser = self.renderings[type_str]
                break
            elif type_str == '*/*':
                parser = self.renderings[self.get_default_type()]
                break

        if parser is None:
            raise HTTPError(406, 'This service is unable to understand the ' +
                            ' mime type: ' + repr(mime_type))
        else:
            return parser

    def set_renderer(self, mime_type, renderer):
        if not isinstance(renderer, Rendering):
            raise AttributeError('renderer needs to derive from Rendering.')
        self.renderings[mime_type] = renderer

    def get_backend(self, category, extras):
        # no need to check - a get_categories or get_categroy will be called
        # first.
        try:
            back = self.backends[category]
            if repr(category) == 'kind' and isinstance(back, KindBackend):
                return back
            if repr(category) == 'action' and isinstance(back,
                                                       ActionBackend):
                return back
            if repr(category) == 'mixin' and isinstance(back, MixinBackend):
                return back
        except KeyError:
            raise AttributeError('Cannot find corresponding Backend.')

    def get_all_backends(self, entity, extras):
        res = []
        res.append(self.get_backend(entity.kind, extras))
        for mixin in entity.mixins:
            res.append(self.get_backend(mixin, extras))
        # remove duplicates - only need to call backs once - right?
        return list(set(res))

    def set_backend(self, category, backend, extras):
        if extras is not None:
            # category belongs to single user...
            category.extras = self.get_extras(extras)
        self.backends[category] = backend

    def delete_mixin(self, mixin, extras):
        # no need to check because in get_category in renderer it is assured
        # that the user only sees own. Will get not found if he tries to delete
        # mixin from other user.
        self.backends.pop(mixin)

    def get_category(self, path, extras):
        # no need for ownership check - paths cannot overlap!
        for category in self.backends.keys():
            if category.location == path:
                return category
        return None

    def get_categories(self, extras):
        result = []
        for item in self.backends.keys():
            if item.extras == None:
                # categories visible to all!
                result.append(item)
            elif extras is not None and self.get_extras(extras) == item.extras:
                # categories visible to this user!
                result.append(item)
        return result

    def get_resource(self, key, extras):
        if self.resources[key].extras != self.get_extras(extras):
            raise KeyError
        return self.resources[key]

    def add_resource(self, key, resource, extras):
        if extras is not None:
            resource.extras = self.get_extras(extras)
        self.resources[key] = resource

    def delete_resource(self, key, extras):
        # get_resources and get_resource is called before this - no need for
        # ownership checking.
        self.resources.pop(key)

    def get_resource_keys(self, extras):
        result = []
        for key in self.resources.keys():
            if self.resources[key].extras is None:
                result.append(key)
            elif self.resources[key].extras is not None and \
                 self.resources[key].extras == self.get_extras(extras):
                result.append(key)
        return result

    def get_resources(self, extras):
        result = []
        for item in self.resources.values():
            if item.extras is None:
                result.append(item)
            elif item.extras is not None and \
                 item.extras == self.get_extras(extras):
                result.append(item)
        return result
