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
Created on Nov 17, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci import registry, service, rendering_parsers
from pyocci.core import Resource, Link, Mixin, Category, Action
from pyocci.my_exceptions import ParsingException
from pyocci.rendering_parsers import TextPlainRendering, Rendering, HTTPData, \
    TextHTMLRendering, TextHeaderRendering, URIListRendering
from tests import http_body, http_body_add_info, http_body_faulty_scheme, \
    http_body_faulty_sep, http_body_faulty_term, http_body_just_crap, \
    http_body_mul_cats, http_body_mis_keyword, http_body_mis_scheme, \
    http_body_mis_term, http_body_non_existing_category, ComputeBackend, \
    http_body_with_attr, http_body_only_attr, http_body_link, MyMixinBackend, \
    http_head, http_head_with_attr, http_head_add_info, http_head_only_attr, \
    http_head_link, http_head_non_existing_category, NetworkLinkBackend, \
    http_body_loc, http_body_action, http_body_mixin, http_body_faulty_loc, \
    http_body_faulty_action, http_body_faulty_mixin, http_body_with_faulty_attr, \
    html_create_res, html_create_link, html_faulty_create, html_action, \
    html_faulty_action, http_head_loc, http_head_action, http_head_mixin, \
    http_head_mul_cats, http_head_faulty_loc, http_head_faulty_action, \
    http_head_faulty_mixin, http_head_faulty_scheme, http_head_faulty_sep, \
    http_head_faulty_term, http_head_just_crap, http_head_mis_keyword, \
    http_head_mis_scheme, http_head_mis_term, http_head_with_faulty_attr, \
    html_with_empty_attr, http_body_link_with_base_url, http_body_loc_with_base_url, \
    http_head_loc_with_base_url, http_head_link_with_base_url, \
    html_create_link_with_base_url, http_body_with_link, http_head_with_link, \
    NetworkInterfaceBackend, http_body_with_faulty_link, http_body_with_faulty_link2, \
    http_body_with_faulty_link3
import unittest
import urllib

class HTTPDataTest(unittest.TestCase):

    def test_instanciation_for_success(self):
        HTTPData()

class RenderingTest(unittest.TestCase):

    rendered = Rendering()

    def test_if_errors_are_thrown(self):
        self.assertRaises(NotImplementedError, self.rendered.from_categories, [None])
        self.assertRaises(NotImplementedError, self.rendered.from_entities, [None])
        self.assertRaises(NotImplementedError, self.rendered.from_entity, None)
        self.assertRaises(NotImplementedError, self.rendered.get_entities, None, None)
        self.assertRaises(NotImplementedError, self.rendered.login_information)
        self.assertRaises(NotImplementedError, self.rendered.to_action, None, None)
        self.assertRaises(NotImplementedError, self.rendered.to_categories, None, None)
        self.assertRaises(NotImplementedError, self.rendered.to_entity, None, None)

