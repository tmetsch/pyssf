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
The OCCI Infrastructure extension.

Created on Jul 20, 2011

@author: tmetsch
'''

from occi.core_model import Action, Kind, Resource, Mixin, Link

#==============================================================================
# Compute
#==============================================================================

START = Action('http://schemas.ogf.org/occi/infrastructure/compute/action#',
               'start', 'Start a compute resource')

STOP = Action('http://schemas.ogf.org/occi/infrastructure/compute/action#',
              'stop', 'Stop a compute resource', {'method': ''})

RESTART = Action('http://schemas.ogf.org/occi/infrastructure/compute/action#',
                 'restart', 'Restart a compute resource', {'method': ''})

SUSPEND = Action('http://schemas.ogf.org/occi/infrastructure/compute/action#',
                 'suspend', 'Suspend a compute resource', {'method': ''})

COMPUTE_ATTRIBUTES = {'occi.compute.architecture': '',
                      'occi.compute.cores': '',
                      'occi.compute.hostname': '',
                      'occi.compute.speed': '',
                      'occi.compute.memory': '',
                      'occi.compute.state': 'immutable'}

COMPUTE = Kind('http://schemas.ogf.org/occi/infrastructure#',
               'compute',
               [Resource.kind],
               [START, STOP, RESTART, SUSPEND],
               'Compute Resource',
               COMPUTE_ATTRIBUTES,
               '/compute/')

#==============================================================================
# Network
#==============================================================================

UP = Action('http://schemas.ogf.org/occi/infrastructure/network/action#',
            'up', 'Bring up a network resource')

DOWN = Action('http://schemas.ogf.org/occi/infrastructure/network/action#',
              'down', 'Bring down a network resource')

NETWORK_ATTRIBUTES = {'occi.network.vlan': '',
                      'occi.network.label': '',
                      'occi.network.state': 'immutable'}

NETWORK = Kind('http://schemas.ogf.org/occi/infrastructure#',
               'network',
               [Resource.kind],
               [UP, DOWN],
               'Network Resource',
               NETWORK_ATTRIBUTES,
               '/network/')

#IP networking mixin

IPNETWORK_ATTRIBUTES = {'occi.network.address': '',
                        'occi.network.gateway': '',
                        'occi.network.allocation': ''}

IPNETWORK = Mixin('http://schemas.ogf.org/occi/infrastructure/network#',
                  'ipnetwork', attributes=IPNETWORK_ATTRIBUTES)

#==============================================================================
# Storage
#==============================================================================

ONLINE = Action('http://schemas.ogf.org/occi/infrastructure/storage/action#',
                'online', 'Bring storage online')

OFFLINE = Action('http://schemas.ogf.org/occi/infrastructure/storage/action#',
              'offline', 'Bring storage offline')

BACKUP = Action('http://schemas.ogf.org/occi/infrastructure/storage/action#',
                'backup', 'Backup storage resource')

SNAPSHOT = Action('http://schemas.ogf.org/occi/infrastructure/storage/action#',
                  'snapshot', 'Make a snapshot of storage resource')

RESIZE = Action('http://schemas.ogf.org/occi/infrastructure/storage/action#',
                'resize', 'Resize storage resource', {'size': 'required'})

STORAGE_ATTRIBUTES = {'occi.storage.size': '',
                      'occi.storage.state': 'immutable'}

STORAGE = Kind('http://schemas.ogf.org/occi/infrastructure#',
               'storage',
               [Resource.kind],
               [ONLINE, OFFLINE, BACKUP, SNAPSHOT, RESIZE],
               'Storage Resource',
               STORAGE_ATTRIBUTES,
               '/storage/')

#==============================================================================
# Linking
#==============================================================================

NETWORKINTERFACE_ATTRIBUTES = {'occi.networkinterface.interface': 'immutable',
                               'occi.networkinterface.mac': '',
                               'occi.networkinterface.state': 'immutable'}

NETWORKINTERFACE = Kind('http://schemas.ogf.org/occi/infrastructure#',
                        'networkinterface',
                        [Link.kind],
                        [],
                        'A L2 Network Interface',
                        NETWORKINTERFACE_ATTRIBUTES,
                        '/network/interface/')

IPNETWORKINTERFACE_ATTRIBUTES = {'occi.networkinterface.address': '',
                                 'occi.networkinterface.gateway': '',
                                 'occi.networkinterface.allocation': ''}

IPNETWORKINTERFACE = Mixin('http://schemas.ogf.org/occi/infrastructure/' \
                           'networkinterface#',
                           'ipnetworkinterface',
                           [],
                           [],
                           'L3/L4 capabilities for L2 Network Interface',
                           IPNETWORKINTERFACE_ATTRIBUTES,
                           '/network/interface/ip/')

STORAGELINK_ATTRIBUTES = {'occi.storagelink.deviceid': '',
                          'occi.storagelink.mountpoint': '',
                          'occi.storagelink.state': 'immutable'}

STORAGELINK = Kind('http://schemas.ogf.org/occi/infrastructure#',
                   'storagelink',
                   [Link.kind],
                   [],
                   'A link to a storage resource',
                   STORAGELINK_ATTRIBUTES,
                   '/storage/link/')
