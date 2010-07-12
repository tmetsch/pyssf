# 
# Copyright (C) 2010  Platform Computing
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
from resource_model import Link, Resource
import unittest

class ActionLinkTest(unittest.TestCase):

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_get_action_links_for_success(self):
        actionLink = Link()
        resource = Resource()
        actionLink.target = "http://example.com/123/#tada"
        actionLink.link_class = "action"
        resource.links.append(actionLink)
        res = resource.get_action_links()
        self.assertEquals(res[0].link_class, actionLink.link_class)

    # --------
    # TEST FOR FAILUTE
    # --------

    def test_get_action_links_for_failure(self):
        # when a action link is given without target -> res = 0!
        actionLink = Link()
        resource = Resource()
        actionLink.link_class = "action"
        resource.links.append(actionLink)
        self.assertEquals([], resource.get_action_links())
    # --------
    # TEST FOR SANITY
    # --------

    def test_get_action_links_for_sanity(self):
        actionLink = Link()
        otherLink = Link()
        resource = Resource()
        actionLink.target = "http://example.com/123/#tada"
        actionLink.link_class = "action"
        otherLink.target = "http://example.com/abc/#job"
        otherLink.link_class = "category"
        resource.links.append(actionLink)
        resource.links.append(otherLink)
        self.assertEquals(1, len(resource.get_action_links()))

if __name__ == "__main__":
    unittest.main()