class OCCIRenderingTest(unittest.TestCase):

    resource = Resource()

    def setUp(self):
        self.resource.identifier = '/network/123'
        self.resource.kind = NetworkLinkBackend.category
        service.RESOURCES['/network/123'] = self.resource

    def tearDown(self):
        service.RESOURCES = {}

    #===========================================================================
    # Test for Sanity
    #===========================================================================

    def test_from_http_category_for_sanity(self):
        category_string = 'storage; scheme="http://schemas.ogf.org/occi/infrastructure#"; class="kind"; title="Storage Resource"; rel="http://schemas.ogf.org/occi/core#resource"; location=/storage/; attributes="occi.storage.size occi.storage.state"; actions="http://schemas.ogf.org/occi/infrastructure/storage/action#resize";'
        tmp = rendering_parsers._from_http_category(category_string)
        result = rendering_parsers._to_http_category(tmp, extended = True)

        self.assertTrue(result.find('storage') is not - 1)
        self.assertTrue(result.find('scheme="http://schemas.ogf.org/occi/infrastructure#";') is not - 1)

    def test_from_http_link_for_sanity(self):
        link_string = '</network/123>; rel="http://schemas.ogf.org/occi/infrastructure#networklink"; category="http://schemas.ogf.org/occi/infrastructure#networkinterface"; occi.networkinterface.interface="eth0"; occi.networkinterface.mac="00:11:22:33:44:55"; occi.networkinterface.state="active";'
        tmp = rendering_parsers._from_http_link(link_string)
        tmp.identifier = '/foo/bar'
        result = rendering_parsers._to_http_link(tmp)
        #self.assertEquals(result, link_string)
        for item1 in link_string.split(';'):
            found = False
            for item2 in result.split(';'):
                if item2.strip().find(item1.strip()) is not - 1:
                    found = True
                    break
            if found is not True:
                self.fail('Could not find item: ' + item1)
            else:
                found = False

        #action...
        action_string = '</compute/123?action=start>; rel="http://schemas.ogf.org/occi/infrastructure/compute/action#start"'

        entity = Resource()
        entity.identifier = '/compute/123'
        action = Action()
        action_cat = Category()
        action_cat.term = 'start'
        action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/compute/action'
        action.kind = action_cat

        result = rendering_parsers._to_http_link(entity, action, is_action = True)
        self.assertEquals(result, action_string)

    def test_from_http_attribute_for_sanity(self):
        attr_string = 'occi.compute.desc="soem bla bla"'
        key, value = rendering_parsers._from_http_attribute(attr_string)
        result = rendering_parsers._to_http_attribute(key, value)
        self.assertEquals(result, attr_string)

        attr_string = 'occi.compute.cores="2"'
        key, value = rendering_parsers._from_http_attribute(attr_string)
        result = rendering_parsers._to_http_attribute(key, value)
        self.assertEquals(result, attr_string)

    def test_from_http_location_for_sanity(self):
        loc_string = 'http://example.com/compute/12'
        tmp = rendering_parsers._from_http_location(loc_string)
        result = rendering_parsers._to_http_location(tmp)
        self.assertEquals(result, loc_string)

