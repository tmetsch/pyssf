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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
A simple module for demonstration purposes.

Created on Nov 10, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci import registry, service
from pyocci.examples.occi_drmaa import DRMAABackend
from pyocci.rendering_parsers import TextPlainRendering, TextHeaderRendering, \
    TextHTMLRendering, URIListRendering
from pyocci.service import ResourceHandler, CollectionHandler, QueryHandler, \
    LoginHandler, LogoutHandler
import tornado.httpserver
import tornado.web

class Login(LoginHandler):

    def authenticate(self, user, password):
        if user == 'foo' and password == 'bar':
            return True
        elif user == 'foo2' and password == 'bar':
            return True
        else:
            return False

class MyService():
    '''
    A simple example of how to use the pyocci WSGI compliant module.
    '''

    application = None

    service.AUTHENTICATION = True

    def __init__(self):
        settings = {
                    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
                    "login_url": "/login",
        }
        self.application = tornado.web.Application([
            (r"/-/", QueryHandler),
            (r"/login", Login),
            (r"/logout", LogoutHandler),
            (r"/(.*)/", CollectionHandler),
            (r"(.*)", ResourceHandler),
        ], **settings)

    def start(self):
        '''
        Start a OCCI comliant service.
        '''
        http_server = tornado.httpserver.HTTPServer(self.application)
        http_server.listen(8888)
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
    registry.register_parser(URIListRendering.content_type, URIListRendering())

    # register a simple key value backend
    registry.register_backend([DRMAABackend.kind,
                               DRMAABackend.terminate_category],
                              DRMAABackend())
    SERVICE = MyService()
    SERVICE.start()
    print 'hello'
