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
The OCCI service.

Created on Jun 27, 2011

@author: tmetsch
'''

# disabling 'Arguments number differs' pylint check (1st argument is the key)
# disabling 'Too many public methods' pylint check (tornado's fault)
# pylint: disable=W0221, R0904

from occi import registry, workflow
from tornado.web import HTTPError
import sys
import tornado.web

CONTENT_TYPE = 'Content-Type'


class BaseHandler(tornado.web.RequestHandler):
    '''
    General request handler.
    '''

    version = 'pyssf OCCI 1/1'

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

    def get_parser(self, content_type):
        '''
        Returns the proper rendering parser.

        @param content_type: String with either either Content-Type or Accept.
        '''
        try:
            return registry.get_parser(self.request.headers[content_type])
        except KeyError:
            return registry.get_parser(registry.DEFAULT_MIME_TYPE)

    def response(self, status, mime_type, headers, body='OK'):
        '''
        Will create a response and send it to the client.

        @param status: The status code.
        @param mime_type: Sets the Content-Type of the response.
        @param headers: The HTTP headers.
        @param body: The text for the body (default: ok).
        '''
        self.set_header('Server', self.version)
        self.set_header('Content-Type', mime_type)
        self.set_status(status)
        if headers is not None:
            for item in headers.keys():
                self._headers[item] = headers[item]
        self.write(body)
        #self.finish(body)

    def get_error_html(self, status_code, **kwargs):
        self.set_header('Server', self.version)
        self.set_header('Content-Type', registry.DEFAULT_MIME_TYPE)
        exception = sys.exc_info()[1]
        msg = str(exception)
        self.set_status(status_code)
        return msg


class ResourceHandler(BaseHandler):
    '''
    Handles the request on single resource instances.
    '''

    def get(self, key):
        try:
            entity = registry.RESOURCES[key]

            workflow.retrieve_entity(entity)

            self.parse_outgoing(entity)
        except AttributeError as attr:
            raise HTTPError(406, str(attr))
        except KeyError as key:
            raise HTTPError(404, str(key))

    def post(self, key):
        if len(self.get_arguments('action')) > 0:
            # action
            try:
                entity = registry.RESOURCES[key]
                action = self.parse_action()

                workflow.action_entity(entity, action)
                self.response(200, registry.DEFAULT_MIME_TYPE, None)
            except AttributeError as attr:
                raise HTTPError(406, str(attr))
            except KeyError as key:
                raise HTTPError(404, str(key))
        else:
            # update
            try:
                old = registry.RESOURCES[key]
                new = self.parse_incoming()

                workflow.update_entity(old, new)

                self.response(200, registry.DEFAULT_MIME_TYPE, None)
            except AttributeError as attr:
                raise HTTPError(406, str(attr))
            except KeyError as key:
                raise HTTPError(404, str(key))

    def put(self, key):
        if key in registry.RESOURCES.keys():
            # replace...
            try:
                old = registry.RESOURCES[key]
                new = self.parse_incoming()

                workflow.replace_entity(old, new)

                self.response(200, registry.DEFAULT_MIME_TYPE, None)
            except AttributeError as attr:
                raise HTTPError(406, str(attr))
        else:
            # create...
            try:
                entity = self.parse_incoming()

                workflow.create_entity(key, entity)

                self.response(201, registry.DEFAULT_MIME_TYPE,
                              {'Location': self.request.protocol
                                           + '://' + self.request.host + key})
            except AttributeError as attr:
                raise HTTPError(406, str(attr))

    def delete(self, key):
        # delete
        try:
            entity = registry.RESOURCES[key]

            workflow.delete_entity(entity)

            self.response(200, registry.DEFAULT_MIME_TYPE, None)
        except AttributeError as attr:
            raise HTTPError(406, str(attr))
        except KeyError as key:
            raise HTTPError(404, str(key))

    def parse_incoming(self):
        '''
        Returns the entity which was rendered within the request.
        '''
        headers, body = self.extract_http_data()
        parser = self.get_parser(CONTENT_TYPE)

        entity = parser.to_entity(headers, body)

        return entity

    def parse_outgoing(self, entity):
        '''
        Renders an entity to the client.

        @param entity: The entity which should be rendered.
        '''
        parser = self.get_parser('Accept')

        headers, body = parser.from_entity(entity)

        self.response(200, parser.mime_type, headers, body)

    def parse_action(self):
        '''
        Returns the Action which was given in the request.
        '''
        headers, body = self.extract_http_data()
        parser = self.get_parser(CONTENT_TYPE)

        action = parser.to_action(headers, body)

        return action


class CollectionHandler(BaseHandler):
    '''
    Handles all operations on collections.
    '''

    def get(self, key):
        # retrieve (filter)
        entities = workflow.get_entities_under_path(key)
        result = workflow.filter_entities(entities, None, None)
        self.parse_outgoing(result, key)

    def post(self, key):
        # action
        # create resource (&links)
        # update
        pass

    def put(self, key):
        # replace
        pass

    def delete(self, key):
        # delete
        pass

    def parse_outgoing(self, resource_list, key):
        '''
        Renders a list of entities to the client.

        @param resource_list: The entities which should be rendered.
        '''
        parser = self.get_parser('Accept')

        headers, body = parser.from_entities(resource_list, key)

        self.response(200, parser.mime_type, headers, body)


class QueryHandler(BaseHandler):
    '''
    Handles the Query interface.
    '''

    def get(self):
        # retrieve (filter)
        pass

    def post(self):
        # add user-defined mixin
        pass

    def delete(self):
        # delete user defined mixin
        pass
