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
Created on Jul 2, 2010

@author: tmetsch
'''

from rendering_parsers import HTTPHeaderParser, HTTPData
import uuid
import web

urls = (
    '/(.*)', 'ResourceHandler'
)
app = web.application(urls, globals())

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

class PersistentResourceDictionary(dict):
    """
    Persistently stores the dictionary to a database to be failsafe.
    
    http://docs.python.org/library/shelve.html
    """
    pass

class HTTPHandler:
    # TODO: overall add auth, and key validation
    # TODO: queries
    # TODO: handle actions

    def POST(self, name, *data):
        # create a new sub resource
        request = HTTPData(web.ctx.env, web.data())
        name = str(name)
        if self.resource_exists(name) is True:
            name += str(uuid.uuid4())
            return self.create_resource(str(name), request)
        else:
            return web.NotFound("Couldn't create sub resource of non-existing resource.")

    def GET(self, name, *data):
        # return resource representation (and act based on mime-types)
        try:
            request = HTTPData(web.ctx.env, web.data())
        except:
            request = HTTPData(web.ctx.env, None)
        name = str(name)
        return self.return_resource(name, request)

    def PUT(self, name = None, *data):
        # if exists - update; else create
        request = HTTPData(web.ctx.env, web.data())
        name = str(name)
        if self.resource_exists(name) is True:
            return self.update_resource(name, request)
        else:
            return self.create_resource(name, request)

    def DELETE(self, name):
        # delete a resource representation
        if self.resource_exists(name):
            return self.delete_resource(str(name))
        else:
            return web.NotFound("Resource doesn't exist.")

class ResourceHandler(HTTPHandler):
    #TODO insert backend here

    resources = NonPersistentResourceDictionary()

    def create_resource(self, key, data):
        # trigger backend to do his magic
        self.resources[key] = data
        return web.header('Location', '/' + key)

    def return_resource(self, key, data):
        # TODO: handle results based on data gives...
        if key is '' or key[-1:] is '/':
            return 'TODO: Listing sub resources...'
        else:
            try:
                # trigger backend to get resource
                # TODO: set headers
                res = self.resources[key]
                return res.body
            except KeyError:
                return web.NotFound()

    def update_resource(self, key, data):
        # trigger backend and tell him there was an update
        self.resources[key] = data

    def delete_resource(self, key):
        try:
            # trigger backend to delete
            del(self.resources[key])
        except KeyError:
            return web.NotFound()

    def resource_exists(self, key):
        if self.resources.has_key(key) or key is '':
            return True
        else:
            return False

if __name__ == "__main__":
    app.run()
