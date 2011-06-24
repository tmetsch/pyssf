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
Created on Nov 10, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.core import Category, Kind, Mixin, Entity, Resource, Link, Action
import unittest

class CoreTest(unittest.TestCase):

    #===========================================================================
    # Test for success
    #===========================================================================

    def test_instanciation_for_success(self):
        Category()
        Mixin()
        Kind()
        Entity()
        Resource()
        Link()
        Action()

    #===========================================================================
    # Test for sanity
    #===========================================================================

    def test_category_repr_for_sanity(self):
        self.assertEquals(repr(Resource.category), Resource.category.scheme + '#' + Resource.category.term)

    def test_action_repr_for_sanity(self):
        action = Action()
        action.kind = Action.category
        self.assertEquals(repr(action), Action.category.scheme + '#' + Action.category.term)

    def test_category_eq_for_sanity(self):
        self.assertTrue(Resource.category == Resource.category)
        self.assertFalse(Resource.category == Link.category)
        self.assertFalse(Resource.category == None)

    def test_action_eq_for_sanity(self):
        action1 = Action()
        action1.kind = Action.category
        action2 = Action()
        action2.kind = Action.category
        action3 = Action()
        action3.kind = Link.category
        self.assertTrue(action1 == action2)
        self.assertFalse(action1 == action3)
        self.assertFalse(action1 == Link())
        self.assertFalse(action1 == None)

if __name__ == "__main__":
    unittest.main()
