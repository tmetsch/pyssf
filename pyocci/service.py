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
        print('POST called on %s', key)
        return 'OK'

    def PUT(self, key):
        '''
        Handles PUT operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        print('PUT called on %s', key)

    def GET(self, key):
        '''
        Handles GET operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        print('GET called on %s', key)

    def DELETE(self, key):
        '''
        Handles DELETE operations.
        
        @param key: The Path of the URI.
        @type key: String
        '''
        print('DELETE called on %s', key)
