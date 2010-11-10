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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
This module holds the OCCI core model.

Created on Nov 10, 2010

@author: tmetsch
'''

# disabling 'Too few public methods' pylint check R0903 (This is a model)
# disabling 'Missing docstring' pyling check C0111 (Docs can be found in OCCI)
# pylint: disable=R0903,C0111

class Category(object):

    def __init__(self):
        self.scheme = ''
        self.term = ''
        self.title = ''
        self.attribtues = []

class Kind(Category):

    def __init__(self):
        super(Kind, self).__init__()
        self.related = []
        self.actions = []

        # Following are not defined by the OCCI spec
        self.location = ''

class Mixin(Category):

    def __init__(self):
        super(Mixin, self).__init__()
        self.related = []
        self.actions = []

        # Following are not defined by the OCCI spec
        self.location = ''

class Entity(object):

    def __init__(self):
        self.kind = None
        self.mixins = []
        self.identifier = 0
        self.title = ''

        # Following are not defined by the OCCI spec
        self.owner = ''

class Resource(Entity):

    def __init__(self):
        super(Resource, self).__init__()
        self.summary = ''
        self.links = []

class Link(Entity):

    def __init__(self):
        super(Link, self).__init__()
        self.source = None
        self.target = None

class Action(object):

    def __init__(self):
        self.kind = None