class TextPlainRenderingTest(unittest.TestCase):

    parser = TextPlainRendering()
    entity = Resource()
    link = Link()

    def setUp(self):
        self.link.source = 'bar'
        self.link.target = 'foo'
        self.entity.kind = ComputeBackend.category
        self.entity.mixins = [MyMixinBackend.category]
        self.entity.actions = [ComputeBackend.start_action]
        self.entity.links = [self.link]
        self.entity.attributes['foo'] = 'bar'
        self.entity.summary = 'foo'
        self.entity.title = 'My compute node...'

        registry.HOST = 'http://localhost:8080'
        registry.register_backend([ComputeBackend.start_category, ComputeBackend.category], ComputeBackend())
        registry.register_backend([NetworkLinkBackend.category], NetworkLinkBackend())
        registry.register_backend([NetworkInterfaceBackend.category], NetworkInterfaceBackend())
        registry.register_backend([MyMixinBackend.category], MyMixinBackend())

    def tearDown(self):
        registry.HOST = ''
        registry.BACKENDS = {}

    #===========================================================================
    # Test for succes
    #===========================================================================

    def test_from_categories_for_success(self):
        self.parser.from_categories([])
        self.parser.from_categories([ComputeBackend.category])

    def test_from_entities_for_succes(self):
        self.parser.from_entities([self.entity])

    def test_from_entity_for_succes(self):
        self.parser.from_entity(self.entity)
        self.parser.from_entity(self.link)

    def test_get_entities_for_succes(self):
        self.parser.get_entities(None, http_body_loc)

    def test_login_information_for_succes(self):
        self.parser.login_information()

    def test_to_action_for_succes(self):
        self.parser.to_action(None, http_body_action)

    def test_to_categories_for_succes(self):
        self.parser.to_categories(None, http_body_mixin)

    def test_to_entity_for_succes(self):
        self.parser.to_entity(None, http_body)
        self.parser.to_entity(None, http_body_with_attr)
        self.parser.to_entity(None, http_body_with_link)
        self.parser.to_entity(None, http_body_add_info)
        self.parser.to_entity(None, http_body_mul_cats)

        self.parser.to_entity(None, http_body_only_attr, True, ComputeBackend.category)

        self.parser.to_entity(None, http_body_link)

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_get_entities_for_failure(self):
        self.assertRaises(ParsingException, self.parser.get_entities, None, http_body_faulty_loc)

    def test_to_action_for_failure(self):
        self.assertRaises(ParsingException, self.parser.to_action, None, '')
        self.assertRaises(ParsingException, self.parser.to_action, None, http_body_mixin)
        self.assertRaises(ParsingException, self.parser.to_action, None, http_body_faulty_action)
        self.assertRaises(ParsingException, self.parser.to_action, None, http_body)

    def test_to_categories_for_failure(self):
        self.assertRaises(ParsingException, self.parser.to_categories, None, http_body_faulty_mixin)

    def test_to_entity_for_failure(self):
        # syntax errors
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_faulty_scheme)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_faulty_sep)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_faulty_term)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_just_crap)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_just_crap)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_mis_keyword)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_mis_scheme)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_mis_term)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_with_faulty_attr)

        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_with_faulty_link)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_with_faulty_link2)
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_with_faulty_link3)

        # semantic errors
        self.assertRaises(ParsingException, self.parser.to_entity, None, http_body_non_existing_category)

        # wrong parameters
        self.assertRaises(ParsingException, self.parser.to_entity, None, None, True, None)

    # All other methods should never throw something!

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_from_categories_for_sanity(self):
        heads, body = self.parser.from_categories([ComputeBackend.category])
        self.assertEquals(heads['Content-Type'], 'text/plain')
        self.assertTrue(body.find(http_body) > -1)

    def test_from_entities_for_sanity(self):
        heads, body = self.parser.from_entities([self.entity])
        self.assertEquals(heads['Content-Type'], 'text/plain')
        self.assertTrue(body.find(self.entity.identifier) > -1)

    def test_from_entity_for_sanity(self):
        heads, data = self.parser.from_entity(self.entity)
        self.assertEquals(heads['Content-Type'], 'text/plain')
        self.assertTrue(data.find('Category: compute;') > -1)
        self.assertTrue(data.find('Category: my_stuff;') > -1)
        self.assertTrue(data.find('summary="foo"') > -1)
        self.assertTrue(data.find('foo="bar"') > -1)

    def test_get_entities_for_sanity(self):
        en_list = self.parser.get_entities(None, http_body_loc)
        self.assertTrue(len(en_list) == 1)
        en_list = self.parser.get_entities(None, http_body_loc_with_base_url)
        self.assertTrue(len(en_list) == 2)

    def test_login_information_for_sanity(self):
        heads, data = self.parser.login_information()
        self.assertEquals(heads['Content-Type'], 'text/plain')

    def test_to_action_for_sanity(self):
        action = self.parser.to_action(None, http_body_action)
        self.assertEqual(action.kind, ComputeBackend.start_category)

    def test_to_categories_for_sanity(self):
        categories = self.parser.to_categories(None, http_body_mixin)
        for cat in categories:
            self.assertTrue(isinstance(cat, Mixin))

    def test_to_entity_for_sanity(self):
        resource, links = self.parser.to_entity(None, http_body_with_attr)
        self.assertTrue(isinstance(resource, Resource))
        self.assertEquals(resource.summary, 'bar')
        self.assertEquals(resource.kind, ComputeBackend.category)

        link, links = self.parser.to_entity(None, http_body_link)
        self.assertTrue(isinstance(link, Link))
        self.assertEquals(link.source, 'foo')
        self.assertEquals(link.target, 'bar')
        self.assertEquals(link.kind, NetworkLinkBackend.category)

        link, links = self.parser.to_entity(None, http_body_link_with_base_url)
        self.assertTrue(isinstance(link, Link))
        self.assertEquals(link.source, '/foo')
        self.assertEquals(link.target, '/bar')
        self.assertEquals(link.kind, NetworkLinkBackend.category)

        multi_line = http_body + '\nCategory:' + http_body_mul_cats.split(',')[1]
        resource1, links = self.parser.to_entity(None, http_body_mul_cats)
        resource2, links = self.parser.to_entity(None, multi_line)
        self.assertEquals(resource1.kind, resource2.kind)
        self.assertEquals(resource1.mixins, resource2.mixins)

