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
from pyrest import backends
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
        
        Needed for actions.
        
        http_data -- the incoming data.
        """
        raise NotImplementedError

    def from_categories(self, categories):
        """
        Parse given categories and return proper HTTP data.
        
        Needed for query interface.
        
        categories -- the list of categories you want to parse
        """
        raise NotImplementedError

    def to_resource(self, key, http_data):
        """
        Parse the incoming data and return a Resource.
        
        Needed for creation of resources.
        
        key -- a unique identifier.
        http_data -- the incoming data.
        """
        raise NotImplementedError

    def from_resource(self, resource):
        """
        Parse the resource and return the data in the right rendering.
        
        Needed for retrieval of resources.
        
        resource -- the Resource to get the data from.
        """
        raise NotImplementedError

    def from_resources(self, resources):
        """
        Parse a list of resources and return the data in the right rendering.
        
        Needed for listing of resources.
        
        resources -- list of resources.
        """

def _get_categories_from_header(heads):
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
            # todo log her... an exception here means - could not parse
            # no need to catch explicit exception...
            # pylint: disable=W0702
            break
        # find scheme
        begin = entry.find('scheme=')
        if begin is not - 1:
            tmp = entry[begin + 7:]
            end = tmp.find(";")
            if end != -1:
                tmp = tmp[:end]
            scheme = tmp.rstrip("\"").lstrip("\"")
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

def _get_attributes_from_header(heads):
    """
    Returns a list of attributes found in the header. Otherwise returns an
    empty dictionary.
    
    heads -- headers to parse the attributes from.
    """
    result = {}
    if 'HTTP_ATTRIBUTE' in heads.keys():
        for item in heads['HTTP_ATTRIBUTE'].split(','):
            try:
                tmp = item.split("=")
                if len(tmp[0].strip()) > 0 and len(tmp[1].strip()) > 0:
                    result[tmp[0].strip()] = tmp[1].strip()
                else:
                    break
            except IndexError:
                break
    return result

def _create_categories_for_header(categories):
    """
    Creates a string which can be added to the header - containing all
    categories.
    
    categories -- list of categories (Category).
    """
    category_string = []
    for item in categories:
        text = item.term + ";scheme=" + item.scheme
        # TODO: fix this.
        #if len(item.related) > 0:
        #    text += ";rel" + str(item.related)
        if item.title is not '':
            text += ";title=" + item.title
        category_string.append(text)
    return ','.join(category_string)

def _create_attributes_for_header(attributes):
    """
    Create a string which can be added to the header - containing all
    attributes.
    
    attributes -- list of the attributes to add.
    """
    attr_list = []
    for item in attributes.keys():
        attr_list.append(str(item) + '=' + str(attributes[item]))
    return ','.join(attr_list)

def _create_links_for_header(resource):
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

class HTTPHeaderParser(Parser):
    """
    Very simple parser which gets/puts links, categories and attributes. Handles
    content-type and accept header 'text/plain' and */*
    """
    # Note: handle multiple headers properly instead of using ,

    content_type = '*/*'

    def to_action(self, http_data):
        if http_data is None:
            raise MissingCategoriesException("Header cannot be None!")

        try:
            categories = _get_categories_from_header(http_data.header)
        except MissingCategoriesException:
            raise

        action = Action()
        action.categories = categories

        # TODO: handle attributes of actions!

        # dropping data in the body :-)
        return action

    def from_categories(self, categories):
        if categories is None:
            raise AttributeError("Categories cannot be empty!")
        heads = {}
        res = _create_categories_for_header(categories)
        if len(res) > 0:
            heads['Category'] = res
        return HTTPData(heads, None)

    def to_resource(self, key, http_data):
        if key is None or http_data is None:
            raise MissingCategoriesException('Header or key cannot be None!')

        # parse categories
        try:
            categories = _get_categories_from_header(http_data.header)
        except MissingCategoriesException:
            raise

        res = Resource()
        res.id = key
        res.categories = categories
        res.attributes = _get_attributes_from_header(http_data.header)

        # append data from body - might be needed for OVF files etc.
        if http_data.body is not '':
            res.data = http_data.body
        return res

    def from_resource(self, resource):
        heads = {}
        # add links and categories to header
        heads['Category'] = _create_categories_for_header(resource.categories)
        # add attributes
        attr_tmp = _create_attributes_for_header(resource.attributes)
        if attr_tmp is not '':
            heads['Attribute'] = attr_tmp
        else:
            try:
                heads.pop('Attribute')
            except KeyError:
                pass
        # add links & actions
        link_tmp = _create_links_for_header(resource)
        if link_tmp is not '':
            heads['Link'] = link_tmp
        else:
            try:
                heads.pop('Link')
            except KeyError:
                pass
        # data to body
        body = resource.data
        return HTTPData(heads, body)

    def from_resources(self, resources):
        heads = {}
        res = []
        for resource in resources:
            res.append('/' + resource.id)
        if len(res) > 0:
            heads['Location'] = ','.join(res)
        body = ''
        return HTTPData(heads, body)

