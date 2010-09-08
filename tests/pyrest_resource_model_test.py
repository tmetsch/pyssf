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
from pyrest.resource_model import Resource, Category, Kind
from pyrest.backends import JobHandler
import unittest

class BasicTests(unittest.TestCase):

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_get_certain_categories_for_success(self):
        category = Category()
        resource = Resource()
        category.term = 'job'
        category.scheme = 'http://schemas.ogf.org/occi/resource#'
        resource.categories.append(category)
        res = resource.get_certain_categories('job')
        self.assertEquals(res[0].scheme, 'http://schemas.ogf.org/occi/resource#')

    def test_resource_eq_for_success(self):
        resource1 = Resource()
        resource1.id = 'foo'
        resource2 = Resource()
        resource2.id = 'foo'
        self.assertTrue(resource1.__eq__(resource2))

    def test_kind_eq_for_success(self):
        # includes tests for category comp. because kind == kind if cat = cat!
        kind1 = Kind()
        kind1.title = 'bla'
        kind1.categories = [Resource.category]
        kind2 = Kind()
        kind2.title = 'foo'
        kind2.categories = [Resource.category]
        self.assertTrue(kind1, kind2)

    # --------
    # TEST FOR FAILUTE
    # --------

    def test_get_certain_categories_for_failure(self):
        # ???
        pass

    def test_resource_eq_for_failure(self):
        resource1 = Resource()
        resource1.id = 'foo'
        resource2 = Resource()
        resource2.id = 'bar'
        self.assertFalse(resource1.__eq__(resource2))

    def test_kind_eq_for_failure(self):
        # includes tests for category comp. because kind == kind if cat = cat!
        kind1 = Kind()
        kind1.title = 'bla'
        kind1.categories = [Resource.category]
        kind2 = Kind()
        kind2.title = 'foo'
        kind2.categories = [JobHandler.category]
        self.assertFalse(kind1.__eq__(kind2))

    # --------
    # TEST FOR SANITY
    # --------

    def test_get_certain_categories_for_sanity(self):
        # already done in success test.
        pass

if __name__ == "__main__":
    unittest.main()
