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
This module takes care of renderings an is pretty much generic.

Created on Jul 9, 2010

@author: tmetsch
'''

from pyrest.myexceptions import MissingCategoriesException
from pyrest.resource_model import Resource, Category, Action
import re

class HTTPData(object):
    """
    Very simple data structure which encapsulates the header and the body of a
    HTTP request. Needed basically by all parsers since this is REST :-)
    """

    header = {}
    body = ''

    def __init__(self, header, body):
        self.header = header
        self.body = body

class Parser(object):
    """
    The parsers have the capability to transform a resource to and from a
    HTTPData strcuture.
    """

    def to_action(self, http_data):
        """
        Parse an action request and return a Action.
        
        http_data -- the incoming data.
        """
        raise NotImplementedError

    def to_resource(self, key, http_data):
        """
        Parse the incoming data and return a Resource.
        
        key -- a unique identifier.
        http_data -- the incoming data.
        """
        raise NotImplementedError

    def from_resource(self, resource):
        """
        Parse the resource and return the data in the right rendering.
        
        resource -- the Resource to get the data from.
        """
        raise NotImplementedError

class HTTPHeaderParser(Parser):
    """
    Very simple parser which gets/puts links, categories and attributes.
    """
    # FIXME: handle multiple headers properly instead of using ,

    def _get_categories_from_header(self, heads):
        """
        Returns the all categories which could be found in the header.
        Otherwise return an empty list.
        
        heads -- the HTTP header dictionary.
        """
        result = []
        try:
            header = heads['HTTP_CATEGORY']
        except:
            raise MissingCategoriesException('No categories could be found in'
                                           + ' the header!')

        categories = header.split(',')
        for entry in categories:
            category = Category()
            # next two are mandatory and should be there!
            # do regex on url and term to check if ok 
            # find term
            try:
                tmp = entry.split(';')
                term = tmp[0].strip(' ')
                if re.match("^[\w\d_-]*$", term) and term is not '':
                    category.term = term
                else:
                    raise MissingCategoriesException('No valid term for given'
                                                   + 'category could be'
                                                   + 'found.')
            except:
                # todo log her...
                break
            # find scheme
            begin = entry.find('scheme="')
            if begin is not - 1:
                tmp = entry[begin + 8:]
                scheme = (tmp[:tmp.find('"')])
                if scheme.find('http') is not - 1:
                    category.scheme = scheme
                else:
                    break
            else:
                break

            # TODO: test if category is registered -> if so use it :-)

            # add non mandatory fields
            begin = entry.find('title="')
            if begin is not - 1:
                tmp = entry[begin + 7:]
                category.title = (tmp[:tmp.find('"')])

#            begin = entry.find('rel="')
#            if begin is not - 1:
#                tmp = entry[begin + 7:]
#                rel = (tmp[:tmp.find('"')])
#                category.related = rel.split(',')

            result.append(category)

        if len(result) == 0:
            raise MissingCategoriesException('No valid categories could be'
            + 'found.')
        return result

    def _get_attributes_from_header(self, heads):
        """
        Returns a list of attributes found in the header. Otherwise returns an
        empty dictionary.
        
        heads -- headers to parse the attributes from.
        """
        result = {}
        if 'HTTP_ATTRIBUTE' in heads.keys():
            for item in heads['HTTP_ATTRIBUTE'].split(','):
                tmp = item.split("=")
                if len(tmp[0].strip()) > 0 and len(tmp[1].strip()) > 0:
                    result[tmp[0].strip()] = tmp[1].strip()
                else:
                    break
        return result

    def _create_categories_for_header(self, categories):
        """
        Creates a string which can be added to the header - containing all
        categories.
        
        categories -- list of categories (Category).
        """
        category_string = []
        for item in categories:
            text = item.term + ";scheme=" + item.scheme
            if len(item.related) > 0:
                text += ";rel" + str(item.related)
            if item.title is not '':
                text += ";title=" + item.title
            category_string.append(text)
        return ','.join(category_string)

    def _create_attributes_for_header(self, attributes):
        """
        Create a string which can be added to the header - containing all
        attributes.
        
        attributes -- list of the attributes to add.
        """
        attr_list = []
        for item in attributes.keys():
            attr_list.append(str(item) + '=' + str(attributes[item]))
        return ','.join(attr_list)

    def _create_links_for_header(self, resource):
        """
        Create a string which can be added to the header - containing all
        the links & links to actions.
        
        resource -- the resource wo create all links for.
        """
        # TODO: add links
        action_list = []
        for item in resource.actions:
            action_list.append("</" + resource.id + ";action="
                               + item.categories[0].term + ">")
        return ','.join(action_list)

    def to_action(self, http_data):
        if http_data is None:
            raise MissingCategoriesException("Header cannot be None!")

        try:
            categories = self._get_categories_from_header(http_data.header)
        except MissingCategoriesException:
            raise

        action = Action()
        action.categories = categories

        # dropping data in the body :-)
        return action

    def to_resource(self, key, http_data):
        if key is None or http_data is None:
            raise MissingCategoriesException('Header or key cannot be None!')

        # parse categories
        try:
            categories = self._get_categories_from_header(http_data.header)
        except MissingCategoriesException:
            raise

        res = Resource()
        res.id = key
        res.categories = categories
        res.attributes = self._get_attributes_from_header(http_data.header)

        # append data from body - might be needed for OVF files etc.
        if http_data.body is not '':
            res.data = http_data.body
        return res

    def from_resource(self, resource):
        res = HTTPData
        # add links and categories to header
        res.header['Category'] = self._create_categories_for_header(resource.categories)
        # add attributes
        attr_tmp = self._create_attributes_for_header(resource.attributes)
        if attr_tmp is not '':
            res.header['Attribute'] = attr_tmp
        else:
            try:
                res.header.pop('Attribute')
            except KeyError:
                pass
        # add links & actions
        link_tmp = self._create_links_for_header(resource)
        if link_tmp is not '':
            res.header['Link'] = link_tmp
        else:
            try:
                res.header.pop('Link')
            except KeyError:
                pass
        # data to body
        res.body = resource.data
        return res

class RDFParser(Parser):
    """
    A to be done parser for RDF/RDFa documents.
    """
    pass
