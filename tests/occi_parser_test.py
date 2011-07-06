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
# disabling 'Line too long' pylint check (Concatenating is worse)
# disabling 'Too many public methods' pylint check (unittest's fault)
# pylint: disable=C0103,C0301,R0904

from occi import registry
from occi.core_model import Action, Kind, Resource, Link
from occi.protocol import parser
import unittest


class TestParser(unittest.TestCase):
    '''
    Test for the parser.
    '''

    start_action = Action('http://schemas.ogf.org/occi/infrastructure#',
                          'start')
    compute = Kind('http://schemas.ogf.org/occi/infrastructure#',
                       'compute', title='A OCCI compute...',
                       attributes={'occi.compute.cores': '',
                                   'occi.compute.state': 'immutable',
                                   'occi.compute.memory': 'required'},
                   related=[Resource.kind],
                   actions=[start_action])
    network_link = Kind('http://schemas.ogf.org/occi/infrastructure#',
                        'networkinterface',
                        related=[Link.kind]
                        )

    source = Resource('/1', compute, [])
    target = Resource('/2', compute, [])

    def setUp(self):
        registry.RESOURCES = {self.source.identifier: self.source,
                              self.target.identifier: self.target}
        registry.BACKENDS[self.start_action] = None
        registry.BACKENDS[self.compute] = None
        registry.BACKENDS[self.network_link] = None

    def tearDown(self):
        registry.BACKENDS = {}

    #==========================================================================
    # Success
    #==========================================================================

    # TBD

    #==========================================================================
    # Failure
    #==========================================================================

    def test_get_category_for_failure(self):
        '''
        Test with faulty category.
        '''
        self.assertRaises(AttributeError, parser.get_category, 'bla')

    #==========================================================================
    # Sanity
    #==========================================================================

    def test_get_category_for_sanity(self):
        '''
        Simple sanity check...
        '''
        res = parser.get_category(parser.get_category_str(self.compute))
        self.assertEqual(res, self.compute)

    def test_get_link_for_sanity(self):
        '''
        Verifies that source and target are set...
        '''
        link_string = '</2>; rel="http://schemas.ogf.org/occi/infrastructure#network";  category="http://schemas.ogf.org/occi/infrastructure#networkinterface"; occi.networkinterface.interface="eth0"; occi.networkinterface.mac="00:11:22:33:44:55"; occi.networkinterface.state="active";'
        link = parser.get_link(link_string, self.source)
        self.assertEquals(link.identifier, None)
        self.assertEquals(link.kind, self.network_link)
        self.assertEquals(link.source, self.source)
        self.assertEquals(link.target, self.target)
        self.assertTrue(len(link.attributes) == 3)
