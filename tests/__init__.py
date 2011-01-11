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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 

'''
Created on Jun 28, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci import registry
from pyocci.backends import Backend
from pyocci.core import Kind, Mixin, Entity, Resource, Link, Action, Category
from pyocci.examples.keyvalue import LinkBackend
from pyocci.rendering_parsers import TextPlainRendering, TextHeaderRendering, \
    TextHTMLRendering

class ComputeBackend(Backend):

    start_action = Action()
    start_category = Category()
    start_category.term = 'start'
    start_category.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    start_action.kind = start_category

    category = Kind()
    category.term = 'compute'
    category.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    category.related = [Resource.category]
    category.location = '/compute/'
    category.attributes = ['occi.compute.architecture', 'occi.compute.cores']
    category.title = 'A compute resource'
    category.actions = [start_action]

    def create(self, entity):
        for item in entity.attributes.keys():
            if item not in self.category.attributes:
                raise AttributeError('The attribute ' + item + ' is not defined for this category!')

    def retrieve(self, entity):
        pass

    def update(self, old, new):
        for item in new.attributes.keys():
            if item in self.category.attributes:
                old.attributes[item] = new.attributes[item]
            else:
                raise AttributeError('The attribute ' + item + ' is not defined for this category!')

    def delete(self, entity):
        pass

    def action(self, entity, action):
        pass

class NetworkLinkBackend(LinkBackend):

    category = Kind()
    category.term = 'networklink'
    category.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    category.related = [Link.category]
    #category.location = '/ip_addr/'
    category.attributes = []

class MyMixinBackend(Backend):

    category = Mixin()
    category.term = 'my_stuff'
    category.scheme = 'http://example.com/occi/mine'
    category.location = '/my_stuff/'

class DefunctBackend(Backend):

    category = Kind()
    category.term = 'defunct'
    category.scheme = 'http://bad.com/defunct'
    category.related = [Resource.category]
    category.location = '/defunct/'
    category.attributes = []

    a_category = Category()
    a_category.term = 'foo'
    a_category.scheme = 'http://foo.com/bar'

#===============================================================================
# Correct requests...
#===============================================================================

# text/plain

http_body = 'Category: ' + ComputeBackend.category.term + ';scheme="' + ComputeBackend.category.scheme + '#";class="kind"'
http_body_with_attr = http_body + '\nX-OCCI-Attribute:foo=bar,summary=bar'
http_body_only_attr = 'X-OCCI-Attribute:foo=bar'
http_body_link = 'Category:' + NetworkLinkBackend.category.term + ';scheme="' + NetworkLinkBackend.category.scheme + '#"\nX-OCCI-Attribute:source=foo,target=bar'
http_body_link_with_base_url = 'Category:' + NetworkLinkBackend.category.term + ';scheme="' + NetworkLinkBackend.category.scheme + '#"\nX-OCCI-Attribute:source=http://localhost:8080/foo,target=http://localhost:8080/bar'
defunct_http_body = 'Category:' + DefunctBackend.category.term + ';scheme="' + DefunctBackend.category.scheme + '#"'
http_body_mul_cats = http_body + ',' + MyMixinBackend.category.term + ';scheme="' + MyMixinBackend.category.scheme + '#"'
http_body_add_info = http_body + ';term=foo'

http_body_loc = 'X-OCCI-Location: /foo/bar1'
http_body_loc_with_base_url = 'X-OCCI-Location: http://localhost:8080/foo/bar1'

http_body_action = 'Category: ' + ComputeBackend.start_category.term + ';scheme="' + ComputeBackend.start_category.scheme + '#"'

http_body_mixin = 'Category: mine;scheme=http://mystuff.com/occi#;location=/foo/bar/;'
http_body_mixin2 = 'Category: mine2;scheme=http://mystuff.com/occi#;location=/foo/bar/;'

# text/occi

http_head = {'Category': ComputeBackend.category.term + ';scheme="' + ComputeBackend.category.scheme + '#"'}
http_head_with_attr = {'Category': http_head['Category'], 'X-OCCI-Attribute':'foo=bar,summary=bar'}
http_head_only_attr = {'X-OCCI-Attribute':'foo=bar'}
http_head_link = {'Category': NetworkLinkBackend.category.term + ';scheme="' + NetworkLinkBackend.category.scheme + '#"', 'X-OCCI-Attribute':'source=foo,target=bar'}
http_head_link_with_base_url = {'Category': NetworkLinkBackend.category.term + ';scheme="' + NetworkLinkBackend.category.scheme + '#"', 'X-OCCI-Attribute':'source=http://localhost:8080/foo,target=http://localhost:8080/bar'}
defunct_http_head = {'Category': DefunctBackend.category.term + ';scheme="' + DefunctBackend.category.scheme + '#"'}

http_head_mul_cats = http_head.copy()
http_head_mul_cats['Category'] = http_head['Category'] + ',' + MyMixinBackend.category.term + ';scheme="' + MyMixinBackend.category.scheme + '#"'

http_head_add_info = http_head.copy()
http_head_add_info['Category'] = http_head['Category'] + ';term=foo'

http_head_loc = {'X-OCCI-Location': '/foo/bar1'}
http_head_loc_with_base_url = {'X-OCCI-Location': 'http://localhost:8080/foo/bar1'}

http_head_action = {'Category': ComputeBackend.start_category.term + ';scheme="' + ComputeBackend.start_category.scheme + '#"', 'X-OCCI-Attribute':'foo=bar'}

http_head_mixin = {'Category': 'mine;scheme="http://mystuff.com/occi#";location=/foo/bar/;'}

# text/html

html_create_res = 'Category=http://schemas.ogf.org/occi/infrastructure#compute&X-OCCI-Attribute=key=foo+value=bar+summary=jeeha'
html_with_empty_attr = 'Category=http://schemas.ogf.org/occi/infrastructure#compute' + '&X-OCCI-Attribute='
html_create_link = 'Category=http://schemas.ogf.org/occi/infrastructure#networklink&X-OCCI-Attribute=source=foo+target=bar'
html_create_link_with_base_url = 'Category=http://schemas.ogf.org/occi/infrastructure#networklink&X-OCCI-Attribute=source=http://localhost:8080/foo+target=http://localhost:8080/bar'
html_action = 'Category=' + ComputeBackend.start_category.scheme + '#' + ComputeBackend.start_category.term

#===============================================================================
# Faulty requests
#===============================================================================

# text/plain

http_body_mis_term = 'Category:scheme="example.com/occi/keyvalue"'
http_body_mis_scheme = 'Category:123;'
http_body_with_faulty_attr = http_body + '\nX-OCCI-Attribute:foo:bar,summary=bar'
http_body_faulty_term = 'Category:123;scheme="example.com/occi/keyvalue"'
http_body_faulty_scheme = 'Category:keyvalue;scheme="example.com/occi/keyvalue"'
http_body_mis_keyword = 'keyvalue;scheme="example.com/occi/keyvalue"'
http_body_faulty_sep = 'Category:keyvalue,scheme="example.com/occi/keyvalue"'
http_body_just_crap = 'sdkfhkjh;sdkjfhaksj'
http_body_non_existing_category = 'Category:foo;scheme="http://example.com/occi/bar"'

http_body_faulty_loc = 'X-OCCI-Locations:'
http_body_faulty_action = 'Category: ' + DefunctBackend.a_category.term + ';scheme="' + DefunctBackend.a_category.scheme + '"'
http_body_faulty_mixin = ''

# text/occi

http_head_mis_term = {'Category': 'scheme="example.com/occi/keyvalue"'}
http_head_mis_scheme = {'Category':'123;'}
http_head_with_faulty_attr = http_head.copy()
http_head_with_faulty_attr['X-OCCI-Attribute'] = 'foo:bar,summary=bar'
http_head_faulty_term = {'Category':'123;scheme="example.com/occi/keyvalue"'}
http_head_faulty_scheme = {'Category':'keyvalue;scheme="example.com/occi/keyvalue"'}
http_head_mis_keyword = {'':'keyvalue;scheme="example.com/occi/keyvalue"'}
http_head_faulty_sep = {'Category':'keyvalue,scheme="example.com/occi/keyvalue"'}
http_head_just_crap = {'sdkfhkjh':'sdkjfhaksj'}
http_head_non_existing_category = {'Category':'foo;scheme="http://example.com/occi/bar"'}

http_head_non_existing_category = {'Category':'foo;scheme="http://example.com/occi/bar"'}

http_head_faulty_loc = {'X-OCCI-Locations':''}
http_head_faulty_action = {'Category': DefunctBackend.a_category.term + ';scheme="' + DefunctBackend.a_category.scheme + '"'}
http_head_faulty_mixin = {}

http_head_faulty_action_attr = {'Category': ComputeBackend.start_category.term + ';scheme="' + ComputeBackend.start_category.scheme + '"', 'X-OCCI-Attribute':'foo:bar, summary = bar'}

# text/html
html_faulty_create = 'Category=http://jeeha.com/bla#tida&Attribute=key=foo+value=bar+summary=jeeha'
html_faulty_action = 'Category=' + DefunctBackend.a_category.scheme + '#' + DefunctBackend.a_category.term