class TextHeaderRenderingTest(unittest.TestCase):

    parser = TextHeaderRendering()
    entity = Resource()
    link = Link()

    def setUp(self):
        self.link.source = 'bar'
        self.link.target = 'foo'
        self.entity.kind = ComputeBackend.category
        self.entity.mixins = [MyMixinBackend.category]
        self.entity.actions = [ComputeBackend.start_action]
        self.entity.links = [self.link]
        self.entity.attributes['foo'] = 'bar'
        self.entity.summary = 'foo'

        service.RESOURCES['foo'] = self.entity
        service.RESOURCES['bar'] = self.entity

        registry.HOST = 'http://localhost:8080'
        registry.register_backend([ComputeBackend.start_category, ComputeBackend.category], ComputeBackend())
        registry.register_backend([NetworkLinkBackend.category], NetworkLinkBackend())
        registry.register_backend([NetworkInterfaceBackend.category], NetworkInterfaceBackend())
        registry.register_backend([MyMixinBackend.category], MyMixinBackend())

    def tearDown(self):
        registry.HOST = ''
        registry.BACKENDS = {}

    #===========================================================================
    # Test for succes
    #===========================================================================

    def test_from_categories_for_success(self):
        self.parser.from_categories([])
        self.parser.from_categories([ComputeBackend.category])

    def test_from_entities_for_succes(self):
        self.parser.from_entities([self.entity])

    def test_from_entity_for_succes(self):
        self.parser.from_entity(self.entity)
        self.parser.from_entity(self.link)

    def test_get_entities_for_succes(self):
        self.parser.get_entities(http_head_loc, None)

    def test_login_information_for_succes(self):
        self.parser.login_information()

    def test_to_action_for_succes(self):
        self.parser.to_action(http_head_action, None)

    def test_to_categories_for_succes(self):
        self.parser.to_categories(http_head_mixin, None)

    def test_to_entity_for_succes(self):
        self.parser.to_entity(http_head, None)
        self.parser.to_entity(http_head_with_attr, None)
        self.parser.to_entity(http_head_with_link, None)
        self.parser.to_entity(http_head_add_info, None)
        self.parser.to_entity(http_head_mul_cats, None)

        self.parser.to_entity(http_head_only_attr, None, True, ComputeBackend.category)

        self.parser.to_entity(http_head_link, None)

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_get_entities_for_failure(self):
        self.assertRaises(ParsingException, self.parser.get_entities, http_head_faulty_loc, None)

    def test_to_action_for_failure(self):
        self.assertRaises(ParsingException, self.parser.to_action, {}, None)
        self.assertRaises(ParsingException, self.parser.to_action, http_head_faulty_action, None)
        self.assertRaises(ParsingException, self.parser.to_action, http_head_mixin, None)
        #self.assertRaises(ParsingException, self.parser.to_action, http_head_faulty_action_attr, None)
        self.assertRaises(ParsingException, self.parser.to_action, http_head, None)

    def test_to_categories_for_failure(self):
        self.assertRaises(ParsingException, self.parser.to_categories, http_head_faulty_mixin, None)

    def test_to_entity_for_failure(self):
        # syntax errors
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_faulty_scheme, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_faulty_sep, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_faulty_term, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_just_crap, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_just_crap, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_mis_keyword, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_mis_scheme, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_mis_term, None)
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_with_faulty_attr, None)

        # semantic errors
        self.assertRaises(ParsingException, self.parser.to_entity, http_head_non_existing_category, None)

        # wrong parameters
        self.assertRaises(ParsingException, self.parser.to_entity, None, None, True, None)

