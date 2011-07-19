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

from occi import registry
from occi.service import OCCI
import threading
import unittest


class ServiceThread(threading.Thread):
    '''
    Simple thread to test service.
    '''

    def __init__(self, service):
        threading.Thread.__init__(self)
        self.service = service

    def run(self):
        self.service.start(8888)


class TestService(unittest.TestCase):
    '''
    Test the service extension point.
    '''

    def setUp(self):
        self.service = OCCI()

    def test_init_for_sanity(self):
        '''
        Test constructor and initialization of service.
        '''
        OCCI()
        self.assertTrue('text/occi' in registry.RENDERINGS)
        self.assertTrue('text/plain' in registry.RENDERINGS)
        self.assertTrue('text/uri-list' in registry.RENDERINGS)
        self.assertTrue('text/html' in registry.RENDERINGS)

    def test_register_backend_for_sanity(self):
        '''
        Test registration.
        '''
        self.service.register_backend('foo', 'bar')
        self.assertTrue(registry.BACKENDS['foo'] == 'bar')