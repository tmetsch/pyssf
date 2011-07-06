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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
Set of functions to parse stuff.

Created on Jun 28, 2011

@author: tmetsch
'''

from occi import registry
from occi.core_model import Category, Link

#==============================================================================
# Following are text/occi and text/plain related parsing functions.
#==============================================================================


def get_category(category_string):
    '''
    Create a Category from a string rendering.

    If found it will return the object from the registry.

    @param category_string: A string rendering of a category.
    '''
    # find term
    term = category_string[:category_string.find(';')].strip()

    # find scheme
    scheme = find_in_string(category_string, 'scheme')

    # return the category from registry...
    tmp = Category(scheme, term)
    for item in registry.BACKENDS.keys():
        if tmp == item:
            del(tmp)
            return item
    raise AttributeError('The following category is not registered within'
                         + ' this service (See Query interfaces): '
                         + str(scheme) + str(term))


def get_category_str(category):
    '''
    Create a string rendering for a Category.

    @param category: A category.
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
    if hasattr(category, 'location') and category.location is not '':
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


def get_link(link_string, source):
    '''
    Create a Link from a string rendering.

    Also note that the link_id is set but is not yet registered as resource.

    @param link_string: A string rendering of a link.
    @param source: The source entity.
    '''
    tmp = link_string.find('<') + 1
    target_id = link_string[tmp:link_string.rfind('>', tmp)].strip()

    link_id = find_in_string(link_string, 'self')

    tmp_category = find_in_string(link_string, 'category')
    if tmp_category is None:
        raise AttributeError('Could not determine the Category of the Link.')
    tempus = tmp_category.split('#')
    link_category = get_category(tempus[1].strip() + ';scheme="'
                                 + tempus[0].strip() + '#"')

    attributes = {}
    attr_begin = link_string.find('category="') + 12 + len(tmp_category)
    attributes_str = link_string[attr_begin:]
    for attribute in attributes_str.split(';'):
        tmp = attribute.strip().split('=')
        if len(tmp) == 2:
            attributes[tmp[0].strip()] = tmp[1].rstrip('"').lstrip('"').strip()

    target = registry.RESOURCES[target_id]
    link = Link(link_id, link_category, [], source, target)
    link.attributes = attributes
    return link


def get_link_str(link):
    '''
    Create a string rendering for a Link.

    @param link: A link.
    '''
    tmp = '<' + link.target.identifier + '>'
    tmp = tmp + '; rel="' + str(link.target.kind) + '"'
    tmp = tmp + '; self="' + str(link.identifier) + '"'
    tmp = tmp + '; category="' + str(link.kind) + '"'
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
        key = tmp.split('=')[0]
        value = tmp.split('=')[1]
        if value.find('"') is not - 1:
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
    Search for string which is surrounded by '<name>=' and ';'. Returns None
    if the value cannot be found.

    @param string: The string to look into.
    @name: The name of the value to look for.
    '''
    begin = string.find(name + '=')
    end = string.find(';', begin)
    result = string[begin + len(name) + 1:end].rstrip('"').lstrip('"').strip()
    if begin == -1:
        return None
    return result
