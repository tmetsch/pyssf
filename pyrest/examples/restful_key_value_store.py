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
Creates a RESTful OCCI compliant interface for a very simple key-value store. 

It demonstrates the following pyrest features:

  - RESTifying an existing application
  - Writing a backend for the pyrest service
  - Using the build-in web server to demo the service

It does NOT make use of the following features:

  - SSL or X509 certificate support
  - deployment with mod_wsgi inside of Apache
  - Security
  - Links
  - Actions

Created on Sep 20, 2010

@author: tmetsch
'''

from pyrest import backends
from pyrest.backends import Handler
from pyrest.myexceptions import MissingAttributesException
from pyrest.resource_model import Category, Resource

# need to import those - not directly called...
# pylint: disable=W0611
from pyrest.service import ResourceHandler, QueryHandler

import web

class KeyValueHandler(Handler):

    category = Category()
    category.attributes = ['keq', 'value']
    category.related = [Resource.category]
    category.scheme = 'http://example.com/occi/keyvalue#'
    category.term = 'keyvalue'
    category.title = 'A key-value Resource'

    def __init__(self):
        """
        Registers the categories this backend can handle.
        """
        # not calling super - would register twice than...
        # pylint: disable=W0231
        backends.register([self.category], self)

    def create(self, resource):
        if self.category in resource.categories:
            if not 'keq' in resource.attributes and not 'value' in resource.attributes:
                raise MissingAttributesException('Missing key and value'
                                                 + ' attributes')
        else:
            pass

    def retrieve(self, resource):
        if self.category in resource.categories:
            pass
        else:
            pass

    def update(self, resource, updated_resource):
        if self.category in updated_resource.categories:
            if not 'keq' in updated_resource.attributes and not 'value' in updated_resource.attributes:
                raise MissingAttributesException('Missing key and value'
                                                 + ' attributes')
            resource.attributes['key'] = updated_resource.attributes['key']
            resource.attributes['value'] = updated_resource.attributes['value']
        else:
            pass

    def delete(self, resource):
        if self.category in resource.categories:
            pass
        else:
            pass

    def action(self, resource, action):
        pass

# setup the service
URLS = ('/-/(.*)', 'QueryHandler', '/(.*)', 'ResourceHandler')
web.config.debug = False

# register the backend
KeyValueHandler()

# create the app...
APPLICATION = web.application(URLS, globals())

# run...
if __name__ == "__main__":
    APPLICATION.run()
