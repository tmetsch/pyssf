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
from occi.backend import ActionBackend, KindBackend, MixinBackend
from occi.extensions.infrastructure import COMPUTE, IPNETWORKINTERFACE, START
from occi.protocol.html_rendering import HTMLRendering
from occi.protocol.occi_rendering import TextOcciRendering, \
    TextUriListRendering, TextPlainRendering
from occi.registry import NonePersistentRegistry
from occi.wsgi import Application
import unittest
import wsgiref
'''
Test for the wsgi module.

Created on Nov 24, 2011

@author: tmetsch
'''


class MockResponse(object):

    def __call__(self, stat, heads):
        pass


class ApplicationTest(unittest.TestCase):
    '''
    Tests for the WSGI application.
    '''

    def test_instanciation_for_sanity(self):
        '''
        Tests the constructor.
        '''
        app = Application()
        self.assertTrue(isinstance(app.registry.get_renderer('text/occi'),
                                   TextOcciRendering))
        self.assertTrue(isinstance(app.registry.get_renderer('text/plain'),
                                   TextPlainRendering))
        self.assertTrue(isinstance(app.registry.get_renderer('text/uri-list'),
                                   TextUriListRendering))
        self.assertTrue(isinstance(app.registry.get_renderer('text/html'),
                                   HTMLRendering))

        # other registry
        my_registry = NonePersistentRegistry()
        app2 = Application(registry=my_registry)
        self.assertEqual(app2.registry, my_registry)

        # different rendering
        rendering = HTMLRendering(my_registry)
        app3 = Application(renderings={'text/bla': rendering})
        self.assertEqual(app3.registry.get_renderer('text/bla'), rendering)

    def test_register_backend_for_failure(self):
        '''
        Test registration.
        '''
        app = Application()
        back = ActionBackend()
        self.assertRaises(AttributeError, app.register_backend, COMPUTE, back)

    def test_register_backend_for_sanity(self):
        '''
        Test registration.
        '''
        app = Application()
        back = KindBackend()
        back1 = MixinBackend()
        back2 = ActionBackend()

        app.register_backend(COMPUTE, back)
        app.register_backend(IPNETWORKINTERFACE, back1)
        app.register_backend(START, back2)

        self.assertTrue(app.registry.get_backend(COMPUTE) == back)
        self.assertTrue(app.registry.get_backend(IPNETWORKINTERFACE) == back1)
        self.assertTrue(app.registry.get_backend(START) == back2)

    def test_call_for_sanity(self):
        '''
        Test the call function.
        '''
        app = Application()

        response = MockResponse()
        environ = {
                   'SERVER_NAME': 'foo',
                   'SERVER_PORT': '8888',
                   'PATH_INFO': '/-/',
                   'REQUEST_METHOD': 'GET',
                   'QUERY_STRING': 'action=start',
                   'CONTENT_TYPE': 'text/plain',
                   'HTTP_ACCEPT': '*/*',
                   'HTTP_LINK': '*/*',
                   'HTTP_CATEGORY': '*/*',
                   'HTTP_X_OCCI_ATTRIBUTE': '*/*',
                   'HTTP_X_OCCI_LOCATION': '*/*'
                   }
        app.__call__(environ, response)

        environ.pop('QUERY_STRING')
        environ['PATH_INFO'] = '/'
        app.__call__(environ, response)

        environ['PATH_INFO'] = '/.well-known/org/ogf/occi/-/'
        environ['HTTP_HOST'] = 'localhost:9888'
        app.__call__(environ, response)

        environ['PATH_INFO'] = '/foo'
        app.__call__(environ, response)
