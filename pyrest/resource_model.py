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
This module contains the basic model which is used in the overall service.

Created on Jul 9, 2010

@author: tmetsch
'''

class Resource:
    """
    A resource kind."""
    id = ''
    """Immutable, unique identifier of the instance (Multiplicity 1)"""
    categories = []
    """This is a set of associated categories with Kind.
       There must be at minimum one Category associated 
       (Multiplicity 1..n)"""
    links = []
    """This is a set of associated Links with Kind (Multiplicity 0..n)"""
    data = ''
    """Data which was initially provided by the client in the body."""

    def get_action_links(self):
        """
        Returns only the links which are basically a action. Empty list if none.
        """
        result = []
        for item in self.links:
            if item.link_class == 'action' and item.target is not '':
                result.append(item)
        return result

    def get_certain_categories(self, name):
        """
        Return all categories with the given term. Empty list if none.
        """
        result = []
        for item in self.categories:
            if item.term == name:
                result.append(item)
        return result

    def __cmp__(self, instance):
        """
        Very weak test if two resources are the same. Since by rule ids are
        unique: two resources with same id are considered identical.
        """
        if self.id == instance.id:
            return True
        else:
            return False


class Category:
    """
    A category.
    """
    term = ''
    """Target definition within the scheme (Multiplicity 1)"""
    scheme = ''
    """A resource that defines the model of the referred term (Multiplicity 1)"""
    title = ''
    """assigned links/actions (Multiplicity 0,1)"""
    related = []
    """A set of related categories (Multiplicity 0..n)"""

class Link:
    """
    A link.
    """
    link_class = ''
    """This denotes the type of Link (Multiplicity 0,1)"""
    title = ''
    """Display name for the Link (Multiplicity 0,1)"""
    rel = ''
    """The type of Link (Multiplicity 0,1)"""
    target = ''
    """The Kind to which the Link points to (Multiplicity 1)"""

class JobResource(Resource):
    """
    A job resource kind.
    """

    attributes = {}
    """Attributes assigned to this resource kind."""