class HTTPTextParser(HTTPHeaderParser):

    content_type = "text/plain"

    def from_categories(self, categories):
        if categories is None:
            raise AttributeError("Categories cannot be empty!")
        heads = {}
        heads['Content-type'] = self.content_type
        res = _create_categories_for_header(categories).split(',')
        body = ''
        for item in res:
            body += 'Category:' + item + '\n'
        return HTTPData(heads, body)

    def from_resources(self, resources):
        heads = {}
        heads['Content-type'] = self.content_type
        res = []
        for resource in resources:
            res.append('Location:/' + resource.id)
        return HTTPData(heads, '\n'.join(res))

    # TODO: add to and from resource and test it...

class HTTPListParser(Parser):
    """
    Very simple parser which handles 'text/uri-list' request. can only do
    get(s) aka from(s)
    """

    content_type = 'text/uri-list'

    def to_action(self, http_data):
        raise NotImplementedError("This rendering cannot handle "
                                  + "POST/PUT requests.")

    def to_resource(self, key, http_data):
        raise NotImplementedError("This rendering cannot handle "
                                  + "POST/PUT requests.")

    def from_resource(self, resource):
        raise NotImplementedError("This rendering cannot handle "
                                  + "a GET on a single resource.")

    def from_categories(self, categories):
        if categories is None:
            raise AttributeError("Categories cannot be empty!")
        heads = {}
        heads['Content-type'] = self.content_type
        body = []
        for category in categories:
            body.append(category.scheme + category.term)
        return HTTPData(heads, '\n'.join(body))

    def from_resources(self, resources):
        heads = {}
        heads['Content-type'] = self.content_type
        res = []
        body = ''
        for resource in resources:
            res.append('/' + resource.id)
        if len(res) > 0:
            body = '\n'.join(res)
        return HTTPData(heads, body)

