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

class Kind(object):
    """
    A OCCI Kind.
    """
    def __init__(self):
        self.title = ''
        """ Denotes the display name of an instance. 0,1 """
        self.categories = []
        """ Comprises the categories associated to this instance. 1...* """

    def __eq__(self, instance):
        if self.categories == instance.categories:
            return True
        else:
            return False

class Category(object):
    """
    A category.
    """
    def __init__(self):
        self.term = ''
        """ Target definition within the scheme (Multiplicity 1) """
        self.scheme = ''
        """ A resource that defines the model of the referred term 
        (Multiplicity 1)"""
        self.title = ''
        """ Assigned links/actions (Multiplicity 0,1) """
        self.attributes = []
        """ Comprise the resource attributes defined by the Category. 
        (Multiplicity 0..n) """
        self.related = []
        """ A set of related categories (Multiplicity 0..n) """

    def __eq__(self, instance):
        if self.term == instance.term and self.scheme == instance.scheme:
            return True
        else:
            return False

class Resource(Kind):
    """
    A resource.
    """

    category = Category()
    category.attributes = ['id', 'summary', 'links', 'actions']
    category.related = []
    category.scheme = 'http://schemas.ogf.org/occi/core#'
    category.term = 'resource'
    category.title = 'A Resource'

    def __init__(self):
        super(Resource, self).__init__()
        self.id = ''
        """Immutable, unique identifier of the instance (Multiplicity 1)"""
        self.summary = ''
        """Holds a summarizing description of the Resource instance. 
        (Multiplicity 0,1)"""
        self.links = []
        """This is a set of associated Links with resource 
        (Multiplicity 0..n)"""
        self.actions = []
        """List of actions associated with this resource
        (Multiplicity 0..n)"""

        # following are not in the spec - but needed.
        self.data = ''
        """Data which was initially provided by the client in the body."""
        self.user = 'default'
        """The owner of this resource"""
        self.attributes = {}
        """Dictionary containing the attributes for this resource."""

    def get_certain_categories(self, name):
        """
        Return all categories with the given term. Empty list if none.
        """
        result = []
        for item in self.categories:
            if item.term == name:
                result.append(item)
        return result

    def __eq__(self, instance):
        """
        Very weak test if two resources are the same. Since by rule ids are
        unique: two resources with same id are considered identical.
        """
        if self.id == instance.id:
            return True
        else:
            return False

class Link(Kind):
    """
    A link.
    """

    category = Category()
    category.attributes = ['target']
    category.related = []
    category.scheme = 'http://schemas.ogf.org/occi/core#'
    category.term = 'link'
    category.title = 'A Link'

    def __init__(self):
        super(Link, self).__init__()
        self.target = ''
        """The Resource to which the Link points to (Multiplicity 1)"""

class Action(Kind):
    """
    A action.
    """

    category = Category()
    category.attributes = []
    category.related = []
    category.scheme = 'http://schemas.ogf.org/occi/core#'
    category.term = 'action'
    category.title = 'An Action'

    def __init__(self):
        super(Action, self).__init__()
