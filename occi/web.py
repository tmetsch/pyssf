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
The web handling part of the OCCI service.

Created on Jun 27, 2011

@author: tmetsch
'''

# disabling 'Arguments number differs' pylint check (1st argument is the key)
# disabling 'Too many public methods' pylint check (tornado's fault)
# pylint: disable=W0221, R0904

from occi import VERSION, workflow
from occi.registry import NonePersistentRegistry
from tornado.web import HTTPError
import sys
import tornado.web

CONTENT_TYPE = 'Content-Type'

ACCEPT = 'Accept'


class BaseHandler(tornado.web.RequestHandler):
    '''
    General request handler.
    '''

    def initialize(self, registry):
        self.registry = registry
        if self.registry.get_hostname() == '':
            self.registry.set_hostname(self.request.protocol + '://' +
                                       self.request.host)

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        # This ensures that at least one registry is loaded in case initialize
        # is not called for some reason...
        self.registry = NonePersistentRegistry()

        if self.registry.get_hostname() == '':
            self.registry.set_hostname(self.request.protocol + '://' +
                                       self.request.host)

    def extract_http_data(self):
        '''
        Extracts all necessary information from the HTTP envelop. Minimize the
        data which is carried around inside of the service. Also ensures that
        the names are always equal - When deployed in Apache the names of the
        Headers change.
        '''
        heads = {}
        headers = self.request.headers
        if 'Category' in headers:
            heads['Category'] = headers['Category']
        if 'X-Occi-Attribute' in headers:
            heads['X-OCCI-Attribute'] = headers['X-Occi-Attribute']
        if 'X-Occi-Location' in headers:
            heads['X-OCCI-Location'] = headers['X-Occi-Location']
        if 'Link' in headers:
            heads['Link'] = headers['Link']
        if self.request.body is not '':
            body = self.request.body.strip()
        else:
            body = ''

        return heads, body

    def get_renderer(self, content_type):
        '''
        Returns the proper rendering parser.

        content_type -- String with either either Content-Type or Accept.
        '''
        try:
            return self.registry.get_renderer(
                                            self.request.headers[content_type])
        except KeyError:
            return self.registry.get_renderer(self.registry.get_default_type())

    def response(self, status, mime_type, headers, body='OK'):
        '''
        Will create a response and send it to the client.

        status -- The status code.
        mime_type -- Sets the Content-Type of the response.
        headers -- The HTTP headers.
        body -- The text for the body (default: ok).
        '''
        self.set_header('Server', VERSION)
        self.set_header('Content-Type', mime_type)
        self.set_status(status)
        if headers is not None:
            for item in headers.keys():
                self._headers[item] = headers[item]
        self.write(body)
        self.finish('\n')

    def get_error_html(self, status_code, **kwargs):
        self.set_header('Server', VERSION)
        self.set_header('Content-Type', self.registry.get_default_type())
        exception = sys.exc_info()[1]
        msg = str(exception)
        self.set_status(status_code)
        return msg

    def parse_action(self):
        '''
        Retrieves the Action which was given in the request.
        '''
        headers, body = self.extract_http_data()
        rendering = self.get_renderer(CONTENT_TYPE)

        action = rendering.to_action(headers, body)

        return action

    def parse_filter(self):
        '''
        Retrieve any attributes or categories which where provided in the
        request for filtering.
        '''
        headers, body = self.extract_http_data()

        attr = 'X-OCCI-Attribute'
        if  attr not in headers and 'Category' not in headers and body == '':
            return [], {}

        rendering = self.get_renderer(CONTENT_TYPE)

        categories, attributes = rendering.get_filters(headers, body)

        return categories, attributes

    def parse_entity(self, def_kind=None):
        '''
        Retrieves the entity which was rendered within the request.

        def_kind -- Indicates if the request can be incomplete (False).
        '''
        headers, body = self.extract_http_data()
        rendering = self.get_renderer(CONTENT_TYPE)

        entity = rendering.to_entity(headers, body, def_kind)

        return entity

    def parse_entities(self):
        '''
        Retrieves a set of entities which was rendered within the request.
        '''
        headers, body = self.extract_http_data()
        rendering = self.get_renderer(CONTENT_TYPE)

        entities = rendering.to_entities(headers, body)

        return entities

    def parse_mixins(self):
        '''
        Retrieves a mixin from a request.
        '''
        headers, body = self.extract_http_data()
        rendering = self.get_renderer(CONTENT_TYPE)

        mixin = rendering.to_mixins(headers, body)

        return mixin

    def render_entity(self, entity):
        '''
        Renders a single entity to the client.

        entity -- The entity which should be rendered.
        '''
        rendering = self.get_renderer(ACCEPT)

        headers, body = rendering.from_entity(entity)

        self.response(200, rendering.mime_type, headers, body)

    def render_entities(self, entities, key):
        '''
        Renders a list of entities to the client.

        entities -- The entities which should be rendered.
        '''
        rendering = self.get_renderer(ACCEPT)

        headers, body = rendering.from_entities(entities, key)

        self.response(200, rendering.mime_type, headers, body)

    def render_categories(self, categories):
        '''
        Renders a list of categories to the client.

        categories -- The categories which should be rendered.
        '''
        rendering = self.get_renderer(ACCEPT)

        headers, body = rendering.from_categories(categories)

        self.response(200, rendering.mime_type, headers, body)


class ResourceHandler(BaseHandler):
    '''
    Handles the request on single resource instances.
    '''

    def get(self, key):
        try:
            entity = self.registry.get_resource(key)

            workflow.retrieve_entity(entity, self.registry)

            self.render_entity(entity)
        except KeyError as key:
            raise HTTPError(404, str(key))

    def post(self, key):
        if len(self.get_arguments('action')) > 0:
            # action
            try:
                entity = self.registry.get_resource(key)
                action = self.parse_action()

                workflow.action_entity(entity, action, self.registry)

                self.render_entity(entity)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
            except KeyError as key:
                raise HTTPError(404, str(key))
        else:
            # update
            try:
                old = self.registry.get_resource(key)
                new = self.parse_entity(def_kind=old.kind)

                workflow.update_entity(old, new, self.registry)

                self.render_entity(old)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
            except KeyError as key:
                raise HTTPError(404, str(key))

    def put(self, key):
        if key in self.registry.get_resource_keys():
            # replace...
            try:
                old = self.registry.get_resource(key)
                new = self.parse_entity()

                workflow.replace_entity(old, new, self.registry)

                self.render_entity(old)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
        else:
            # create...
            try:
                entity = self.parse_entity()

                workflow.create_entity(key, entity, self.registry)

                self.response(201, self.registry.get_default_type(),
                              {'Location': self.request.protocol
                                           + '://' + self.request.host + key})
            except AttributeError as attr:
                raise HTTPError(400, str(attr))

    def delete(self, key):
        # delete
        try:
            entity = self.registry.get_resource(key)

            workflow.delete_entity(entity, self.registry)

            self.response(200, self.registry.get_default_type(), None)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))
        except KeyError as key:
            raise HTTPError(404, str(key))


class CollectionHandler(BaseHandler):
    '''
    Handles all operations on collections.
    '''

    def get(self, key):
        # retrieve (filter)
        try:
            if key == '' or key[-1] != '/':
                key += '/'

            categories, attributes = self.parse_filter()
            entities = workflow.get_entities_under_path(key, self.registry)
            result = workflow.filter_entities(entities, categories, attributes)

            self.render_entities(result, key)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def post(self, key):
        if key == '' or key[-1] != '/':
            key += '/'
        if len(self.get_arguments('action')) > 0:
            # action
            try:
                action = self.parse_action()
                entities = workflow.get_entities_under_path(key, self.registry)
                for entity in entities:
                    workflow.action_entity(entity, action, self.registry)

                self.response(200, self.registry.get_default_type(), None)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
        elif len(self.parse_entities()) == 0:
            # create resource (&links)
            try:
                entity = self.parse_entity()

                workflow.create_entity(workflow.create_id(entity.kind),
                                       entity, self.registry)

                self.response(201, self.registry.get_default_type(),
                              {'Location': self.request.protocol
                                           + '://' + self.request.host
                                           + entity.identifier})
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
        elif len(self.parse_entities()) > 0:
            # update
            try:
                mixin = self.registry.get_category(key)
                new_entities = self.parse_entities()
                old_entities = workflow.get_entities_under_path(key,
                                                                self.registry)
                workflow.update_collection(mixin, old_entities,
                                           new_entities,
                                           self.registry)

                self.response(200, self.registry.get_default_type(), None)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))

    def put(self, key):
        # replace
        try:
            if key == '' or key[-1] != '/':
                key += '/'
            mixin = self.registry.get_category(key)
            new_entities = self.parse_entities()
            old_entities = workflow.get_entities_under_path(key, self.registry)
            workflow.replace_collection(mixin, old_entities, new_entities,
                                        self.registry)

            self.response(200, self.registry.get_default_type(), None)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def delete(self, key):
        if key == '' or key[-1] != '/':
            key += '/'
        if len(self.parse_entities()) == 0:
            # delete entities
            entities = workflow.get_entities_under_path(key, self.registry)
            for entity in entities:
                workflow.delete_entity(entity, self.registry)

            self.response(200, self.registry.get_default_type(), None)
        elif len(self.parse_entities()) > 0:
            # remove from collection
            try:
                mixin = self.registry.get_category(key)
                entities = self.parse_entities()
                workflow.delete_from_collection(mixin, entities, self.registry)

                self.response(200, self.registry.get_default_type(), None)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))


class QueryHandler(BaseHandler):
    '''
    Handles the Query interface.
    '''

    # disabling 'Unused attr' pylint check (not needed here)
    # pylint: disable=W0612

    def get(self):
        # retrieve (filter)
        try:
            categories, attributes = self.parse_filter()

            result = workflow.filter_categories(categories, self.registry)

            self.render_categories(result)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def post(self):
        # add user-defined mixin
        try:
            mixins = self.parse_mixins()

            workflow.append_mixins(mixins, self.registry)

            self.render_categories(mixins)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def delete(self):
        # delete user defined mixin
        try:
            categories, attributes = self.parse_filter()

            workflow.remove_mixins(categories, self.registry)

            self.response(200, self.registry.get_default_type(), None)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))
