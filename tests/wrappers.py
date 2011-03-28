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
Created on Dec 2, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.service import ResourceHandler, CollectionHandler, QueryHandler, \
    LoginHandler, LogoutHandler, BaseHandler

class TestMixin(BaseHandler):

    body = ''

    current_user = 'default'

    def __init__(self, application, request, **kwargs):
        super(TestMixin, self).__init__(application, request, **kwargs)
        self._transforms = []

    def get_output(self):
        heads, data = self._headers, self.body
        self.body = ''
        self._headers = {}
        return heads, data

    def write(self, chunk):
        self.body = chunk

class Wrapper(ResourceHandler, TestMixin):
    pass

class ListWrapper(CollectionHandler, TestMixin):
    pass

class QueryWrapper(QueryHandler, TestMixin):
    pass

#===============================================================================
# Secure Wrappers...
#===============================================================================

class SecureWrapper(Wrapper):

    current_user = None

    def get_secure_cookie(self, key):
        return self.current_user

class SecureQueryWrapper(QueryWrapper):

    current_user = ''

    def get_secure_cookie(self, key):
        return self.current_user

class SecureListWrapper(ListWrapper):

    current_user = ''

    def get_secure_cookie(self, key):
        return self.current_user

class Login(LoginHandler, TestMixin):

    current_user = ''

    def authenticate(self, user, password):
        if user == 'foo' and password == 'bar':
            return True
        elif user == 'foo2' and password == 'bar':
            return True
        else:
            return False

    def set_secure_cookie(self, key, value):
        SecureWrapper.current_user = value
        SecureQueryWrapper.current_user = value
        SecureListWrapper.current_user = value

class Logout(LogoutHandler, TestMixin):

    def clear_cookie(self, key):
        SecureWrapper.current_user = ''
        SecureQueryWrapper.current_user = ''
        SecureListWrapper.current_user = ''
