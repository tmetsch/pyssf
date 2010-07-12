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

from resource_model import Resource, Category, JobResource
import re, sys

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
            categories = header.split(',')
            for entry in categories:
                category = Category()
                tmp = entry.split(';')
                # next two are mandatory and should be there!
                # do regex on url and term to check if ok 
                term = tmp[0].strip(' ')
                if re.match("^[\w\d_-]*$", term) and term is not '':
                    category.term = term
                    terms.append(category.term)
                else:
                    raise AttributeError('No valid term for given category could be found.')

                scheme = tmp[1].split('=')[-1:][0]
                if scheme.find('http') is not - 1:
                    category.scheme = scheme
                else:
                    raise AttributeError('No a valid scheme for given category could be found.')

                # add non mandatory fields
                #if tmp[2] is not KeyError:
                #    category.title = tmp[2].split('=')[-1:]
                #if tmp[3]:
                #    # TODO should be list
                #    category.related = tmp[3].split('=')[-1:]
                result.append(category)
        except KeyError, err:
            raise AttributeError('No Categories found in the HTTP Header: %s\n' % str(err))
        except IndexError, err:
            sys.stdout.write('Warning: %s\n' % str(err))
            #pass
        return terms, result

    def _get_job_attributes_from_header(self, heads):
        """
        Returns a list of attributes found in the header which start with the
        'occi.job.' in the key section. Otherwise returns an empty dictionary.
        
        heads -- headers to parse the attributes from.
        """
        result = {}
        for item in heads.keys():
            if item.find('HTTP_OCCI.JOB.') > -1:
                result[item.lstrip('HTTP_').lower()] = heads[item]
        return result

    def _create_categories_for_http_header(self, categories):
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

    def _create_links_for_http_header(self, links):
        """
        Creates a string which can be added to the header - containing all
        links.
        
        links -- list of links (Link)
        """
        link_string = []
        for item in links:
            text = '<' + item.target + '>;class="' + item.link_class + '";rel="' + item.rel + '";title="' + item.title + '"'
            link_string.append(text)
        return ','.join(link_string)

    def to_resource(self, key, http_data):
        if key is None or http_data is None:
            raise AttributeError('Header or key cannot be None!')

        # parse categories
        terms, categories = self._get_categories_from_header(http_data.header)

        # TODO: add more resource kinds if needed
        try:
            terms.index('job')
            res = JobResource()
            res.attributes = self._get_job_attributes_from_header(http_data.header)
        except Exception, err:
            res = Resource()

        res.id = key
        res.categories = categories
        # add links <- done by backend - client normally shouldn't set links

        # append data from body - might be needed for OVF files etc.
        if http_data.body is not '':
            res.data = http_data.body
        return res

    def from_resource(self, resource):
        res = HTTPData
        # add links and categories to header
        res.header['Category'] = self._create_categories_for_http_header(resource.categories)
        res.header['Link'] = self._create_links_for_http_header(resource.links)
        # add attributes
        if isinstance(resource, JobResource):
            for item in resource.attributes.keys():
                res.header[item] = resource.attributes[item]
        # data to body
        res.body = resource.data
        return res

class RDFParser(Parser):
    pass
