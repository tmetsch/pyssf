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
Created on Nov 10, 2010

@author: tmetsch
'''

# disabling 'Unused import' pylint check (Needs to be imported)
# disabling 'Too few public methods' pyling check (:-))
# pylint: disable=W0611,R0903

from pyocci.service import HTTPVerbHandler
import web

class MyService():
    '''
    A simple example of how to use the pyocci WSGI compliant module.
    '''

    my_service = None

    def __init__(self):
        urls = ('/(.*)', 'HTTPVerbHandler')
        web.config.debug = False
        self.my_service = web.application(urls, globals())

    def start(self):
        '''
        Start a OCCI comliant service.
        '''
        self.my_service.run()

if __name__ == '__main__':
    SERVICE = MyService()
    SERVICE.start()
