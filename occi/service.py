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
Use this class to create your own OCCI compatible service.

Created on Jul 19, 2011

@author: tmetsch
'''

from occi import registry
from occi.backend import KindBackend, ActionBackend, MixinBackend
from occi.protocol.html_rendering import HTMLRendering
from occi.protocol.occi_rendering import TextOcciRendering, \
    TextPlainRendering, TextUriListRendering
from occi.web import QueryHandler, CollectionHandler, ResourceHandler
import tornado.httpserver


class OCCI(object):
    '''
    A OCCI compatible service.
    '''

    # disabling 'Method could be func' pylint check (this is for extension)
    # pylint: disable=R0201

    def __init__(self):

        registry.RENDERINGS['text/occi'] = TextOcciRendering()
        registry.RENDERINGS['text/plain'] = TextPlainRendering()
        registry.RENDERINGS['text/uri-list'] = TextUriListRendering()
        registry.RENDERINGS['text/html'] = HTMLRendering()

        application = tornado.web.Application([
                (r"/-/", QueryHandler),
                (r"/.well-known/org/ogf/occi/-/", QueryHandler),
                (r"(.*)/", CollectionHandler),
                (r"(.*)", ResourceHandler),
            ])

        self.http_server = tornado.httpserver.HTTPServer(application)

    def register_backend(self, category, backend):
        '''
        Register a backend.

        Verifies that correct 'parent' backends are used.

        @param category: The category the backend defines.
        @param backend: The backend which handles the given category.
        '''
        allow = False
        if repr(category) == 'kind' and isinstance(backend, KindBackend):
            allow = True
        elif repr(category) == 'mixin' and isinstance(backend, MixinBackend):
            allow = True
        elif repr(category) == 'action' and isinstance(backend, ActionBackend):
            allow = True

        if allow:
            registry.BACKENDS[category] = backend
        else:
            raise AttributeError('Backends handling kinds need to derive' \
                                 ' from KindBackend; Backends handling' \
                                 ' actions need to derive from' \
                                 ' ActionBackend and backends handling' \
                                 ' mixins need to derive from MixinBackend.')

    def start(self, port):
        '''
        Start the service.
        '''
        self.http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