#    # All other methods should never throw something!

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_from_categories_for_sanity(self):
        heads, body = self.parser.from_categories([ComputeBackend.category])
        self.assertEquals(heads['Content-Type'], 'text/occi')
        self.assertTrue(heads['Category'])
        self.assertTrue(body == 'OK')

    def test_from_entities_for_sanity(self):
        heads, body = self.parser.from_entities([self.entity])
        self.assertEquals(heads['Content-Type'], 'text/occi')
        self.assertTrue(body == 'OK')
        self.assertTrue(heads['X-OCCI-Location'].find(self.entity.identifier) > -1)

    def test_from_entity_for_sanity(self):
        heads, body = self.parser.from_entity(self.entity)
        self.assertEquals(heads['Content-Type'], 'text/occi')
        self.assertTrue(body == 'OK')
        self.assertTrue(heads['Category'].find('compute;') > -1)
        self.assertTrue(heads['Category'].find('my_stuff;') > -1)
        self.assertTrue(heads['X-OCCI-Attribute'].find('foo="bar"') > -1)

    def test_get_entities_for_sanity(self):
        en_list = self.parser.get_entities(http_head_loc, None)
        self.assertTrue(len(en_list) == 1)
        en_list = self.parser.get_entities(http_head_loc_with_base_url, None)
        self.assertTrue(len(en_list) == 1)

    def test_login_information_for_sanity(self):
        heads, data = self.parser.login_information()
        self.assertEquals(heads['Content-Type'], 'text/occi')

    def test_to_action_for_sanity(self):
        action = self.parser.to_action(http_head_action, None)
        self.assertEqual(action.kind, ComputeBackend.start_category)

    def test_to_categories_for_sanity(self):
        categories = self.parser.to_categories(http_head_mixin, None)
        for cat in categories:
            self.assertTrue(isinstance(cat, Mixin))

    def test_to_entity_for_sanity(self):
        resource, links = self.parser.to_entity(http_head_with_attr, None)
        self.assertTrue(isinstance(resource, Resource))
        self.assertEquals(resource.summary, 'bar')
        self.assertEquals(resource.kind, ComputeBackend.category)

        link, links = self.parser.to_entity(http_head_link, None)
        self.assertTrue(isinstance(link, Link))
        self.assertEquals(link.source, 'foo')
        self.assertEquals(link.target, 'bar')
        self.assertEquals(link.kind, NetworkLinkBackend.category)

        link, links = self.parser.to_entity(http_head_link_with_base_url, None)
        self.assertTrue(isinstance(link, Link))
        self.assertEquals(link.source, '/foo')
        self.assertEquals(link.target, '/bar')
        self.assertEquals(link.kind, NetworkLinkBackend.category)

