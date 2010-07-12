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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 
'''
Created on Jul 12, 2010

@author: tmetsch
'''
from resource_model import Link, Resource, Category
import unittest

class ActionLinkTest(unittest.TestCase):

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_get_action_links_for_success(self):
        action_link = Link()
        resource = Resource()
        action_link.target = "http://example.com/123/#tada"
        action_link.link_class = "action"
        resource.links.append(action_link)
        res = resource.get_action_links()
        self.assertEquals(res[0].link_class, action_link.link_class)

    def test_get_certain_categories_for_success(self):
        category = Category()
        resource = Resource()
        category.term = 'job'
        category.scheme = 'http://purl.org/occi/kind#'
        resource.categories.append(category)
        res = resource.get_certain_categories('job')
        self.assertEquals(res[0].scheme, 'http://purl.org/occi/kind#')

    # --------
    # TEST FOR FAILUTE
    # --------

    def test_get_action_links_for_failure(self):
        # when a action link is given without target -> res = 0!
        action_link = Link()
        resource = Resource()
        action_link.link_class = "action"
        resource.links.append(action_link)
        self.assertEquals([], resource.get_action_links())

    def test_get_certain_categories_for_failure(self):
        # ???
        pass

    # --------
    # TEST FOR SANITY
    # --------

    def test_get_action_links_for_sanity(self):
        action_link = Link()
        other_link = Link()
        resource = Resource()
        action_link.target = "http://example.com/123/#tada"
        action_link.link_class = "action"
        other_link.target = "http://example.com/abc/#job"
        other_link.link_class = "category"
        resource.links.append(action_link)
        resource.links.append(other_link)
        self.assertEquals(1, len(resource.get_action_links()))

    def test_get_certain_categories_for_sanity(self):
        # already done in success test.
        pass

if __name__ == "__main__":
    unittest.main()
