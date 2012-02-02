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
Set of functions to parse stuff.

Created on Jun 28, 2011

@author: tmetsch
'''

from occi.core_model import Category, Link, Mixin, Kind

#==============================================================================
# Following are text/occi and text/plain related parsing functions.
#==============================================================================


def get_category(category_string, categories, is_mixin=False):
    '''
    Create a Category from a string rendering.

    If found it will return the object from the registry.

    If is_mixin is set to true it will not match with the registry and just
    return a Mixin.

    category_string -- A string rendering of a category.
    categories -- A list of registered categories.
    is_mixin -- Mixin will be created and no matching will be done.
    '''
    # find term
    term = category_string[:category_string.find(';')].strip()

    # find scheme
    scheme = find_in_string(category_string, 'scheme')

    if is_mixin:
        location = find_in_string(category_string, 'location')
        if not location[0] == '/' or not location[-1] == '/':
            raise AttributeError('Illegal location; must start and end with /')
        return Mixin(scheme, term, location=location)

    # return the category from registry...
    tmp = Category(scheme, term, '', {}, '')
    for item in categories:
        if tmp == item:
            del(tmp)
            return item
    raise AttributeError('The following category is not registered within'
                         + ' this service (See Query interfaces): '
                         + str(scheme) + str(term))


def get_category_str(category):
    '''
    Create a string rendering for a Category.

    category -- A category.
    '''
    tmp = ''
    tmp += category.term
    tmp += '; scheme="' + category.scheme + '"'
    tmp += '; class="' + repr(category) + '"'
    if hasattr(category, 'title') and category.title is not '':
        tmp += '; title="' + category.title + '"'
    if hasattr(category, 'related') and len(category.related) > 0:
        rel_list = []
        for item in category.related:
            rel_list.append(str(item))
        tmp += '; rel="' + ' '.join(rel_list) + '"'
    if hasattr(category, 'location') and category.location is not None:
        tmp += '; location="' + category.location + '"'
    if hasattr(category, 'attributes') and len(category.attributes) > 0:
        attr_list = []
        for item in category.attributes:
            if category.attributes[item] == 'required':
                attr_list.append(item + '{required}')
            elif category.attributes[item] == 'immutable':
                attr_list.append(item + '{immutable}')
            else:
                attr_list.append(item)
        tmp += '; attributes="' + ' '.join(attr_list) + '"'
    if hasattr(category, 'actions') and len(category.actions) > 0:
        action_list = []
        for item in category.actions:
            action_list.append(str(item))
        tmp += '; actions="' + ' '.join(action_list) + '"'
    return tmp


def _get_link_categories(categories, registry):
    '''
    Determine the kind ans mixins for inline link creation.

    categories -- String with a set of category string definitions.
    registry -- Registry used for this call.
    '''
    tmp_kind = None
    tmp_mixins = []
    for tmp_cat in categories.split(' '):
        tempus = tmp_cat.split('#')
        link_category = get_category(tempus[1].strip() + ';scheme="'
                                     + tempus[0].strip() + '#"',
                                     registry.get_categories())
        if isinstance(link_category, Kind):
            tmp_kind = link_category
        else:
            tmp_mixins.append(link_category)

    return tmp_kind, tmp_mixins


def get_link(link_string, source, registry):
    '''
    Create a Link from a string rendering.

    Also note that the link_id is set but is not yet registered as resource.

    link_string -- A string rendering of a link.
    source -- The source entity.
    registry -- Registry used for this call.
    '''
    tmp = link_string.find('<') + 1
    target_id = link_string[tmp:link_string.rfind('>', tmp)].strip()

    try:
        link_id = find_in_string(link_string, 'self')
    except AttributeError:
        link_id = None

    try:
        tmp_category = find_in_string(link_string, 'category')
    except AttributeError:
        raise AttributeError('Could not determine the Category of the Link.')

    tmp_kind, tmp_mixins = _get_link_categories(tmp_category, registry)

    if tmp_kind is None:
        raise AttributeError('Unable to find the Kind of the Link.')

    attributes = {}
    attr_begin = link_string.find('category="') + 12 + len(tmp_category)
    attributes_str = link_string[attr_begin:]
    for attribute in attributes_str.split(';'):
        tmp = attribute.strip().split('=')
        if len(tmp) == 2:
            attributes[tmp[0].strip()] = tmp[1].rstrip('"').lstrip('"').strip()

    try:
        if target_id.find(registry.get_hostname()) == 0:
            target_id = target_id.replace(registry.get_hostname(), '')
        target = registry.get_resource(target_id)
    except KeyError:
        raise AttributeError('The target for the link cannot be found: '
                             + target_id)

    link = Link(link_id, tmp_kind, tmp_mixins, source, target)
    link.attributes = attributes
    return link


def get_link_str(link):
    '''
    Create a string rendering for a Link.

    link -- A link.
    '''
    tmp = '<' + link.target.identifier + '>'
    tmp = tmp + '; rel="' + str(link.target.kind) + '"'
    tmp = tmp + '; self="' + str(link.identifier) + '"'
    tmp = tmp + '; category="' + str(link.kind)

    if len(link.mixins) > 0:
        for mixin in link.mixins:
            tmp = tmp + ' ' + str(mixin)

    tmp = tmp + '"'

    link.attributes['occi.core.id'] = link.identifier
    link.attributes['occi.core.source'] = link.source.identifier
    link.attributes['occi.core.target'] = link.target.identifier

    if len(link.attributes) > 0:
        attr_str_list = []
        for item in link.attributes:
            attr_str_list.append(item + '="' + link.attributes[item] + '"')
        tmp = tmp + '; ' + '; '.join(attr_str_list)
    return tmp


def get_attributes(attribute_string):
    '''
    Retrieve the attributes from the HTTP X-OCCI-Attribute rendering.
    '''
    try:
        tmp = _strip_all(attribute_string)
        key = _strip_all(tmp.split('=')[0])
        value = tmp.split('=')[1]
        if value.find('"') is not -1:
            value = _strip_all(value)
    except IndexError:
        raise AttributeError('Could not determine the given attributes')

    return key, value

#==============================================================================
# Helpers
#==============================================================================


def _strip_all(string):
    '''
    Removes beginning / ending quotes and whitespaces.
    '''
    return string.lstrip().lstrip('"').rstrip().rstrip('"')


def find_in_string(string, name):
    '''
    Search for string which is surrounded by '<name>=' and ';'. Raises
    AttributeError if value cannot be found.

    string -- The string to look into.
    name -- The name of the value to look for.
    '''
    begin = string.find(name + '=')
    end = string.find(';', begin)
    result = string[begin + len(name) + 1:end].rstrip('"').lstrip('"').strip()
    if begin == -1:
        raise AttributeError('Could not determine the value for: ' + name)
    return result
