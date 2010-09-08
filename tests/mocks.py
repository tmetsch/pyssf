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
Created on Jul 20, 2010

@author: tmetsch
'''
from pyrest.backends import Handler, JobHandler
from pyrest.myexceptions import MissingActionException, SecurityException
from pyrest.resource_model import Action
from pyrest.service import SecurityHandler

class DummyBackend(Handler):

    def create(self, resource):
        action = Action()
        action.categories = [JobHandler.terminate_category]
        resource.actions = [action]

    def update(self, resource):
        pass

    def retrieve(self, resource):
        pass

    def delete(self, resource):
        pass

    def action(self, resource, action):
        if action in resource.actions:
            resource.attributes['occi.drmaa.job_state'] = 'EXIT'
            resource.actions = []
        else:
            raise MissingActionException('Non existing action called!')

class SimpleSecurityHandler(SecurityHandler):
    """
    Simple mock security handler which can authenticate & authorize users 'foo'
    and 'bar' with the password 'ssf'.
    """

    users = {'foo':'ssf', 'bar':'ssf', '/C=DE/L=Munich/O=Sun/OU=Staff/CN=Foo': '', '/C=DE/L=Munich/O=Sun/OU=Staff/CN=Bar':''}

    def authenticate(self, username, password):
        if self.users.has_key(username) and self.users[username] == password:
            pass
        else:
            raise SecurityException()