class TextHTMLRenderingTest(unittest.TestCase):

    parser = TextHTMLRendering()

    entity = Resource()
    link = Link()

    def setUp(self):
        self.link.source = 'bar'
        self.link.target = 'foo'
        self.entity.kind = ComputeBackend.category
        self.entity.mixins = [MyMixinBackend.category]
        self.entity.actions = [ComputeBackend.start_action]
        self.entity.links = [self.link]
        self.entity.attributes['foo'] = 'bar'
        self.entity.summary = 'foo'

        service.AUTHENTICATION = True

        registry.HOST = 'http://localhost:8080'
        registry.register_backend([ComputeBackend.start_category, ComputeBackend.category], ComputeBackend())
        registry.register_backend([NetworkLinkBackend.category], NetworkLinkBackend())
        registry.register_backend([MyMixinBackend.category], MyMixinBackend())

    def tearDown(self):
        registry.HOST = ''
        registry.BACKENDS = {}
        service.AUTHENTICATION = False

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_from_categories_for_success(self):
        self.parser.from_categories([])
        self.parser.from_categories([ComputeBackend.category])
        self.parser.from_categories([ComputeBackend.category, NetworkLinkBackend.category])

    def test_from_entities_for_success(self):
        self.parser.from_entities([self.entity])
        self.parser.from_entities([])

    def test_from_entity_for_success(self):
        self.parser.from_entity(self.entity)
        self.parser.from_entity(self.link)

    def test_login_information_for_succes(self):
        self.parser.login_information()

    def test_to_action_for_success(self):
        data = urllib.quote(html_action)
        self.parser.to_action(None, data)

    def test_to_entity_for_success(self):
        data = urllib.quote(html_create_res)
        self.parser.to_entity(None, data)
        data = urllib.quote(html_with_empty_attr)
        self.parser.to_entity(None, data)
        self.parser.to_entity(None, data, allow_incomplete = True, defined_kind = self.entity.kind)

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_to_action_for_failure(self):
        #self.assertRaises(ParsingException, self.parser.to_action, None, 'Category=http://example.com/occi/mine#my_stuff')
        self.assertRaises(ParsingException, self.parser.to_action, None, http_body_just_crap)
        self.assertRaises(ParsingException, self.parser.to_action, None, None)
        data = urllib.quote(html_faulty_action)
        self.assertRaises(ParsingException, self.parser.to_action, None, data)
        data = urllib.quote(html_create_res)
        self.assertRaises(ParsingException, self.parser.to_action, None, data)

    def test_get_entities_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.get_entities, None, None)

    def test_to_categories_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.to_categories, None, None)

    def test_to_entity_for_failure(self):
        data = urllib.quote(html_faulty_create)
        self.assertRaises(ParsingException, self.parser.to_entity, None, data)

        self.assertRaises(ParsingException, self.parser.to_entity, None, None)

        data = urllib.quote(http_body_just_crap)
        self.assertRaises(ParsingException, self.parser.to_entity, None, data)

        self.assertRaises(ParsingException, self.parser.to_entity, None, html_create_res, allow_incomplete = True, defined_kind = None)

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_to_entity_for_sanity(self):
        data = urllib.quote(html_create_res)
        resource, links = self.parser.to_entity(None, data)
        self.assertTrue(isinstance(resource, Resource))

        data = urllib.quote(html_create_link)
        link, links = self.parser.to_entity(None, data)
        self.assertTrue(isinstance(link, Link))

        data = urllib.quote(html_create_link_with_base_url)
        link, links = self.parser.to_entity(None, data)
        self.assertTrue(isinstance(link, Link))

    def test_from_categories_for_sanity(self):
        heads, body = self.parser.from_categories([ComputeBackend.category])
        self.assertEquals(heads['Content-Type'], 'text/html')

    def test_from_entities_for_sanity(self):
        heads, body = self.parser.from_entities([self.entity])
        self.assertEquals(heads['Content-Type'], 'text/html')

    def test_from_entity_for_sanity(self):
        heads, data = self.parser.from_entity(self.entity)
        self.assertEquals(heads['Content-Type'], 'text/html')

class URIListRenderingTest(unittest.TestCase):

    parser = URIListRendering()

    entity = Resource()
    link = Link()

    def setUp(self):
        self.link.source = 'bar'
        self.link.target = 'foo'
        self.entity.kind = ComputeBackend.category
        self.entity.mixins = [MyMixinBackend.category]
        self.entity.actions = [ComputeBackend.start_action]
        self.entity.links = [self.link]
        self.entity.attributes['foo'] = 'bar'
        self.entity.summary = 'foo'

        service.AUTHENTICATION = True

        registry.HOST = 'http://localhost:8080'
        registry.register_backend([ComputeBackend.start_category, ComputeBackend.category], ComputeBackend())
        registry.register_backend([NetworkLinkBackend.category], NetworkLinkBackend())
        registry.register_backend([MyMixinBackend.category], MyMixinBackend())

    def tearDown(self):
        registry.HOST = ''
        registry.BACKENDS = {}
        service.AUTHENTICATION = False

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_from_categories_for_success(self):
        self.parser.from_categories([])
        self.parser.from_categories([ComputeBackend.category])
        self.parser.from_categories([ComputeBackend.category, NetworkLinkBackend.category])

    def test_from_entities_for_success(self):
        self.parser.from_entities([self.entity])
        self.parser.from_entities([])

    #===========================================================================
    # Test for failure
    #===========================================================================

    def test_from_entity_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.from_entity, None)

    def test_get_entities_failure(self):
        self.assertRaises(NotImplementedError, self.parser.get_entities, None, None)

    def test_login_information_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.login_information)

    def test_to_action_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.to_action, None, None)

    def test_to_categories_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.to_categories, None, None)

    def test_to_entity_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.to_entity, None, None)

if __name__ == "__main__":
    unittest.main()
