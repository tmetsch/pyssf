# 
# Copyright (C) 2010 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
A simple module for demonstration purposes.

Created on Nov 10, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci import registry
from pyocci.rendering_parsers import TextPlainRendering, TextHeaderRendering, \
    TextHTMLRendering
from pyocci.service import ResourceHandler, ListHandler, QueryHandler
from pyocci.examples.occi_drmaa import DRMAABackend
import tornado.httpserver
import tornado.web

class MyService():
    '''
    A simple example of how to use the pyocci WSGI compliant module.
    '''

    application = None

    def __init__(self):
        self.application = tornado.web.Application([
            (r"/-/", QueryHandler),
            (r"/(.*)/", ListHandler),
            (r"(.*)", ResourceHandler),
        ])
        #, **settings

    def start(self):
        '''
        Start a OCCI comliant service.
        '''
        http_server = tornado.httpserver.HTTPServer(self.application)
        http_server.listen(8080)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    # register parsers
    registry.register_parser(TextPlainRendering.content_type,
                                       TextPlainRendering())
    registry.register_parser(TextHeaderRendering.content_type,
                                       TextHeaderRendering())
    HTML_RENDERER = TextHTMLRendering()
    registry.register_parser(TextHTMLRendering.content_type,
                                       HTML_RENDERER)
    registry.register_parser('application/x-www-form-urlencoded', HTML_RENDERER)

    # register a simple key value backend
    registry.register_backend([DRMAABackend.kind,
                               DRMAABackend.terminate_category],
                              DRMAABackend())
    SERVICE = MyService()
    SERVICE.start()
    print 'hello'
