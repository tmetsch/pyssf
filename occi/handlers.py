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
The web handling part of the OCCI service.

Created on Jun 27, 2011

@author: tmetsch
'''

from occi import workflow
from occi.exceptions import HTTPError

#==============================================================================
# Set of HTTP Header field names - naming is defined by WSGI
#==============================================================================

CONTENT_TYPE = 'Content-Type'
ACCEPT = 'Accept'
LINK = 'Link'
LOCATION = 'X-OCCI-Location'
ATTRIBUTE = 'X-OCCI-Attribute'
CATEGORY = 'Category'
QUERY_STRING = 'Query_String'


class BaseHandler():
    '''
    General request handler.
    '''

    # disabling 'Too many arguments' pylint check (only inst. within module)
    # pylint: disable=R0913

    def __init__(self, registry, headers, body, query, extras=None):
        self.registry = registry
        self.headers = headers
        self.body = body
        self.query = query

        self.extras = extras

    def handle(self, method, key):
        '''
        Call a HTTP method function on this handler. E.g. when method is HTTP
        GET the function get(key) will be called. If the function is not
        defined a 405 is returned.

        method -- The HTTP method name.
        key -- The key of the resource.
        '''
        try:
            return getattr(self, str.lower(method))(key)
        except AttributeError:
            return 405, {'Content-type': 'text/plain'}, 'Method not supported.'

    def get_renderer(self, content_type):
        '''
        Returns the proper rendering parser.

        content_type -- String with either either Content-Type or Accept.
        '''
        try:
            return self.registry.get_renderer(self.headers[content_type])
        except KeyError:
            # In case no Accept is defined in the request
            return self.registry.get_renderer(self.registry.get_default_type())

    def response(self, status, headers=None, body='OK'):
        '''
        Will try to figure out what rendering the client wants and return back
        the given status, header and boy.

        status -- The status code.
        headers -- The HTTP headers (default: empty).
        body -- The text for the body (default: 'ok').
        '''
        rendering = self.get_renderer(ACCEPT)

        if headers is None:
            headers = {}

        headers['Content-Type'] = rendering.mime_type

        return status, headers, body

    def parse_action(self):
        '''
        Retrieves the Action which was given in the request.
        '''
        rendering = self.get_renderer(CONTENT_TYPE)

        action = rendering.to_action(self.headers, self.body)

        return action

    def parse_filter(self):
        '''
        Retrieve any attributes or categories which where provided in the
        request for filtering.
        '''
        attr = ATTRIBUTE
        cat = CATEGORY
        if  attr not in self.headers:
            # stupid pep8 - have to break in two lines :-/
            if cat not in self.headers and self.body == '':
                return [], {}

        rendering = self.get_renderer(CONTENT_TYPE)

        categories, attributes = rendering.get_filters(self.headers, self.body)

        return categories, attributes

    def parse_entity(self, def_kind=None):
        '''
        Retrieves the entity which was rendered within the request.

        def_kind -- Indicates if the request can be incomplete (False).
        '''
        rendering = self.get_renderer(CONTENT_TYPE)

        entity = rendering.to_entity(self.headers, self.body, def_kind)

        return entity

    def parse_entities(self):
        '''
        Retrieves a set of entities which was rendered within the request.
        '''
        rendering = self.get_renderer(CONTENT_TYPE)

        entities = rendering.to_entities(self.headers, self.body)

        return entities

    def parse_mixins(self):
        '''
        Retrieves a mixin from a request.
        '''
        rendering = self.get_renderer(CONTENT_TYPE)

        mixin = rendering.to_mixins(self.headers, self.body)

        return mixin

    def render_entity(self, entity):
        '''
        Renders a single entity to the client.

        entity -- The entity which should be rendered.
        '''
        rendering = self.get_renderer(ACCEPT)

        headers, body = rendering.from_entity(entity)

        return 200, headers, body

    def render_entities(self, entities, key):
        '''
        Renders a list of entities to the client.

        entities -- The entities which should be rendered.
        '''
        rendering = self.get_renderer(ACCEPT)

        headers, body = rendering.from_entities(entities, key)

        return 200, headers, body

    def render_categories(self, categories):
        '''
        Renders a list of categories to the client.

        categories -- The categories which should be rendered.
        '''
        rendering = self.get_renderer(ACCEPT)

        headers, body = rendering.from_categories(categories)

        return 200, headers, body


class ResourceHandler(BaseHandler):
    '''
    Handles the request on single resource instances.
    '''

    def get(self, key):
        '''
        Do a HTTP GET on a resource.

        key -- The resource id.
        '''
        try:
            entity = self.registry.get_resource(key)

            workflow.retrieve_entity(entity, self.registry, self.extras)

            return self.render_entity(entity)
        except KeyError as key_error:
            raise HTTPError(404, 'Resource not found: ' + str(key_error))

    def post(self, key):
        '''
        Do a HTTP POST on a resource.

        key -- The resource id.
        '''
        if self.query is not ():
            # action
            try:
                entity = self.registry.get_resource(key)
                action = self.parse_action()

                workflow.action_entity(entity, action, self.registry,
                                       self.extras)

                return self.render_entity(entity)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
            except KeyError as key_error:
                raise HTTPError(404, str(key_error))
        else:
            # update
            try:
                old = self.registry.get_resource(key)
                new = self.parse_entity(def_kind=old.kind)

                workflow.update_entity(old, new, self.registry, self.extras)

                return self.render_entity(old)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
            except KeyError as key_error:
                raise HTTPError(404, str(key_error))

    def put(self, key):
        '''
        Do a HTTP PUT on a resource.

        key -- The resource id.
        '''
        if key in self.registry.get_resource_keys():
            # replace...
            try:
                old = self.registry.get_resource(key)
                new = self.parse_entity()

                workflow.replace_entity(old, new, self.registry, self.extras)

                return self.render_entity(old)
            except AttributeError as attr:
                raise HTTPError(400, str(key))
        else:
            # create...
            try:
                entity = self.parse_entity()

                workflow.create_entity(key, entity, self.registry, self.extras)

                heads = {'Location': self.registry.get_hostname()
                                           + entity.identifier}
                return self.response(201, heads)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))

    def delete(self, key):
        '''
        Do a HTTP DELETE on a resource.

        key -- The resource id.
        '''
        # delete
        try:
            entity = self.registry.get_resource(key)

            workflow.delete_entity(entity, self.registry, self.extras)

            return self.response(200)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))
        except KeyError as key_error:
            raise HTTPError(404, str(key_error))


class CollectionHandler(BaseHandler):
    '''
    Handles all operations on collections.
    '''

    def get(self, key):
        '''
        Do a HTTP GET on a collection.

        key -- The resource id.
        '''
        # retrieve (filter)
        try:
            categories, attributes = self.parse_filter()
            entities = workflow.get_entities_under_path(key, self.registry)
            result = workflow.filter_entities(entities, categories, attributes)

            return self.render_entities(result, key)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def post(self, key):
        '''
        Do a HTTP POST on a collection.

        key -- The resource id.
        '''
        if self.query is not ():
            # action
            try:
                action = self.parse_action()
                entities = workflow.get_entities_under_path(key, self.registry)
                for entity in entities:
                    workflow.action_entity(entity, action, self.registry,
                                           self.extras)

                return self.response(200)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))
        elif len(self.parse_entities()) == 0:
            # create resource (&links)
            try:
                entity = self.parse_entity()
                workflow.create_entity(workflow.create_id(entity.kind),
                                       entity, self.registry, self.extras)

                heads = {'Location': self.registry.get_hostname()
                                           + entity.identifier}
                return self.response(201, heads)
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
                                           new_entities, self.registry,
                                           self.extras)

                return self.response(200)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))

    def put(self, key):
        '''
        Do a HTTP PUT on a collection.

        key -- The resource id.
        '''
        # replace
        try:
            mixin = self.registry.get_category(key)
            new_entities = self.parse_entities()
            old_entities = workflow.get_entities_under_path(key, self.registry)
            workflow.replace_collection(mixin, old_entities, new_entities,
                                        self.registry, self.extras)

            return self.response(200)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def delete(self, key):
        '''
        Do a HTTP DELETE on a collection.

        key -- The resource id.
        '''
        if len(self.parse_entities()) == 0:
            # delete entities
            entities = workflow.get_entities_under_path(key, self.registry)
            for entity in entities:
                workflow.delete_entity(entity, self.registry, self.extras)

            return self.response(200)
        elif len(self.parse_entities()) > 0:
            # remove from collection
            try:
                mixin = self.registry.get_category(key)
                entities = self.parse_entities()
                workflow.delete_from_collection(mixin, entities, self.registry,
                                                self.extras)

                return self.response(200)
            except AttributeError as attr:
                raise HTTPError(400, str(attr))


class QueryHandler(BaseHandler):
    '''
    Handles the Query interface.
    '''

    # disabling 'Unused attr' pylint check (not needed here)
    # disabling 'Unused argument' pylint check (only here to have one sig)
    # pylint: disable=W0612,W0613

    def get(self, key=None):
        '''
        Do a HTTP GET on the query interface.

        key -- The resource id.
        '''
        # retrieve (filter)
        try:
            categories, attributes = self.parse_filter()

            result = workflow.filter_categories(categories, self.registry)

            return self.render_categories(result)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def post(self, key=None):
        '''
        Do a HTTP POST on the query interface.

        key -- The resource id.
        '''
        # add user-defined mixin
        try:
            mixins = self.parse_mixins()

            workflow.append_mixins(mixins, self.registry)

            return self.render_categories(mixins)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))

    def delete(self, key=None):
        '''
        Do a HTTP DELETE on the query interface.

        key -- The resource id.
        '''
        # delete user defined mixin
        try:
            categories, attributes = self.parse_filter()

            workflow.remove_mixins(categories, self.registry)

            return self.response(200)
        except AttributeError as attr:
            raise HTTPError(400, str(attr))
