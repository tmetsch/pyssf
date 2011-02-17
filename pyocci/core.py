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
This module holds the OCCI core model.

Created on Nov 10, 2010

@author: tmetsch
'''

# disabling 'Too few public methods' pylint check R0903 (This is a model)
# disabling 'Missing docstring' pylint check C0111 (Docs can be found in OCCI)
# disabling 'Too many instance attributes' pyling check Ro902 (All okay)
# pylint: disable=R0903,C0111,R0902


class Category(object):

    def __init__(self):
        self.scheme = ''
        self.term = ''
        self.title = ''
        self.attributes = []

        self.cls_str = 'action'

    def __eq__(self, instance):
        if instance is None or not isinstance(instance, Category):
            return False
        if self.term == instance.term and self.scheme == instance.scheme:
            return True
        else:
            return False

    def __repr__(self):
        return self.scheme + '#' + self.term

class Kind(Category):

    def __init__(self):
        super(Kind, self).__init__()
        self.related = []
        self.actions = []

        # Following are not defined by the OCCI spec
        self.location = ''
        self.cls_str = 'kind'

class Mixin(Category):

    def __init__(self):
        super(Mixin, self).__init__()
        self.related = []
        self.actions = []

        # Following are not defined by the OCCI spec
        self.location = ''
        self.owner = ''
        self.cls_str = 'mixin'

class Entity(object):

    category = Kind()
    category.actions = []
    category.attributes = ['id', 'title']
    category.location = ''
    category.related = []
    category.scheme = 'http://schemas.ogf.org/occi/core'
    category.term = 'entity'
    category.title = 'Entity type'

    def __init__(self):
        self.kind = None
        self.mixins = []
        self.identifier = 0
        self.title = ''

        # Following are not defined by the OCCI spec
        self.owner = ''
        self.identifier = ''

class Resource(Entity):

    category = Kind()
    category.actions = []
    category.attributes = ['summary']
    category.location = ''
    category.related = [Entity.category]
    category.scheme = 'http://schemas.ogf.org/occi/core'
    category.term = 'resource'
    category.title = 'Resource'

    def __init__(self):
        super(Resource, self).__init__()
        self.kind = self.category
        self.summary = ''
        self.links = []

        # not defined by OCCI spec
        self.attributes = {}
        self.actions = []

class Link(Entity):

    category = Kind()
    category.actions = []
    category.attributes = ['source', 'target']
    category.location = ''
    category.related = [Entity.category]
    category.scheme = 'http://schemas.ogf.org/occi/core'
    category.term = 'link'
    category.title = 'Link'

    def __init__(self):
        super(Link, self).__init__()
        self.kind = self.category
        self.source = None
        self.target = None

        # not defined by OCCI spec
        self.attributes = {}
        self.actions = []

class Action(object):

    category = Category()
    category.attributes = []
    category.scheme = 'http://schemas.ogf.org/occi/core'
    category.term = 'action'
    category.title = 'Action'

    def __init__(self):
        self.kind = self.category

        # not defined by OCCI spec
        self.attributes = {}

    def __repr__(self):
        return self.kind.scheme + '#' + self.kind.term

    def __eq__(self, instance):
        if instance is None or not isinstance(instance, Action):
            return False
        if self.kind == instance.kind:
            return True
        else:
            return False
