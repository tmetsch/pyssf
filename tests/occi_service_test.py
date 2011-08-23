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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
Module to test the parser.

Created on Jul 4, 2011

@author: tmetsch
'''

# disabling 'Invalid name' pylint check (unittest's fault)
# disabling 'Too many public methods' pylint check (unittest's fault)
# pylint: disable=C0103,R0904

from occi.backend import KindBackend, MixinBackend, ActionBackend
from occi.extensions.infrastructure import COMPUTE, IPNETWORKINTERFACE, START
from occi.registry import NonePersistentRegistry
from occi.service import OCCI
import tornado
import unittest


class TestService(unittest.TestCase):
    '''
    Test the service extension point.
    '''

    registry = NonePersistentRegistry()

    def setUp(self):
        self.service = OCCI()

    def test_init_for_sanity(self):
        '''
        Test constructor and initialization of service.
        '''
        self.assertTrue(self.registry.get_renderer('text/occi'))
        self.assertTrue(self.registry.get_renderer('text/plain'))
        self.assertTrue(self.registry.get_renderer('text/uri-list'))
        self.assertTrue(self.registry.get_renderer('text/html'))

        OCCI(registry=NonePersistentRegistry())

    def test_register_backend_for_failure(self):
        '''
        Test registration.
        '''
        back1 = MixinBackend()
        back2 = ActionBackend()
        self.assertRaises(AttributeError, self.service.register_backend,
                          COMPUTE, back1)
        self.assertRaises(AttributeError, self.service.register_backend,
                          COMPUTE, back2)
        try:
            OCCI(registry=dict())
        except AttributeError:
            pass
        else:
            self.assertFalse(True, 'Exception not thrown...')

    def test_register_backend_for_sanity(self):
        '''
        Test registration.
        '''
        back = KindBackend()
        back1 = MixinBackend()
        back2 = ActionBackend()
        self.service.register_backend(COMPUTE, back)
        self.service.register_backend(IPNETWORKINTERFACE, back1)
        self.service.register_backend(START, back2)

        self.assertTrue(self.registry.get_backend(COMPUTE) == back)
        self.assertTrue(self.registry.get_backend(IPNETWORKINTERFACE) == back1)
        self.assertTrue(self.registry.get_backend(START) == back2)

    def test_start_for_success(self):
        '''
        Just here to reach 100% code coverage :-)
        '''
        self.service.http_server.listen = fake_listen
        tornado.ioloop.IOLoop.instance = fake_ioloop
        self.service.start(1010)


class fake_ioloop(object):
    '''
    Fake io loop for tornado.
    '''

    # pylint: disable=R0903

    def start(self):
        '''
        Start.
        '''
        pass


def fake_listen(port):
    '''
    fake function to emulate listen...

    port -- A random nr.
    '''

    # pylint: disable=W0613

    pass
