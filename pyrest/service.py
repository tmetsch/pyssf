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
This module contains the RESTful service itself.

Created on Jul 2, 2010

@author: tmetsch
'''

from backends import JobHandler
from rendering_parsers import HTTPHeaderParser, HTTPData
import uuid
import web


URLS = (
    # '/(.*)(;[a-zA-z]*)', 'ActionHandler'; no clue why he doesn't trigger this
    '/(.*)', 'ResourceHandler'
)
APPLICATION = web.application(URLS, globals())

class NonPersistentResourceDictionary(dict):
    """
    Overrides a dictionary - Since the resource model and rendering parsers are
    generic this is the most interesting part.
    
    Whenever a item is added, update or removed, a parser will be called to 
    update the resource description.
    
    This one now uses HTTPHeaderParser
    """
    parser = HTTPHeaderParser()

    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, key):
        item = dict.__getitem__(self, key)
        return self.parser.from_resource(item)

    def __setitem__(self, key, value):
        item = self.parser.to_resource(key, value)
        return dict.__setitem__(self, key, item)

    def __delitem__(self, key):
        return dict.__delitem__(self, key)

    def get_resource(self, key):
        """
        Returns the resource without parsing it back to HTTP data.
        """
        return dict.__getitem__(self, key)

class PersistentResourceDictionary(dict):
    """
    Persistently stores the dictionary to a database to be failsafe.
    
    http://docs.python.org/library/shelve.html
    """
    pass

class HTTPHandler(object):
    """
    Handles the very basic HTTP operations. The logic when a resource is
    created, updated or delete is handle in here.
    """

    def POST(self, name, *data):
        """
        Handles the POST request - triggers creation of a resource. Will
        return a location of the newly created resource.
        
        name -- the id of the resource.
        *data -- if available (this it the body of the HTTP message).
        """
        index = web.ctx.env['PATH_INFO'].find(';')
        if index is not - 1:
            key = web.ctx.env['PATH_INFO'][1:index]
            actionclass = web.ctx.env['PATH_INFO'][index + 1:]
            return self.trigger_action(key, actionclass)
        # create a new sub resource
        request = HTTPData(web.ctx.env, web.data())
        name = str(name)
        if self.resource_exists(name) is True:
            name += str(uuid.uuid4())
            return self.create_resource(str(name), request)
        else:
            return web.NotFound("Couldn't create sub resource of non-existing"
                                + "resource.")

    def GET(self, name, *data):
        """
        Handles the GET request - triggers the service to return information.
        
        name -- the id of the resource.
        *data -- if available (this it the body of the HTTP message).
        """
        # return resource representation (and act based on mime-types)
        try:
            request = HTTPData(web.ctx.env, web.data())
        except:
            request = HTTPData(web.ctx.env, None)
        name = str(name)
        tmp = self.return_resource(name, request)
        # following is uncool!
        if isinstance(tmp, str):
            return tmp
        if tmp is not None:
            for item in tmp.header.keys():
                web.header(item, tmp.header[item])
            return tmp.body
        else:
            return web.NotFound()

    def PUT(self, name = None, *data):
        """
        Handles the PUT request - triggers either the creation or updates a 
        resource.
        
        name -- if available (the id of the resource).
        *data -- if available (this it the body of the HTTP message).
        """
        # if exists - update; else create
        request = HTTPData(web.ctx.env, web.data())
        name = str(name)
        if self.resource_exists(name) is True:
            return self.update_resource(name, request)
        else:
            return self.create_resource(name, request)

    def DELETE(self, name):
        """
        Handles the DELETE request.
        
        name -- the id of the resource).
        """
        # delete a resource representation
        if self.resource_exists(name):
            return self.delete_resource(str(name))
        else:
            return web.NotFound("Resource doesn't exist.")

class ResourceHandler(HTTPHandler):
    """
    Manages the resources and stores them. Also triggers backend operations.
    """

    resources = NonPersistentResourceDictionary()
    backend = JobHandler()

    def create_resource(self, key, data):
        """
        Creates a resource.
        
        key -- the unique id.
        data -- the data.
        """
        try:
            self.resources[key] = data
            # trigger backend to do his magic
            self.backend.create(self.resources.get_resource(key))
            return web.header('Location', '/' + key)
        except Exception as inst:
            web.HTTPError(inst)

    def return_resource(self, key, data):
        """
        Returns a resource.
        
        key -- the unique id.
        data -- the data.
        """
        # TODO: mime types, Accept headers and listings
        if key is '' or key[-1:] is '/':
            return 'Listing sub resources...'
        else:
            try:
                # trigger backend to get resource
                res = self.resources.get_resource(key)
                self.backend.retrieve(res)
                res = self.resources[key]
                return res
            except Exception as inst:
                web.HTTPError(inst)

    def update_resource(self, key, data):
        """
        Updates a resource.
        
        key -- the unique id.
        data -- the data.
        """
        # trigger backend and tell him there was an update
        # only backend update the real resource - incl checks what can be 
        #   changed and what not :-)
        try:
            #self.resources[key] = data
            res = self.resources.get_resource(key)
            self.backend.retrieve(res)
        except Exception as inst:
            web.HTTPError(inst)

    def delete_resource(self, key):
        """
        Deletes a resource.
        
        key -- the unique id.
        data -- the data.
        """
        try:
            # trigger backend to delete
            res = self.resources.get_resource(key)
            self.backend.delete(res)
            del(self.resources[key])
        except KeyError:
            web.NotFound()
        except Exception as inst:
            web.HTTPError(inst)

    def resource_exists(self, key):
        """
        Tests if an resource exists.
        
        key -- the id to look for...
        """
        if self.resources.has_key(key) or key is '':
            return True
        else:
            return False

    def trigger_action(self, key, name):
        """
        Trigger an action in the backend system. Backend should update state
        and links if needed.
        
        key -- the id for the resource.
        name -- name of the action.
        """
        try:
            resource = self.resources.get_resource(key)
            self.backend.action(resource, name)
            web.OK()
        except KeyError:
            web.NotFound()
        except Exception as inst:
            web.HTTPError(inst)

if __name__ == "__main__":
    APPLICATION.run()

