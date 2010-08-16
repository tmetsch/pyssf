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

from myexceptions import MissingCategoriesException
from resource_model import Resource, Category, JobResource, Link
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

    def to_resource(self, key, http_data):
        """
        Parse the incoming data and return a Resource
        
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
        terms = []
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
                    terms.append(category.term)
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

            # add non mandatory fields
            begin = entry.find('title="')
            if begin is not - 1:
                tmp = entry[begin + 7:]
                category.title = (tmp[:tmp.find('"')])

            begin = entry.find('rel="')
            if begin is not - 1:
                tmp = entry[begin + 7:]
                rel = (tmp[:tmp.find('"')])
                category.related = rel.split(',')
            result.append(category)

        if len(result) == 0:
            raise MissingCategoriesException('No valid categories could be'
            + 'found.')
        return terms, result

    def _get_links_from_header(self, heads):
        """
        Retrieve all links from the header but doesn't look at action kinds.
        Those should not be set by the user.
        
        heads -- headers to parse the links from.
        """
        # only target in mandatory...
        result = []
        try:
            header = heads['HTTP_LINK']
        except:
            return result # this is actually okay :-)
        links = header.split(',')
        for item in links:
            link = Link()
            # find target
            begin = item.find('<')
            end = item.find('>')
            if begin < end and begin is not - 1 and end is not - 1:
                link.target = item[begin + 1:end]
            else:
                break
            # find class
            begin = item.find('class="')
            if begin is not - 1:
                tmp = item[begin + 7:]
                link_class = tmp[:tmp.find('"')]
                if link_class != 'action':
                    link.link_class = link_class
                else:
                    break

            # find rel
            begin = item.find('rel="')
            if begin is not - 1:
                tmp = item[begin + 5:]
                link.rel = (tmp[:tmp.find('"')])

            # find 
            begin = item.find('title="')
            if begin is not - 1:
                tmp = item[begin + 7:]
                link.title = (tmp[:tmp.find('"')])
            result.append(link)
        return result

    def _get_job_attributes_from_header(self, heads):
        """
        Returns a list of attributes found in the header which start with the
        'occi.drmaa.' in the key section. Otherwise returns an empty dictionary.
        
        heads -- headers to parse the attributes from.
        """
        result = {}
        for item in heads.keys():
            if item.find('HTTP_OCCI.DRMAA.') > -1:
                result[item.lstrip('HTTP_').lower()] = heads[item]
            elif item.find('HTTP_OCCI_DRMAA_') > -1:
                result['occi.drmaa.' + item[16:].lower()] = heads[item]
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
                text += ";label=" + item.title
            category_string.append(text)
        return ','.join(category_string)

    def _create_links_for_header(self, links):
        """
        Creates a string which can be added to the header - containing all
        links.
        
        links -- list of links (Link)
        """
        # only target in mandatory...
        link_string = []
        for item in links:
            text = ''
            text += '<' + item.target + '>'
            if item.link_class is not '':
                text += ';class="' + item.link_class + '"'
            if item.rel is not '':
                text += ';rel="' + item.rel + '"'
            if item.title is not '':
                text += ';title="' + item.title + '"'
            link_string.append(text)
        return ','.join(link_string)

    def to_resource(self, key, http_data):
        if key is None or http_data is None:
            raise MissingCategoriesException('Header or key cannot be None!')

        # parse categories
        try:
            terms, categories = self._get_categories_from_header(http_data.header)
        except MissingCategoriesException:
            raise

        # XXX: add more resource if needed
        try:
            terms.index('job')
            res = JobResource()
            res.attributes = self._get_job_attributes_from_header(http_data.header)
        except:
            res = Resource()

        res.id = key
        res.categories = categories
        # add links <- done by backend
        res.links = self._get_links_from_header(http_data.header)

        # append data from body - might be needed for OVF files etc.
        if http_data.body is not '':
            res.data = http_data.body
        return res

    def from_resource(self, resource):
        res = HTTPData
        # add links and categories to header
        res.header['Category'] = self._create_categories_for_header(resource.categories)
        res.header['Link'] = self._create_links_for_header(resource.links)
        # add attributes
        if isinstance(resource, JobResource):
            for item in resource.attributes.keys():
                res.header[item] = resource.attributes[item]
        # data to body
        res.body = resource.data
        return res

class RDFParser(Parser):
    pass
