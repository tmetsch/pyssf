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
Created on Nov 18, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci import registry
from pyocci.core import Resource
from pyocci.examples.keyvalue import KeyValueBackend, Backend
from pyocci.my_exceptions import AlreadyRegisteredException, \
    NoEntryFoundException
from pyocci.rendering_parsers import TextHTMLRendering, TextPlainRendering
from tests import MyMixinBackend
import unittest

class BackendTest(unittest.TestCase):

    def tearDown(self):
        registry.BACKENDS = {}

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_register_backend_for_success(self):
        backend = KeyValueBackend()
        registry.register_backend([KeyValueBackend.kind], backend)

    def test_unregister_backend_for_success(self):
        backend = KeyValueBackend()
        registry.register_backend([KeyValueBackend.kind], backend)
        registry.unregister_backend([KeyValueBackend.kind])

    def test_get_backend_for_success(self):
        self.assertTrue(isinstance(registry.get_backend(None), Backend))

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_register_backend_for_failure(self):
        self.assertRaises(AttributeError, registry.register_backend, None, None)
        self.assertRaises(AttributeError, registry.register_backend, [], None)
        self.assertRaises(AttributeError, registry.register_backend, [KeyValueBackend.kind], None)
        registry.register_backend([KeyValueBackend.kind], KeyValueBackend())
        self.assertRaises(AttributeError, registry.register_backend, [KeyValueBackend.kind], KeyValueBackend())

    def test_unregister_backend_for_failure(self):
        pass

    def test_get_backend_for_failure(self):
        pass

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_register_backend_for_sanity(self):
        backend = KeyValueBackend()
        registry.register_backend([KeyValueBackend.kind], backend)
        self.assertEquals(registry.get_backend(KeyValueBackend.kind), backend)

    def test_unregister_backend_for_sanity(self):
        backend = KeyValueBackend()
        registry.register_backend([KeyValueBackend.kind], backend)
        registry.unregister_backend([KeyValueBackend.kind])
        self.assertTrue(len(registry.BACKENDS) == 0)

    def test_get_all_backends_for_sanity(self):
        backend = KeyValueBackend()
        registry.register_backend([KeyValueBackend.kind], backend)
        second_backend = MyMixinBackend()
        registry.register_backend([MyMixinBackend.category], second_backend)

        entity = Resource()
        entity.kind = KeyValueBackend.kind
        entity.mixins = [MyMixinBackend.category]
        self.assertTrue(len(registry.get_all_backends(entity)), 2)

class RenderingTest(unittest.TestCase):

    def tearDown(self):
        registry.RENDERINGS = {}

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_register_parser_for_success(self):
        registry.register_parser(TextPlainRendering.content_type, TextPlainRendering())

    def test_get_parser_for_success(self):
        registry.register_parser(TextPlainRendering.content_type, TextPlainRendering())
        registry.get_parser('*/*')

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_register_parser_for_failure(self):
        registry.register_parser(TextPlainRendering.content_type, TextPlainRendering())
        self.assertRaises(AlreadyRegisteredException, registry.register_parser, TextPlainRendering.content_type, TextPlainRendering())

    def test_get_parser_for_failure(self):
        self.assertRaises(NoEntryFoundException, registry.get_parser, 'text/xml')

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_get_parser_for_sanity(self):
        parser = TextPlainRendering()
        registry.register_parser(TextPlainRendering.content_type, parser)
        self.assertEquals(registry.get_parser(TextPlainRendering.content_type), parser)
        # should drop the q=x.x stuff...
        self.assertEquals(registry.get_parser(TextPlainRendering.content_type + ';q=0.9'), parser)
        # */* --> default
        self.assertEquals(registry.get_parser('*/*'), parser)
        # request with comma separated list...
        self.assertEquals(registry.get_parser(TextPlainRendering.content_type + ',' + TextHTMLRendering.content_type), parser)

if __name__ == "__main__":
    unittest.main()