class HTTPHTMLParser(Parser):
    """
    Simple parser which displays categories and resource in a format which a
    browser can understand.
    """

    css_string = "body {font-family: 'Ubuntu Beta', 'Bitstream Vera Sans', 'DejaVu Sans', Tahoma, sans-serif; font-size: 0.6em; color: black; max-width: 500px; border: 1px solid #888; padding:10px;} table {font-size: 1.1em;border:0px solid white; width: 100%;} th {background-color:#73c167;color:white;padding: 5px;} td {background-color:#eee;color:black;padding: 5px;} strong {color:#73c167;} form {border: 1px solid #73c167;padding: 10px;}"
    content_type = 'text/html'

    def to_action(self, http_data):
        heads = {}

        tmp = http_data.body.replace("%3B", ";").replace("%2F", '/').replace("%3D", "=").replace("%23", "#").replace("%22", "\"").replace("%3A", ":").split("&")[0]

        heads['HTTP_CATEGORY'] = '='.join(tmp.split('=')[1:])

        cats = _get_categories_from_header(heads)

        action = Action
        action.categories = cats

        return action

    def to_resource(self, key, http_data):
        heads = {}
        res = Resource()
        try:
            tmp = http_data.body.replace("%3B", ";").replace("%2F", '/').replace("%3D", "=").replace("%23", "#").replace("%22", "\"").replace("%3A", ":").split("&")[0]

            heads['HTTP_CATEGORY'] = '='.join(tmp.split('=')[1:])

            tmp = http_data.body.replace("%3B", ";").replace("%2F", '/').replace("%3D", "=").replace("%23", "#").replace("%22", "\"").replace("%3A", ":").replace("%2C", ",").split("&")[1]

            heads['HTTP_ATTRIBUTE'] = '='.join(tmp.split('=')[1:])

            cats = _get_categories_from_header(heads)
            attr = _get_attributes_from_header(heads)
        except (IndexError, MissingCategoriesException):
            raise MissingCategoriesException("Could not parse the body of the document.")

        res.id = key
        res.categories = cats

        if len(attr) > 0:
            res.attributes = attr

        return res

    def from_categories(self, categories):
        heads = {}
        heads['Content-type'] = self.content_type
        body = " <! DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\"><html><head><style type=\"text/css\">" + self.css_string + "</style><title>Registered Categories</title></head><body>"
        body += "<p><em><a href=\"/\">Home</a></em></p>"
        body += "<h1>Registered Categories:</h1>"

        for cat in categories:
            if cat.title is not '':
                body += "<h2>" + cat.title + "</h2>"
            else:
                body += "<h2>" + cat.term + "</h2>"
            body += "<table>"
            body += "<tr><th>Term</th><td>" + cat.term + "</td></tr>"
            body += "<tr><th>Scheme</th><td><a href=\"" + cat.scheme + "\">" + cat.scheme + "</a></td></tr>"

            if cat.title is not '':
                body += "<tr><th>Title</th><td>" + cat.title + "</td></tr>"

            if len(cat.attributes) > 0:
                body += "<tr><th>Attributes</th><td>"
                for item in cat.attributes:
                    body += item + '<br />'
                body += "</td></tr>"

            if len(cat.related) > 0:
                body += "<tr><th>Related</th><td>"
                for item in cat.related:
                    body += "<a href=\"" + item.scheme + item.term + "\">" + item.scheme + item.term + "</a><br />"
                body += "</td></tr>"

            body += "</table>"

        body += "</body></html>"
        return HTTPData(heads, body)

    def from_resource(self, resource):
        heads = {}
        heads['Content-type'] = self.content_type

        body = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\"><html><head><style type=\"text/css\">" + self.css_string + "</style><title>HTML Rendering of OCCI Resource: " + resource.id + "</title></head><body>"

        body += "<p><em><a href=\"/\">Home</a></em></p>"

        body += "<h1>Resource description:</h1>"

        body += "<p>Id: <strong>" + resource.id + "</strong></p>"

        body += "<h2>Assigned Categories:</h2>"
        body += "<table><tr><th>Term</th><th>Scheme</th></tr>"
        for category in resource.categories:
            body += ("<tr><td>" + category.term + "</td><td><a href=\""
                     + category.scheme + "\">" + category.scheme
                     + "</a></td></tr>")
        body += "</table>"

        body += "<h2>Assigned Links / Actions:</h2>"
        body += "<table><tr><th>Type</th><th>URL</th><th>...</th></tr>"
        for link in resource.links:
            body += ("<tr><td>Link</td><td><a href=\"" + link.target + "\">"
                     + link.target + "</a></td></tr>")

        for action in resource.actions:
            body += ("<tr><td>Action</td><td><a href=\"/" + resource.id + ";action=" + action.categories[0].term + "\">/" + resource.id + ";action=" + action.categories[0].term + "</a></td>")
            body += "<td><form method=\"post\" action=/" + resource.id + ";action=" + action.categories[0].term + ">"
            body += "<input type=\"hidden\" name=\"Category\" value='" + action.categories[0].term + ";scheme=\"" + action.categories[0].scheme + "\"' />"
            body += "<input type=\"submit\" value=\"Trigger\" /></form></td></tr>"

        body += "</table>"

        body += "<h2>Assigned Attributes:</h2>"
        body += "<table><tr><th>Key</th><th>Value</th></tr>"
        for item in resource.attributes.keys():
            body += ("<tr><td>" + item + "</td><td>"
                     + resource.attributes[item] + "</td></tr>")
        body += "</table>"

        if len(backends.REGISTERED_BACKENDS) > 0:
            body += "<h2>Create Sub-Resource</h2>"
            body += "<form name=\"input\" action=\"\" method=\"post\">"
            body += "Category: <select name=\"Category\">"
            for item in backends.REGISTERED_BACKENDS.keys():
                body += "<option value='" + item.term + ";scheme=\"" + item.scheme + "\"'>" + item.scheme + item.term + "</option>"
            body += "</select>"
            body += "<br />CSV Attribute List: <input type=\"text\" name=\"Attribute\" value=\"\" />"
            body += "<br /><input type=\"submit\" value=\"Create\" /></form> "

        body += "</body></html>"

        return HTTPData(heads, body)

    def from_resources(self, resources):
        heads = {}
        heads['Content-type'] = self.content_type

        body = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\"><html><head><style type=\"text/css\">" + self.css_string + "</style><title>HTML Rendering of OCCI Resources</title></head><body>"

        body += "<p><em><a href=\"/\">Home</a></em></p>"

        body += "<h1>pyREST OCCI Implementation</h1>"

        body += "<h2>Query Interface</h2>"
        body += "<p><a href=\"/-/\">Check Query Interface</a></p>"

        body += "<h2>Your Resources</h2>"
        body += "<table><tr><th>Link</th><th>Term</th></tr>"
        for res in resources:
            categories = []
            for cat in res.categories:
                categories.append(cat.term)
            body += "<tr><td><a href=\"/" + res.id + "\">" + res.id + "</a></td><td>" + ','.join(categories) + "</td></tr>"
        body += "</table>"

        if len(backends.REGISTERED_BACKENDS) > 0:
            body += "<h2>Create Sub-Resource</h2>"
            body += "<form name=\"input\" action=\"\" method=\"post\">"
            body += "Category: <select name=\"Category\">"
            for item in backends.REGISTERED_BACKENDS.keys():
                body += "<option value='" + item.term + ";scheme=\"" + item.scheme + "\"'>" + item.scheme + item.term + "</option>"
            body += "</select>"
            body += "<br />CSV Attribute List: <input type=\"text\" name=\"Attribute\" value=\"\" />"
            body += "<br /><input type=\"submit\" value=\"Create\" /></form> "

        body += "</body></html>"

        return HTTPData(heads, body)

#class RDFParser(Parser):
#    """
#    A to be done parser for RDF/RDFa documents.
#    """
#    pass
