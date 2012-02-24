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
Module which incorporates the WSGI integration.

Created on 22.11.2011

@author: tmetsch

'''

from occi import VERSION
from occi.backend import KindBackend, MixinBackend, ActionBackend
from occi.exceptions import HTTPError
from occi.handlers import QUERY_STRING
from occi.handlers import QueryHandler, CollectionHandler, ResourceHandler, \
    CATEGORY, LINK, ATTRIBUTE, LOCATION, ACCEPT, CONTENT_TYPE
from occi.protocol.html_rendering import HTMLRendering
from occi.protocol.json_rendering import JsonRendering
from occi.protocol.occi_rendering import TextOcciRendering, \
    TextPlainRendering, TextUriListRendering
from occi.registry import NonePersistentRegistry
import StringIO
import logging


RETURN_CODES = {201: '201 Created',
                200: '200 OK',
                400: '400 Bad Request',
                403: '403 Forbidden',
                404: '404 Not Found',
                405: '405 Method Not Allowed',
                406: '406 Not Acceptable',
                500: '500 Internal Server Error',
                501: '501 Not implemented'}


def _parse_headers(environ):
    '''
    Will parse the HTTP Headers and only return those who are needed for
    the OCCI service.

    Also translates the WSGI notion of the Header field names to those used
    by OCCI.

    environ -- The WSGI environ
    '''
    headers = {}

    if 'HTTP_CATEGORY'in environ.keys():
        headers[CATEGORY] = environ['HTTP_CATEGORY']
    if 'HTTP_LINK'in environ.keys():
        headers[LINK] = environ['HTTP_LINK']
    if 'HTTP_X_OCCI_ATTRIBUTE'in environ.keys():
        headers[ATTRIBUTE] = environ['HTTP_X_OCCI_ATTRIBUTE']
    if 'HTTP_X_OCCI_LOCATION'in environ.keys():
        headers[LOCATION] = environ['HTTP_X_OCCI_LOCATION']
    if 'HTTP_ACCEPT' in environ.keys():
        headers[ACCEPT] = environ.get('HTTP_ACCEPT')
    if 'CONTENT_TYPE' in environ.keys():
        headers[CONTENT_TYPE] = environ.get('CONTENT_TYPE')
    if 'QUERY_STRING' in environ.keys():
        headers[QUERY_STRING] = environ.get('QUERY_STRING')

    return headers


def _parse_body(environ):
    '''
    Parse the body from the WSGI environ.

    environ -- The WSGI environ.
    '''
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
        return StringIO.StringIO(environ['wsgi_input'].read(length))
    except (KeyError, ValueError):
        return ''


def _parse_query(environ):
    '''
    Parse the query from the WSGI environ.

    environ -- The WSGI environ.
    '''
    tmp = environ.get('QUERY_STRING')
    if tmp is not None:
        try:
            query = (tmp.split('=')[0], tmp.split('=')[1])
        except IndexError:
            query = ()
    else:
        query = ()
    return query


def _set_hostname(environ, registry):
    '''
    Set the hostname of the service.

    environ -- The WSGI environ.
    registry -- The OCCI registry.
    '''
    # set hostname
    if 'HTTP_HOST' in environ.keys():
        registry.set_hostname('http://' + environ['HTTP_HOST'])
    else:
        # WSGI - could be that HTTP_HOST is not available...
        host = 'http://' + environ.get('SERVER_NAME') + ':'
        host += environ.get('SERVER_PORT')
        registry.set_hostname(host)


class Application(object):
    '''
    An WSGI application for OCCI.
    '''

    # disabling 'Too few public methods' pylint check (given by WSGI)
    # pylint: disable=R0903

    def __init__(self, registry=None, renderings=None):
        # set default registry
        if registry is None:
            self.registry = NonePersistentRegistry()
        else:
            self.registry = registry

        # set default renderings
        if renderings is None:
            self.registry.set_renderer('text/occi',
                                       TextOcciRendering(self.registry))
            self.registry.set_renderer('text/plain',
                                       TextPlainRendering(self.registry))
            self.registry.set_renderer('text/uri-list',
                                       TextUriListRendering(self.registry))
            self.registry.set_renderer('text/html',
                                       HTMLRendering(self.registry))
            self.registry.set_renderer('application/x-www-form-urlencoded',
                                       HTMLRendering(self.registry))
            self.registry.set_renderer('application/occi+json',
                                       JsonRendering(self.registry))
        else:
            for mime_type in renderings.keys():
                self.registry.set_renderer(mime_type, renderings[mime_type])

    def register_backend(self, category, backend):
        '''
        Register a backend.

        Verifies that correct 'parent' backends are used.

        category -- The category the backend defines.
        backend -- The backend which handles the given category.
        '''
        allow = False
        if repr(category) == 'kind' and isinstance(backend, KindBackend):
            allow = True
        elif repr(category) == 'mixin' and isinstance(backend, MixinBackend):
            allow = True
        elif repr(category) == 'action' and isinstance(backend, ActionBackend):
            allow = True

        if allow:
            self.registry.set_backend(category, backend)
        else:
            raise AttributeError('Backends handling kinds need to derive' \
                                 ' from KindBackend; Backends handling' \
                                 ' actions need to derive from' \
                                 ' ActionBackend and backends handling' \
                                 ' mixins need to derive from MixinBackend.')

    def _call_occi(self, environ, response, **kwargs):
        '''
        Starts the overall OCCI part of the service. Needs to be called by the
        __call__ function defined by an WSGI app.

        environ -- The WSGI environ.
        response -- The WESGI response.
        kwargs -- keyworded arguments which will be forwarded to the backends.
        '''
        extras = kwargs.copy()

        # parse
        heads = _parse_headers(environ)

        # parse body...
        body = _parse_body(environ)

        # parse query
        query = _parse_query(environ)

        _set_hostname(environ, self.registry)

        # find right handler
        handler = None
        if environ['PATH_INFO'] == '/-/':
            handler = QueryHandler(self.registry, heads, body, query, extras)
        elif environ['PATH_INFO'] == '/.well-known/org/ogf/occi/-/':
            handler = QueryHandler(self.registry, heads, body, query, extras)
        elif environ['PATH_INFO'].endswith('/'):
            handler = CollectionHandler(self.registry, heads, body, query,
                                        extras)
        else:
            handler = ResourceHandler(self.registry, heads, body, query,
                                      extras)

        # call handler
        mtd = environ['REQUEST_METHOD']
        try:
            key = environ['PATH_INFO']
            status, headers, body = handler.handle(mtd, key)
            del(handler)
        except HTTPError as err:
            status = err.code
            headers = {CONTENT_TYPE: 'text/plain'}
            body = err.message
            logging.error(body)

        # send
        headers['Server'] = VERSION
        headers['Content-length'] = str(len(body))

        code = RETURN_CODES[status]

        # headers.items() because we need a list of sets...
        response(code, headers.items())
        return [body, ]

    def __call__(self, environ, response):
        '''
        Will be called as defined by WSGI.

        environ -- The environ.
        response -- The response.
        '''
        return self._call_occi(environ, response)
