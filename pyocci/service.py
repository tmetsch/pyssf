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
Implementation for an OCCI compliant service.

Created on Nov 10, 2010

@author: tmetsch
'''

from pyocci import registry
from pyocci.backends import Backend
from pyocci.core import Mixin
from pyocci.my_exceptions import NoEntryFoundException, ParsingException
from tornado.web import HTTPError
import sys
import tornado.web
import uuid

RESOURCES = {}
AUTHENTICATION = False

class BaseHandler(tornado.web.RequestHandler):
    '''
    Handler derived from an handler in the tornado framework. Extended with some
    convenient routines.
    '''

    # disabling 'Unused argument' pylint check (overwritten methods)
    # disabling 'Too many public methods' pylint check (tornado's fault)
    # disabling 'method could be a function' pylint check (for sanity reasons)
    # pylint: disable=R0904,W0613,R0201

    version = 'pyocci OCCI/1.1'

    def __init__(self, application, request, **kwargs):
        if registry.HOST == '':
            registry.HOST = request.protocol + '://' + request.host
        super(BaseHandler, self).__init__(application, request, **kwargs)

    def extract_http_data(self):
        '''
        Extracts all necessary information from the HTTP envelop. Minimize the
        data which is carried around inside of the service. Also ensures that
        the names are always equal - When deployed in Apache the names of the
        Headers change.
        '''
        heads = {}
        headers = self.request.headers
        if 'Category' in headers:
            heads['Category'] = headers['Category']
        if 'X-Occi-Attribute' in headers:
            heads['X-OCCI-Attribute'] = headers['X-Occi-Attribute']
        if 'X-Occi-Location' in headers:
            heads['X-OCCI-Location'] = headers['X-Occi-Location']
        if 'Link' in headers:
            heads['Link'] = headers['Link']
        if self.request.body is not '':
            body = self.request.body.strip()
        else:
            body = ''
        return heads, body

    def get_pyocci_parser(self, content_type):
        '''
        Returns the proper pyocci rendering parser.
        
        @param content_type: Either Content-Type or Accept
        @type content_type: str
        '''
        # find a parser for the data format the client provided...
        try:
            return registry.get_parser(self.request.headers[content_type])
        except KeyError:
            return registry.get_parser(registry.DEFAULT_CONTENT_TYPE)
        except NoEntryFoundException as nefe:
            raise HTTPError(400, log_message = str(nefe))

    def get_error_html(self, code, **kwargs):
        exception = sys.exc_info()[1]
        msg = str(exception)
        return msg

    def _send_response(self, heads, data):
        '''
        Prepares all information to send a response to the client.
        
        @param heads: Data which should go in the header.
        @type heads: dict
        @param data: The body of the HTTP message.
        @type data: str
        '''
        self._headers['Server'] = self.version
        if heads is not None:
            for item in heads.keys():
                self._headers[item] = heads[item]
        self.write(data)

    def get_current_user(self):
        if AUTHENTICATION is True:
            return self.get_secure_cookie("pyocci_user")
        else:
            return 'default'

    def filter_childs(self, key, resources, categories):
        '''
        Retrieve childs in a hierachy and use categories to filter the result.
        
        @param key: A key.
        @type key: str
        @param resources: A list of resources.
        @type resources: list
        @param categories: A list of categories which is used to filter.
        @type categories: list
        '''
        tmp = []
        for name in resources:
            if name.identifier.find(key) > -1 and key.endswith('/'):
                if categories is None:
                    tmp.append(name)
                elif len(categories) > 0:
                    for category in categories:
                        if category == name.kind:
                            tmp.append(name)
                        elif category in name.kind.related:
                            tmp.append(name)
                        elif category in name.mixins:
                            tmp.append(name)
        return tmp

    def get_my_resources(self):
        '''
        Returns a list of all resources belonging to the current user.
        '''
        my_resources = []
        for tmp in RESOURCES.keys():
            item = RESOURCES[tmp]
            if item.owner == self.get_current_user():
                my_resources.append(item)
        return my_resources

class ResourceHandler(BaseHandler):
    '''
    Handles basic HTTP operations. To achieve this it will make use of WSGI and
    the web.py framework.
    '''

    # disabling 'Too many public methods' pylint check (tornado's fault)
    # disabling 'Arguments number differs from ...' pylint check 
    #                                               (methods exists twice...)
    # pylint: disable=R0904,W0221

    @tornado.web.authenticated
    def post(self, key):
        headers, body = self.extract_http_data()
        parser = self.get_pyocci_parser('Content-Type')

        if self.request.uri.find('?action=') > -1:
            key = self.request.uri.split('?')[0]
            try:
                entity = RESOURCES.get(key)
                action = parser.to_action(headers, body)
                backend = registry.get_backend(action.kind)
                backend.action(entity, action)
            except (ParsingException, AttributeError) as pse:
                raise HTTPError(400, str(pse))
        else:
            # parse the request
            entity = None
            try:
                # create the entity
                entity, links = parser.to_entity(headers, body)
                entity.owner = self.get_current_user()
                key = self._create_key(entity)
                backend = registry.get_backend(entity.kind)
                backend.create(entity)

                RESOURCES[key] = entity

                # handle the links...
                for item in links:
                    backend = registry.get_backend(item.kind)
                    item.source = key
                    backend.create(item)
                    key = self._create_key(item)
                    RESOURCES[key] = item
                    item.idetifier = key
                    item.owner = self.get_current_user()

            except (ParsingException, AttributeError) as pse:
                # TODO: RESOURCES.pop(key)
                raise HTTPError(400, str(pse))

        self._send_response({'Location': registry.HOST + key}, 'OK')

    @tornado.web.authenticated
    def put(self, key):
        headers, body = self.extract_http_data()
        parser = self.get_pyocci_parser('Content-Type')

        if key in RESOURCES.keys():
            old_entity = RESOURCES[key]
            new_entity = None
            try:
                new_entity, links = parser.to_entity(headers, body,
                                              allow_incomplete = True,
                                              defined_kind = old_entity.kind)

                if self.get_current_user() != old_entity.owner:
                    raise HTTPError(401)

                backend = registry.get_backend(old_entity.kind)

                backend.update(old_entity, new_entity)
            except (ParsingException, AttributeError) as pse:
                raise HTTPError(400, str(pse))
        else:
            try:
                new_entity, links = parser.to_entity(headers, body)
                new_entity.identifier = key
                new_entity.owner = self.get_current_user()

                backend = registry.get_backend(new_entity.kind)
                backend.create(new_entity)

                RESOURCES[key] = new_entity

                # handle the links...
                for item in links:
                    backend = registry.get_backend(item.kind)
                    item.source = key
                    backend.create(item)
                    key = self._create_key(item)
                    RESOURCES[key] = item
                    item.idetifier = key
                    item.owner = self.get_current_user()

            except (ParsingException, AttributeError) as pse:
                # TODO: RESOURCES.pop(key)
                raise HTTPError(400, str(pse))

        self._send_response(None, 'OK')

    @tornado.web.authenticated
    def get(self, key):
        # find a parser for the data format the client provided...
        parser = self.get_pyocci_parser('Accept')
        headers, body = self.extract_http_data()

        if key in RESOURCES.keys():
            entity = RESOURCES[key]
            if entity.owner != self.get_current_user():
                raise HTTPError(401)

            # trigger backend to get the freshest results
            backend = registry.get_backend(entity.kind)
            backend.retrieve(entity)

            # get a rendering of this entity...
            heads, data = parser.from_entity(entity)

            self._send_response(heads, data)
        elif key == '/':
            # render a list of resources...
            categories = None
            try:
                data_parser = self.get_pyocci_parser('Content-Type')
                categories = data_parser.to_categories(headers, body)
            except (KeyError, ParsingException):
                pass

            my_resources = self.get_my_resources()

            resources = self.filter_childs(key, my_resources, categories)
            heads, data = parser.from_entities(resources)
            self._send_response(heads, data)
        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    def delete(self, key):
        if key in RESOURCES.keys():
            entity = RESOURCES[key]

            if entity.owner != self.get_current_user():
                raise HTTPError(401)

            # trigger backend to delete the resource
            backend = registry.get_backend(entity.kind)
            backend.delete(entity)

            RESOURCES.pop(key)
            self._send_response(None, 'OK')
        else:
            raise HTTPError(404)

    def _create_key(self, entity):
        '''
        Create a key with the hierarchy of the entity encapsulated.
        
        @param entity: The entity to create the key for.
        @type entity: Entity
        '''
        if entity.kind.location is not '':
            key = '/users/' + self.get_current_user() + entity.kind.location
            key += str(uuid.uuid4())
        else:
            key = '/users/' + self.get_current_user() + '/' + str(uuid.uuid4())
        entity.identifier = key
        return key

class ListHandler(BaseHandler):
    '''
    This class handles listing of resources in REST resource hierarchy and
    listing, adding and removing resource intstance from mixins.
    '''

    # disabling 'Too many public methods' pylint check (tornado's fault)
    # disabling 'Arguments number differs from ...' pylint check 
    #                                               (methods exists twice...)
    # disabling 'Method could be a function' pylint check (I want it here)
    # pylint: disable=R0904,W0221,R0201 

    def get_locations(self):
        '''
        Returns a dict with all categories which have locations.
        '''
        locations = {}
        for cat in registry.BACKENDS.keys():
            if hasattr(cat, 'location') and cat.location is not '':
                if hasattr(cat, 'owner') and cat.owner is not '':
                    if cat.owner is self.get_current_user():
                        locations[cat.location] = cat
                        break
                locations[cat.location] = cat
        return locations

    def get_all_resources_of_category(self, category, resources):
        '''
        Return all resources belonging to one category.
        
        @param category: A category
        @type category: Category
        @param resources: List of resources
        @type resources: list
        '''
        tmp = []
        for res in resources:
            if res.kind == category:
                tmp.append(res)
            elif category in res.mixins:
                tmp.append(res)
        return tmp

    @tornado.web.authenticated
    def get(self, key):
        key = '/' + key + '/'
        headers, body = self.extract_http_data()

        return_parser = self.get_pyocci_parser('Accept')
        categories = None
        try:
            data_parser = self.get_pyocci_parser('Content-Type')
            categories = data_parser.to_categories(headers, body)
        except (KeyError, ParsingException):
            pass

        locations = self.get_locations()
        resources = []

        my_resources = self.get_my_resources()

        if key in locations:
            tmp = self.get_all_resources_of_category(locations[key],
                                                     my_resources)
            resources = self.filter_childs('/', tmp, categories)
        elif key.endswith('/'):
            resources = self.filter_childs(key, my_resources, categories)

        if len(resources) > 0:
            heads, data = return_parser.from_entities(resources)
            return self._send_response(heads, data)
        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    def put(self, key):
        key = '/' + key + '/'
        headers, body = self.extract_http_data()
        # find a parser for the data format the client provided...
        parser = self.get_pyocci_parser('Content-Type')

        locations = self.get_locations()
        if key in locations:
            try:
                category = locations[key]
                entities = parser.get_entities(headers, body)
                for item in entities:
                    if item in RESOURCES.keys():
                        res = RESOURCES[item]
                        if category not in res.mixins:
                            res.mixins.append(category)
            except ParsingException as pse:
                raise HTTPError(400, log_message = str(pse))
        else:
            raise HTTPError(400, 'Put is only allowed on a location path.')

    @tornado.web.authenticated
    def delete(self, key):
        key = '/' + key + '/'
        headers, body = self.extract_http_data()
        # find a parser for the data format the client provided...
        parser = self.get_pyocci_parser('Content-Type')

        locations = self.get_locations()

        if key in locations:
            try:
                category = locations[key]
                entities = parser.get_entities(headers, body)
                for item in entities:
                    if item in RESOURCES.keys():
                        RESOURCES[item].mixins.remove(category)
            except ParsingException as pse:
                raise HTTPError(400, log_message = str(pse))
        else:
            raise HTTPError(400, 'Put is only allowed on a location path.')

class QueryHandler(BaseHandler):
    '''
    This class represents the OCCI query interface.
    '''

    # disabling 'Too many public methods' pylint check (tornado's fault)
    # pylint: disable=R0904

    @tornado.web.authenticated
    def get(self):
        headers, body = self.extract_http_data()
        parser = self.get_pyocci_parser('Content-Type')
        return_parser = self.get_pyocci_parser('Accept')

        result = []

        cats = []
        for item in registry.BACKENDS.keys():
            if isinstance(item, Mixin):
                if item.owner == self.get_current_user() or item.owner == '':
                    cats.append(item)
            else:
                cats.append(item)

        filter_cats = []
        try:
            filter_cats = parser.to_categories(headers, body)
        except ParsingException:
            pass

        if len(filter_cats) == 0:
            result = cats
        else:
            for item in cats:
                if item in filter_cats:
                    result.append(item)

        heads, data = return_parser.from_categories(result)
        self._send_response(heads, data)

    @tornado.web.authenticated
    def put(self):
        headers, body = self.extract_http_data()
        parser = self.get_pyocci_parser('Content-Type')

        try:
            categories = parser.to_categories(headers, body)
            for tmp in categories:
                if isinstance(tmp, Mixin):
                    tmp.owner = self.get_current_user()
                    registry.register_backend([tmp], MixinBackend())
                else:
                    raise ParsingException('Not a valid mixin.')
        except (ParsingException, AttributeError) as pse:
            raise HTTPError(400, log_message = str(pse))

    @tornado.web.authenticated
    def delete(self):
        headers, body = self.extract_http_data()
        parser = self.get_pyocci_parser('Content-Type')

        try:
            del_categories = parser.to_categories(headers, body)
        except ParsingException as pse:
            raise HTTPError(400, log_message = str(pse))

        for cat in registry.BACKENDS.keys():
            if cat in del_categories:
                if isinstance(cat, Mixin):
                    if cat.owner == self.get_current_user():
                        registry.unregister_backend([cat])
                        del_categories.remove(cat)
                    else:
                        raise HTTPError(401)

        if len(del_categories) > 0:
            raise HTTPError(400, log_message = 'Cannot delete these'
                            + ' categories.')

#===============================================================================
# Basic Security handlers
#===============================================================================

class LoginHandler(BaseHandler):
    '''
    Simple Handler for a login which sets a cookie for a session.
    '''

    # disabling 'Too many public methods' pylint check (tornado's fault)
    # pylint: disable=R0904

    def get(self):
        parser = self.get_pyocci_parser('Accept')
        heads, data = parser.login_information()
        self._send_response(heads, data)

    def post(self):
        username = self.get_argument('name')
        password = self.get_argument('pass')
        if self.authenticate(username, password):
            self.set_secure_cookie("pyocci_user", username)
            self.redirect("/")
        else:
            raise HTTPError(401)

    # disabling 'Unused argument' pylint check (method should be overwritten)
    # disabling 'Method could be a function' pylint check (method should be 
    #                                                      overwritten) 
    # pylint: disable=R0201,W0613

    def authenticate(self, username, password):
        '''
        Authenticates a user by username and password. Should be overwritten by
        any real implementation. This one will return False as default.
        
        @param username: The name of the user.
        @type username: str
        @param password: The password.
        @type password: str
        '''
        return False

class LogoutHandler(BaseHandler):
    '''
    Simple handler which deletes a preivously set cookie.
    '''

    # disabling 'Too many public methods' pylint check (tornado's fault)
    # pylint: disable=R0904

    URL = r'/logout'

    def get(self):
        self.clear_cookie('pyocci_user')
        self.redirect('/')

#===============================================================================
# Some Basic Backends
#===============================================================================

class MixinBackend(Backend):
    '''
    This backend is registered for each user defined Mixin. It does nothing.
    '''

    def create(self, entity):
        pass

    def retrieve(self, entity):
        pass

    def update(self, old_entity, new_entity):
        pass

    def delete(self, entity):
        pass

    def action(self, entity, action):
        pass

class LinkBackend(Backend):
    '''
    This class will be handling the basic Links. If the user defines a kind
    which relates to OCCI-Link it must derive from this class.
    '''

    def create(self, link):
        if link.source is '':
            raise AttributeError('A link needs to have a source.')
        if link.target is '':
            raise AttributeError('A link needs to have a target.')

        try:
            RESOURCES.has_key(link.target)
            src = RESOURCES[link.source]
            src.links.append(link)
        except KeyError as notfound:
            raise AttributeError('Source and target need to be valid'
                                 + ' Resources: ' + str(notfound))

    def retrieve(self, link):
        pass

    def update(self, old, new):
        if new.source is not '':
            try:
                old_src = RESOURCES[old.source]
                new_src = RESOURCES[new.source]

                old_src.links.remove(old)

                old.source = new.source
                new_src.links.append(old)

            except KeyError:
                raise AttributeError('Source and target need to be valid'
                                     + ' Resources')
        if new.target is not '':
            old.target = new.target
        if len(new.attributes.keys()) > 0:
            old.attributes = new.attributes

    def delete(self, link):
        try:
            src = RESOURCES[link.source]

            src.links.remove(link)
        except KeyError:
            raise AttributeError('Source and target need to be valid Resources')

    def action(self, entity, action):
        pass
