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
Implementation of an HTTP RESTful rendering of the OCCI model.

Created on Nov 11, 2010

@author: tmetsch
'''

from pyocci import registry, service
from pyocci.core import Category, Kind, Resource, Link, Action, Mixin
from pyocci.my_exceptions import ParsingException
import re
import urllib

class HTTPData(object):
    '''
    Simple class which functions as an adapter between the OCCI model and the
    HTTP rendering. Holds all information in the way an entity is rendered.
    '''

    # disabling 'Too few public methods' pylint check (just a data model)
    # pylint: disable=R0903

    def __init__(self):
        self.categories = []
        self.links = []
        self.attributes = []
        self.locations = []

class Rendering(object):
    '''
    All renderings should derive from this class.
    '''

    # disabling 'Method could be a function' pylint check
    # disabling 'Unused argument' pylint check (This is an abstract class)
    # pylint: disable=W0613,R0201

    def from_categories(self, categories):
        '''
        Render a set of categories. 
        
        @param categories: The set of categories to render.
        @type categories: list
        '''
        raise NotImplementedError()

    def from_entities(self, entities):
        '''
        Given an set of entities this method will create an HTTP representation
        of those.
        
        @param entities: A set of entities.
        @type entities: list
        '''
        raise NotImplementedError()

    def from_entity(self, entity):
        '''
        Given an entity this method will convert it into an HTTP representation
        consisting of HTTP headers and body.
        
        @param entity: The entity which needs to rendered.
        @type entity: Entity
        '''
        raise NotImplementedError()

    def get_entities(self, headers, data):
        '''
        Retrieve a list of IDs for resource instances.
        
        @param headers: The HTTP headers.
        @type headers: dict
        @param body: The HTTP body.
        @type body: str
        '''
        raise NotImplementedError()

    def login_information(self):
        '''
        Return proper information indicating how the user can login.
        '''
        raise NotImplementedError()

    def to_action(self, headers, data):
        '''
        Create an action instance.
        
        @param headers: The HTTP headers.
        @type headers: dict
        @param body: The HTTP body.
        @type body: str
        '''
        raise NotImplementedError()

    def to_categories(self, headers, data):
        '''
        Create a set of categories (for the query interface).
        
        @param headers: The HTTP headers.
        @type headers: dict
        @param body: The HTTP body.
        @type body: str
        '''
        raise NotImplementedError()

    def to_entity(self, headers, body, allow_incomplete = False,
                  defined_kind = None):
        '''
        Given the HTTP headers and the body this method will convert the HTTP
        data into an entity representation. Must return Resource or Link
        instances.
        
        @param headers: The HTTP headers.
        @type headers: dict
        @param body: The HTTP body.
        @type body: str
        @param allow_incomplete: Indicates if the rendering will be complete
                                 (create) or incomplete (update)
        @type allow_incomplete: Boolean
        '''
        raise NotImplementedError()

#===============================================================================
# Convenient routines
#===============================================================================

def _get_category(cat_string):
    '''
    Create a category instance from an string.
    
    @param cat_string: The string with RFC compliant syntac of a Category.
    @type cat_string: str
    '''

    # TODO: make use of the class attribute

    cat = Category()
    # find the term
    tmp = cat_string.split(';')
    term = tmp[0].strip()
    if re.match("^[\w\d_-]*$", term) and term is not '':
        cat.term = term.strip()
    else:
        raise ParsingException('No valid term for given category could'
                               + ' be found.')

    # find the scheme
    begin = cat_string.find('scheme=')
    if begin is not - 1:
        tmp = cat_string[begin + 7:]
        end = tmp.find(";")
        if end > -1:
            tmp = tmp[:end]
        scheme = tmp.rstrip('"').lstrip('"')
        if scheme.find('http') is not - 1:
            cat.scheme = scheme.strip().rstrip('#')
        else:
            raise ParsingException('No valid scheme for given category'
                                   + ' could be found.')

    # find the location
    begin = cat_string.find('location=')
    if begin is not - 1:
        tmp = cat_string[begin + 9:]
        end = tmp.find(";")
        if end > -1:
            tmp = tmp[:end]
        location = tmp.rstrip('"').lstrip('"')
        tmp = location
        if tmp.find('/') is 0 and tmp.rfind('/') is len(tmp) - 1:
            res = Mixin()
            res.term = cat.term
            res.scheme = cat.scheme
            res.location = location
            cat = res

    return cat

def _get_categories(category_string_list):
    '''
    Retrieve the Kind and a list of categories. Will only return those which are
    eventually registered in this service.
    
    @param category_string_list: list with OCCI compliant renderings of 
       categories
    @type category_string_list: list
    '''
    kind = None
    categories = []
    for tmp in category_string_list:
        for cat_string in tmp.split(','):
            cat = _get_category(cat_string)

            # now that we have a category try to look it up and use that objects
            for category in registry.BACKENDS.keys():
                if cat == category:
                    if isinstance(category, Kind) and kind is None:
                        kind = category
                        break
                    else:
                        categories.append(category)
                        break

            if kind is None and len(categories) is 0:
                raise ParsingException('The following category is not'
                                        + ' registered in this service: '
                                        + repr(cat))

    return kind, categories

def _get_attributes(attributes):
    '''
    Parse the Attributes.
    
    @param attributes: List of attributes
    @type attributes: list 
    '''
    tmp = {}
    for item in attributes:
        for attr in item.split(','):
            try:
                tmp[attr.split('=')[0].strip()] = attr.split('=')[1]
            except IndexError:
                raise ParsingException('Could not determine the attributes...')
    return tmp

def _from_category(kind, extended = False):
    '''
    Create a category rendering for a kind or mixin. If extended it will try to
    put in as much information as possible.
    
    @param kind: A kind of a mixin.
    @type kind: Kind or Mixin
    @param extended: Indicating wether rendering should be minimal or not.
    @type extended: boolean  
    '''
    tmp = ''
    tmp += kind.term
    tmp += ';scheme="' + kind.scheme + '#"'
    tmp += ';class="' + kind.cls_str + '"'
    if extended:
        if hasattr(kind, 'title') and kind.title is not '':
            tmp += ';title="' + kind.title + '"'
        if hasattr(kind, 'related') and len(kind.related) > 0:
            rel_list = []
            for item in kind.related:
                rel_list.append(repr(item))
            tmp += ';rel=' + ' '.join(rel_list)
        if hasattr(kind, 'location') and kind.location is not '':
            tmp += ';location=' + kind.location
        if hasattr(kind, 'attributes') and len(kind.attributes) > 0:
            tmp += ';attributes="' + ' '.join(kind.attributes) + '"'
        if hasattr(kind, 'actions') and len(kind.actions) > 0:
            action_list = []
            for item in kind.actions:
                action_list.append(repr(item))
            tmp += ';actions="' + ' '.join(action_list) + '"'
    return tmp

def _to_entity(defined_kind, kind, categories, attributes, allow_incomplete):
    '''
    Helper routine for creating a new entity.
    
    @param defined_kind: A previsously defined kind.
    @type defined_kind: Kind
    @param kind: A kind
    @type kind: Kind
    @param categories: A list of all categories.
    @type categories: list
    @param attributes: A list of all attributes.
    @type attributes: list
    @param allow_incomplete: Indicates wether rendering should be complete.
    @type allow_incomplete: boolean
    '''
    if allow_incomplete:
        kind = defined_kind
    elif kind is None:
        raise ParsingException('Could not find a Kind for this request.')

    if Resource.category in kind.related:
        entity = Resource()
        if 'summary' in attributes.keys():
            entity.summary = attributes['summary']
            attributes.pop('summary')
    elif Link.category in kind.related:
        entity = Link()
        if 'source' in attributes.keys():
            source = attributes['source']
            if source.find(registry.HOST) == 0:
                entity.source = source[len(registry.HOST):]
            else:
                entity.source = attributes['source']
            attributes.pop('source')
        if 'target' in attributes.keys():
            target = attributes['target']
            if target.find(registry.HOST) == 0:
                entity.target = target[len(registry.HOST):]
            else:
                entity.target = target
            attributes.pop('target')
    entity.kind = kind
    entity.mixins = categories
    entity.attributes = attributes
    return entity

def _from_entity(entity):
    '''
    Helper routine for rendering an entity.
    
    @param entity: The entity to create a rendering for.
    @type entity: Entity
    '''
    result = HTTPData()

    # add kind
    result.categories.append(_from_category(entity.kind))
    # mixins...
    for item in entity.mixins:
        result.categories.append(_from_category(item))

    if isinstance(entity, Resource):
        # check if summary is available...
        if entity.summary is not '':
            result.attributes.append('summary=' + entity.summary)

        if len(entity.actions) > 0:
            for action in entity.actions:
                result.links.append('<' + registry.HOST + entity.identifier
                                    + '?action=' + action.kind.term + '>')

        if len(entity.links) > 0:
            for item in entity.links:
                result.links.append('<' + registry.HOST + item.target
                                    + '>;self=' + registry.HOST
                                    + item.identifier + ';')

    elif isinstance(entity, Link):
        # source and target must be there!
        result.attributes.append('source=' + registry.HOST + entity.source)
        result.attributes.append('target=' + registry.HOST + entity.target)
    for item in entity.attributes.keys():
        result.attributes.append(item + '=' + entity.attributes[item])

    return result

#===============================================================================
# Renderings for different content types can be found below this comment
#===============================================================================

class TextPlainRendering(Rendering):
    '''
    This is a rendering which will use the HTTP body to place the information in
    an syntax and semantics as defined in the OCCI specification.
    '''

    # disabling 'Unused variable' pylint check (categories are not used all 
    #                                          the time)
    # disabling 'Method could be a function' pylint check (I want it here)
    # pylint: disable=W0612,R0201

    content_type = 'text/plain'

    def _get_data(self, body):
        '''
        Simple method to split out the information from the HTTP body.
        
        @param body: The HTML body.
        @type body: str
        '''
        data = HTTPData()
        for entry in body.split('\n'):
            if entry.find('Category:') > -1:
                data.categories.append(entry[entry.find('Category:') + 9:])
            if entry.find('X-OCCI-Attribute:') > -1:
                data.attributes.append(entry[entry.find('X-OCCI-Attribute:')
                                             + 17:])
        return data

    def from_categories(self, categories):
        headers = {}
        body = ''
        for item in categories:
            body += 'Category: ' + _from_category(item, extended = True)
            body += '\n'
        headers['Content-Type'] = self.content_type
        return headers, body

    def from_entities(self, entities):
        headers = {}
        body = ''
        for item in entities:
            body += 'X-OCCI-Location: ' + registry.HOST + item.identifier + '\n'
        headers['Content-Type'] = self.content_type
        return headers, body

    def from_entity(self, entity):
        data = _from_entity(entity)
        body = ''

        for item in data.categories:
            body += 'Category: ' + item + '\n'
        for item in data.attributes:
            body += 'X-OCCI-Attribute: ' + item + '\n'
        for item in data.links:
            body += 'Link: ' + item + '\n'

        headers = {}
        headers['Content-Type'] = self.content_type
        del(data)
        return headers, body

    def get_entities(self, headers, body):
        ids = []
        for entry in body.split('\n'):
            if entry.find('X-OCCI-Location:') > -1:
                tmp = entry[entry.find('X-OCCI-Location:') + 16:]
                for item in tmp.split(','):
                    if item.strip().find(registry.HOST) == 0:
                        ids.append(item.strip()[len(registry.HOST):])
                    else:
                        ids.append(item.strip())
        if len(ids) > 0:
            return ids
        else:
            raise ParsingException('Body does not contain any X-OCCI-Locations'
                                   + ' pointing to resource instances.')

    def login_information(self):
        html = 'Please do a POST operation with a name and pass attribute.'

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, html

    def to_action(self, headers, body):
        data = self._get_data(body)

        # Parse the data
        kind, categories = _get_categories(data.categories)

        action = None
        if len(categories) == 0:
            raise ParsingException('Could not find a Category for this'
                                   + ' request.')
        else:
            for cat in categories:
                action = Action()
                action.kind = cat
                action.attributes = _get_attributes(data.attributes)
                break

        del(data)
        return action

    def to_categories(self, headers, body):
        categories = []
        for entry in body.split('\n'):
            if entry.find('Category:') > -1:
                for item in entry[entry.find('Category:') + 9:].split(','):
                    categories.append(_get_category(item))
        if len(categories) > 0:
            return categories
        else:
            raise ParsingException('Body does not contain any categories.')

    def to_entity(self, headers, body, allow_incomplete = False,
                  defined_kind = None):
        # create a resource or link
        if allow_incomplete and defined_kind is None:
            raise ParsingException('When allowing an incomplete requests'
                                   + ' the kind must be predefined!')
        # split out the information

        data = self._get_data(body)

        # Parse the data
        kind, categories = _get_categories(data.categories)
        attributes = _get_attributes(data.attributes)

        entity = _to_entity(defined_kind, kind, categories, attributes,
                            allow_incomplete)

        del(data)
        return entity

class TextHeaderRendering(Rendering):
    '''
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    '''

    # disabling 'Unused variable' pylint check (categories are not used all 
    #                                          the time)
    # disabling 'Unused argument' pylint check (No need for body here)
    # disabling 'Method could be a function' pylint check (I want it here)
    # pylint: disable=W0612,W0613,R0201

    content_type = 'text/occi'

    def _get_data(self, headers):
        '''
        Simple method to split out the information from the HTTP headers.
        
        @param headers: The HTML headers.
        @type headers: dict
        '''
        # split out the information
        data = HTTPData()
        if 'Category' in headers.keys():
            data.categories.append(headers['Category'])
        if 'X-OCCI-Attribute' in headers.keys():
            data.attributes.append(headers['X-OCCI-Attribute'])
        return data

    def from_categories(self, categories):
        headers = {}
        tmp = []
        for item in categories:
            tmp.append(_from_category(item, extended = True))
        if len(tmp) > 0:
            headers['Category'] = ','.join(tmp)
        headers['Content-Type'] = self.content_type
        return headers, 'OK'

    def from_entities(self, entities):
        headers = {}
        tmp = []
        for item in entities:
            tmp.append(registry.HOST + item.identifier)
        if len(tmp) > 0:
            headers['X-OCCI-Location'] = ','.join(tmp)
        headers['Content-Type'] = self.content_type
        return headers, 'OK'

    def from_entity(self, entity):
        headers = {}
        data = _from_entity(entity)

        if len(data.categories) > 0:
            headers['Category'] = ','.join(data.categories)
        if len(data.attributes) > 0:
            headers['X-OCCI-Attribute'] = ','.join(data.attributes)
        if len(data.links) > 0:
            headers['Link'] = ','.join(data.links)

        headers['Content-Type'] = self.content_type
        del(data)
        return headers, 'OK'

    def get_entities(self, headers, body):
        ids = []
        if 'X-OCCI-Location' in headers.keys():
            for item in headers['X-OCCI-Location'].split(','):
                if item.strip().find(registry.HOST) == 0:
                    ids.append(item.strip()[len(registry.HOST):])
                else:
                    ids.append(item.strip())
        if len(ids) > 0:
            return ids
        else:
            raise ParsingException('Header does not contain a location.')

    def login_information(self):
        html = 'Please do a POST operation with a name and pass attribute.'

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, html

    def to_action(self, headers, body):
        data = self._get_data(headers)

        # all data...
        kind, categories = _get_categories(data.categories)
        attributes = _get_attributes(data.attributes)

        action = None
        if len(categories) == 0:
            raise ParsingException('Could not find a Category for this'
                                   + ' request.')
        else:
            for cat in categories:
                action = Action()
                action.kind = cat
                action.attributes = _get_attributes(data.attributes)
                break

        del(data)
        return action

    def to_categories(self, headers, body):
        categories = []
        if 'Category' in headers.keys():
            for item in headers['Category'].split(','):
                categories.append(_get_category(item))
        if len(categories) > 0:
            return categories
        else:
            raise ParsingException('Header does not contain a category.')

    def to_entity(self, headers, body, allow_incomplete = False,
                  defined_kind = None):
        if allow_incomplete and defined_kind is None:
            raise ParsingException('When allowing an incomplete requests the'
                                   + ' kind must be predefined!')

        # split out the information
        data = self._get_data(headers)

        # all data...
        kind, categories = _get_categories(data.categories)
        attributes = _get_attributes(data.attributes)

        entity = _to_entity(defined_kind, kind, categories, attributes,
                            allow_incomplete)

        del(data)
        return entity

class URIListRendering(Rendering):
    '''
    This rendering can handle text/uri-list requests. Cannot be used for
    creation of entities or similar.
    '''

    content_type = 'text/uri-list'
    err_msg = 'text/uri-list rendering cannot be used for this operation.'

    def from_categories(self, categories):
        body = ''
        for item in categories:
            body += str(item) + '\n'

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, body

    def from_entities(self, entities):
        body = ''
        for item in entities:
            body += registry.HOST + item.identifier + '\n'

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, body

    def from_entity(self, entity):
        raise NotImplementedError(self.err_msg)

    def get_entities(self, headers, data):
        raise NotImplementedError(self.err_msg)

    def login_information(self):
        raise NotImplementedError(self.err_msg)

    def to_action(self, headers, data):
        raise NotImplementedError(self.err_msg)

    def to_categories(self, headers, data):
        raise NotImplementedError(self.err_msg)

    def to_entity(self, headers, body, allow_incomplete = False,
                  defined_kind = None):
        raise NotImplementedError(self.err_msg)

class TextHTMLRendering(Rendering):
    '''
    This rendering will use a generic HTML rendering to represent the resources.
    '''

    # disabling 'Unused variable' pylint check (categories are not used all 
    #                                          the time)
    # disabling 'Method could be a function' pylint check (I want it here)
    # pylint: disable=W0612,R0201

    # FIXME: check if it wouldn't be better to do term;scheme=scheme instead 
    # of scheme#term

    content_type = 'text/html'

    try:
        import os
        with open(os.getenv('PYOCCI_STYLE_SHEET'), 'r') as file:
            read_data = file.read()
        css_string = read_data
    except (IOError, TypeError):
        css_string = 'body {font: .8em/normal sans-serif;}'
        css_string += 'div {padding: 1em; margin: 1em;'
        css_string += 'border: 1px solid #73c167;}'
        css_string += 'table {margin: 1em; border: 1px solid #444;}'

    def _get_data(self, body):
        '''
        Simple method to split out the information from the HTTP HTML body.
        
        @param headers: The HTML body.
        @type headers: str
        '''
        data = HTTPData()
        if body is not None:
            tmp = urllib.unquote(body).split('&')
        else:
            raise ParsingException('Body should not be empty.')

        # FIXME!!! handle incomplete request properly!
        try:
            kin = tmp[0][tmp[0].find('Category=') + 9:].split('#')
            kin = kin[1] + ';scheme=' + kin[0]
        except IndexError:
            raise ParsingException('Cannot find properely formatted data.')

        attr = None
        try:
            test = tmp[1][tmp[1].find('X-OCCI-Attribute=') + 17:]
            if test is '':
                attr = []
            else:
                attr = test.split('+')
        except IndexError:
            pass

        if kin is not None:
            data.categories.append(kin)
        if attr is not None:
            data.attributes = attr

        return data

    def from_categories(self, categories):
        html = self._create_html_head()

        html += '<h1>Registered Categories</h1>'

        sorted_cats = {}

        if len(categories) > 0:
            for cat in categories:
                tmp = self._create_category_table(cat)
                if sorted_cats.has_key(cat.scheme):
                    sorted_cats[cat.scheme] = sorted_cats[cat.scheme] + tmp
                else:
                    sorted_cats[cat.scheme] = tmp

            for scheme in sorted_cats:
                html += '<h2>' + scheme + '</h2>'
                html += sorted_cats[scheme]
        else:
            html += '<p>No categories registered</p>'

        html += self._create_html_footer()

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, html

    def from_entities(self, entities):
        html = self._create_html_head()

        html += self._create_form()

        html += '<h1>Your Resources</h1>'

        if len(entities) > 0:
            html += '<ul>'
            for entity in entities:
                html += '<li><a href="' + entity.identifier + '">'
                html += entity.identifier + '</a>'
                html += ' (<strong>Kind: </strong>' + entity.kind.term + ')'
                html += '</li>'
            html += '</ul>'
        else:
            html += '<p>No Resources found.</p>'

        html += self._create_html_footer()

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, html

    def from_entity(self, entity):
        html = self._create_html_head()

        html += self._create_form()

        html += '<h1>Resource</h1>'
        html += '<p><strong>Id: </strong>' + entity.identifier + '</p>'
        html += '<p><strong>Owner: </strong>' + repr(entity.owner) + '</p>'
        html += '<p><strong>Kind: </strong>' + repr(entity.kind) + '</p>'

        for item in entity.mixins:
            html += '<p><strong>Mixin: </strong>' + repr(item) + '</p>'

        # Attributes...
        if isinstance(entity, Resource):
            # check if summary is available...
            if entity.summary is not '':
                html += '<p><strong>Summary: </strong>'
                html += entity.summary + '</p>'

            if len(entity.actions) > 0:
                html += '<h2>Actions</h2><table>'
                for action in entity.actions:
                    html += '<tr><td>' + action.kind.term + '</td><td>'

                    html += '<form method="post" action=' + entity.identifier
                    html += '?action=' + action.kind.term + '>'
                    html += '<input type="hidden" name="Category" value='
                    html += action.kind.scheme + '#' + action.kind.term + ' />'
                    html += '<input type="submit" value="Trigger" /></form>'

                    html += '</td></tr>'
                html += '</table>'

            if len(entity.links) > 0:
                html += '<h2>Links</h2><table>'
                html += '<tr><th>Link</th><th>Target</th></tr>'
                for item in entity.links:
                    html += '<tr><td><a href="' + item.identifier + '">'
                    html += item.identifier + '</a></td>'
                    html += '<td><a href="' + item.target + '">'
                    html += item.target + '</a></td>'
                    html += '</tr>'
                html += '</table>'

        elif isinstance(entity, Link):
            # source and target must be there!
            html += '<p><strong>Source: </strong><a href="' + entity.source
            html += '">' + entity.source + '</a></p>'
            html += '<p><strong>Target: </strong><a href="' + entity.target
            html += '">' + entity.target + '</a></p>'

        if len(entity.attributes.keys()) > 0:
            html += '<h2>Attributes</h2><table>'
            for item in entity.attributes.keys():
                html += '<tr><th>' + item + '</th><td>'
                html += entity.attributes[item] + '</td></tr>'
            html += '</table>'

        html += '<h2>&nbsp;</h2>'
        html += '<input type="button" value="Back" onclick="goBack()" />'

        html += self._create_html_footer()

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, html

    def get_entities(self, headers, body):
        # This is something HTML rendering cannot do...
        raise NotImplementedError('HTML rendering does not support this.')

    def login_information(self):
        html = self._create_html_head()
        html += '<h1>Please Sign in</h1>'
        html += '<form action="/login" method="post">'
        html += 'Username: <input type="text" name="name"><br />'
        html += 'Password: <input type="password" name="pass"><br />'
        html += '<input type="submit" value="Sign in">'
        html += '</form>'
        html += self._create_html_footer()

        headers = {}
        headers['Content-Type'] = self.content_type
        return headers, html

    def to_action(self, headers, body):
        data = self._get_data(body)

        # all data...
        kind, categories = _get_categories(data.categories)

        action = None

        if len(categories) == 0:
            raise ParsingException('Could not find a Category for this'
                                   + ' request.')
        else:
            for cat in categories:
                action = Action()
                action.kind = cat
                break

        del(data)
        return action

    def to_categories(self, headers, body):
        # This is something HTML rendering cannot do...
        raise NotImplementedError('HTML rendering does not support this.')

    def to_entity(self, headers, body, allow_incomplete = False,
                  defined_kind = None):
        if allow_incomplete and defined_kind is None:
            raise ParsingException('When allowing an incomplete requests'
                                   + ' the kind must be predefined!')

        data = self._get_data(body)

        # all data...
        kind, categories = _get_categories(data.categories)
        attributes = _get_attributes(data.attributes)

        if allow_incomplete:
            kind = defined_kind

        if Resource.category in kind.related:
            entity = Resource()
            if 'summary' in attributes.keys():
                entity.summary = attributes['summary']
                attributes.pop('summary')
        elif Link.category in kind.related:
            entity = Link()
            if 'source' in attributes.keys():
                source = attributes['source']
                if source.find(registry.HOST) == 0:
                    entity.source = source[len(registry.HOST):]
                else:
                    entity.source = attributes['source']
                attributes.pop('source')
            if 'target' in attributes.keys():
                target = attributes['target']
                if target.find(registry.HOST) == 0:
                    entity.target = target[len(registry.HOST):]
                else:
                    entity.target = target
                attributes.pop('target')
        entity.kind = kind
        entity.attributes = attributes

        del(data)
        return entity

    #===========================================================================
    # Some routines for convenience
    #===========================================================================

    # disabling 'Method could be a function' pylint check (these belong here!)
    # pylint: disable=R0201

    def _create_category_table(self, category):
        '''
        Create a string containing a table with the category's information.
        '''
        tmp = '<table>'
        tmp += '<tr><th>Term</th><td>' + category.term + '</td></tr>'
        tmp += '<tr><th>Scheme</th><td>' + category.scheme + '</td></tr>'
        tmp += '<tr><th>Class</th><td>' + category.cls_str + '</td></tr>'

        if hasattr(category, 'title') and category.title is not '':
            tmp += '<tr><th>Title/th><td>' + category.title + '</td></tr>'
        if hasattr(category, 'actions') and len(category.actions) > 0:
            tmp += '<tr><th>Actions</th><td><ul>'
            for item in category.actions:
                tmp += '<li>' + item.kind.term + '</li>'
            tmp += '</ul></td></tr>'
        if hasattr(category, 'attributes') and len(category.attributes) > 0:
            tmp += '<tr><th>Attributes</th><td><ul>'
            for item in category.attributes:
                tmp += '<li>' + item + '</li>'
            tmp += '</ul></td></tr>'
        if hasattr(category, 'location') and category.location is not '':
            tmp += '<tr><th>Location</th><td><a href="'
            tmp += category.location + '">'
            tmp += category.location + '</a></td></tr>'
        if hasattr(category, 'related')and len(category.related) > 0:
            tmp += '<tr><th>related</th><td><ul>'
            for item in category.related:
                tmp += '<li>' + repr(item) + '</li>'
            tmp += '</ul></td></tr>'
        tmp += '</table>'
        return tmp

    def _create_form(self):
        '''
        Will create an HTML representation of a fieldset for creating resource
        instance.
        '''
        html = '<form name="input" action="" method="post">'
        html += '<fieldset><legend>Create a new resource</legend><p>'
        html += '<label>Kind</label><select name="Category">'

        for kind in registry.BACKENDS.keys():
            if isinstance(kind, Kind) and Action.category not in kind.related:
                html += '<option selected = "selected" value ='
                html += repr(kind) + '>' + repr(kind)
                html += '</option>'

        html += '</select></p><p><label>Attribute List</label>'
        html += '<input name="X-OCCI-Attribute" class="text" type="text" />'
        html += '</p><p><input value="Create" type="submit" /></p>'
        html += '</fieldset></form>'
        return html

    def _create_html_head(self):
        '''
        Returns a string with the first part of the HTML page.
        '''
        html = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"'
        html += '"http://www.w3.org/TR/html4/strict.dtd">'
        html += '<html>'
        html += '<head>'
        html += '<title>pyocci service - OCCI</title>'
        html += '<meta http-equiv="Content-Type"'
        html += 'content="text/html; charset=UTF-8">'
        html += '<style type="text/css">'
        html += self.css_string
        html += '</style>'
        html += '<script type="text/javascript">function goBack() {'
        html += 'window.history.back()}</script>'
        html += '</head><html>'
        html += '<div id="container">'
        html += '<div id="header">'
        html += '    <a href="/">Home</a>'
        html += '    <a href="/-/">Query Interface</a>'
        if service.AUTHENTICATION is True:
            html += '    <a href="/logout">Logout</a>'
        html += '</div>'
        html += '<div id="content">'
        return html

    def _create_html_footer(self):
        '''
        Returns a string with the last part of the HTML page.
        '''
        html = '</div>'
        html += '</div>'
        html += '<div id="footer">'
        html += 'Generated by <a href="http://pyssf.sf.net">SSF</a>'
        html += ' &copy; Platform Computing'
        html += '</div>'
        html += '</html>'
        html += '</html>'
        return html
