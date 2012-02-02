#
# Copyright (C) 2010-2012 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
Exception definitions.

Created on Nov 24, 2011

@author: tmetsch
'''


class HTTPError(Exception):
    '''
    A HTTP Error exception.
    '''

    def __init__(self, code, msg):
        '''
        Creates an HTTP Error.

        code -- the status code.
        msg -- the error message.
        '''
        Exception.__init__(self)
        self.code = code
        self.message = msg

    def __str__(self):
        return repr(self.code) + ' - ' + self.message
