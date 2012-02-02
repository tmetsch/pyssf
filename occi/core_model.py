#
# Copyright (C) 2010-2012 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
OCCI's core model.

Created on Jun 27, 2011

@author: tmetsch
'''

# disabling 'Too few public methods' pylint check (It's a model...)
# disabling 'Too many arguments' pylint check (It's more elegant this way...)
# pylint: disable=R0903, R0913

#==============================================================================
# Categories
#==============================================================================


class Category(object):
    '''
    OCCI Category.
    '''

    def __init__(self, scheme, term, title, attributes, location):
        self.scheme = scheme
        self.term = term
        self.title = title
        self.attributes = attributes

        # location
        self.location = location

    def __eq__(self, instance):
        if instance is None or not isinstance(instance, Category):
            return False
        if self.term == instance.term and self.scheme == instance.scheme:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.scheme) ^ hash(self.term)

    def __str__(self):
        return self.scheme + self.term


class Kind(Category):
    '''
    OCCI Kind.
    '''

    def __init__(self, scheme, term, related=None, actions=None, title='',
                 attributes=None, location=None):
        super(Kind, self).__init__(scheme, term, title, attributes or {},
                                   location or '/' + term + '/')
        self.related = related or []
        self.actions = actions or []

    def __repr__(self):
        return 'kind'


class Action(Category):
    '''
    OCCI Action.
    '''

    def __init__(self, scheme, term, title='', attributes=None):
        super(Action, self).__init__(scheme, term, title, attributes or {},
                                     location=None)

    def __repr__(self):
        return 'action'


class Mixin(Category):
    '''
    OCCI Mixin.
    '''

    def __init__(self, scheme, term, related=None, actions=None, title='',
                 attributes=None, location=None):
        super(Mixin, self).__init__(scheme, term, title, attributes or {},
                                    location or '/' + term + '/')
        self.related = related or []
        self.actions = actions or []

    def __repr__(self):
        return 'mixin'


#==============================================================================
# Entities
#==============================================================================


class Entity(object):
    '''
    OCCI Entity.
    '''

    def __init__(self, identifier, title, kind, mixins):
        self.identifier = identifier
        self.title = title
        self.kind = kind
        self.mixins = mixins

        # Attributes of resource entities
        self.attributes = {}
        self.actions = []
        self.extras = None


class Resource(Entity):
    '''
    OCCI Resource.
    '''

    kind = Kind('http://schemas.ogf.org/occi/core#', 'resource')

    def __init__(self, identifier, kind, mixins, links=None, summary=None,
                 title=None):
        super(Resource, self).__init__(identifier, title, kind, mixins)
        self.links = links or []
        self.summary = summary


class Link(Entity):
    '''
    OCCI Link.
    '''

    kind = Kind('http://schemas.ogf.org/occi/core#', 'link')

    def __init__(self, identifier, kind, mixins, source, target, title=None):
        super(Link, self).__init__(identifier, title, kind, mixins)
        self.source = source
        self.target = target
