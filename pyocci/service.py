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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
Implementation for an OCCI compliant service.

Created on Nov 10, 2010

@author: tmetsch
'''

import web

def extract_http_data():
    '''
    Extracts all necesarry information from the HTTP envelop. Minimize the data
    which is carried aroud inside of the service. Also ensures that the names
    are always equal - When deployed in Apache the names of the Headers change.
    '''
    # FIXME: check for names when deployed in Apache...
    result = {}
    print web.ctx.env
    # Cherrypy server naming...
    if 'HTTP_CATEGORY' in web.ctx.env:
        result['Category'] = web.ctx.env['HTTP_CATEGORY']
    if 'HTTP_LINK' in web.ctx.env:
        result['Link'] = web.ctx.env['HTTP_LINK']
    if 'HTTP_X_OCCI_ATTRIBUTE' in web.ctx.env:
        result['Attribute'] = web.ctx.env['HTTP_X_OCCI_ATTRIBUTE']
    return result, repr(web.data())

class HTTPVerbHandler(object):
    '''
    Handles basic HTTP operations. To achieve this it will make use of WSGI and
    the web.py framework.
    '''

    # disabling 'Invalid name' pylint check (Given by web.py)
    # pylint: disable=C0103

    def POST(self, key):
        '''
        Handles POST operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        headers, body = extract_http_data();
        print(headers)
        print(body)
        # trigger actions

        # mixins in loc N/A

        # kind in loc (create new entity - res, link)

        # loc = query (create a new mixin)

        web.OK()

    def PUT(self, key):
        '''
        Handles PUT operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        # mixins in loc (add entity - res, link to mixin)

        # kind in loc (create entity - res, link)

        # loc = query (N/A)

        print('PUT called on %s', key)

    def GET(self, key):
        '''
        Handles GET operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        # mixins in loc (return redirects to entities)

        # kind in loc (return locations of entitires)

        # loc = query (return listing of all categories)

        print('GET called on %s', key)

    def DELETE(self, key):
        '''
        Handles DELETE operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        # mixins in loc (remove entity from mixin)

        # kind in loc (delete entitiy)

        # loc = query (delete user degined-mixin)

        print('DELETE called on %s', key)
