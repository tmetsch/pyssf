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
A skeleton implementation for OCCI infrastructure.

Created on Dec 7, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.backends import Backend
from pyocci.core import Kind, Resource, Action, Category, Mixin, Link
from pyocci.service import LinkBackend

class Compute(Backend):

    start_action = Action()
    start_action_cat = Category()
    start_action_cat.attributes = []
    start_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/compute/action'
    start_action_cat.term = 'start'
    start_action_cat.title = 'Start a compute instance'
    start_action.kind = start_action_cat

    stop_action = Action()
    stop_action_cat = Category()
    stop_action_cat.attributes = ['method']
    stop_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/compute/action'
    stop_action_cat.term = 'stop'
    stop_action_cat.title = 'Stop a compute instance'
    stop_action.kind = stop_action_cat

    restart_action = Action()
    restart_action_cat = Category()
    restart_action_cat.attributes = ['method']
    restart_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/compute/action'
    restart_action_cat.term = 'restart'
    restart_action_cat.title = 'Restart a compute instance'
    restart_action.kind = restart_action_cat

    suspend_action = Action()
    suspend_action_cat = Category()
    suspend_action_cat.attributes = ['method']
    suspend_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/compute/action'
    suspend_action_cat.term = 'suspend'
    suspend_action_cat.title = 'Suspend a compute instance'
    suspend_action.kind = suspend_action_cat

    kind = Kind()
    kind.actions = [start_action, stop_action, restart_action, suspend_action]
    kind.attributes = ['occi.compute.architecture', 'occi.compute.cores', 'occi.compute.hostname', 'occi.compute.speed', 'occi.compute.memory', 'occi.compute.state']
    kind.location = '/compute/'
    kind.related = [Resource.category]
    kind.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    kind.term = 'compute'
    kind.title = 'A compute instance'

    def create(self, entity):
        # e.g. check if all needed attributes are defined...

        # adding some default dummy values:
        entity.attributes['occi.compute.architecture'] = 'x86'
        entity.attributes['occi.compute.cores'] = '2'
        entity.attributes['occi.compute.hostname'] = 'dummy'
        entity.attributes['occi.compute.speed'] = '1'
        entity.attributes['occi.compute.memory'] = '2'

        # trigger your hypervisor to start...
        entity.attributes['occi.compute.state'] = 'inactive'
        entity.actions = [self.start_action]
        print 'Creating the virtual machine'

    def retrieve(self, entity):
        # trigger your hypervisor to get most up to date information

        # add up to date actions...
        if entity.attributes['occi.compute.state'] == 'inactive':
            entity.actions = [self.start_action]
        if entity.attributes['occi.compute.state'] == 'active':
            entity.actions = [self.stop_action, self.suspend_action]
        if entity.attributes['occi.compute.state'] == 'suspended':
            entity.actions = [self.start_action]

    def update(self, old_entity, new_entity):
        # here you can check what information from new_entity you wanna bring 
        # into old_entity

        # trigger your hypervisor and push most recent information
        pass

    def delete(self, entity):
        # call the hypervisor to delete this VM...
        print 'Removing representation of virtual maching with id: ' + entity.identifier

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == self.start_action_cat:
            entity.attributes['occi.compute.state'] = 'active'
            # read attributes from action and do something with it :-)
            print 'Starting virtual machine with id' + entity.identifier
        elif action.kind == self.stop_action_cat:
            entity.attributes['occi.compute.state'] = 'inactive'
            # read attributes from action and do something with it :-)
            print 'Stopping virtual machine with id' + entity.identifier
        elif action.kind == self.restart_action_cat:
            entity.attributes['occi.compute.state'] = 'active'
            # read attributes from action and do something with it :-)
            print 'Restarting virtual machine with id' + entity.identifier
        elif action.kind == self.suspend_action_cat:
            entity.attributes['occi.compute.state'] = 'suspended'
            # read attributes from action and do something with it :-)
            print 'Suspending virtual machine with id' + entity.identifier

class Network(Backend):

    up_action = Action()
    up_action_cat = Category()
    up_action_cat.attributes = []
    up_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/network/action'
    up_action_cat.term = 'up'
    up_action_cat.title = 'Bring network up'
    up_action.kind = up_action_cat

    down_action = Action()
    down_action_cat = Category()
    down_action_cat.attributes = []
    down_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/network/action'
    down_action_cat.term = 'down'
    down_action_cat.title = 'Bring network down'
    down_action.kind = down_action_cat

    kind = Kind()
    kind.actions = [up_action, down_action]
    kind.attributes = ['occi.network.vlan', 'occi.network.label', 'occi.network.state']
    kind.location = '/network/'
    kind.related = [Resource.category]
    kind.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    kind.term = 'network'
    kind.title = 'A network instance'

    def create(self, entity):
        # create a VNIC...
        entity.attributes['occi.network.vlan'] = '1'
        entity.attributes['occi.network.label'] = 'dummy interface'
        entity.attributes['occi.network.state'] = 'inactive'
        entity.actions = [self.up_action]
        print 'Creating a VNIC'

    def retrieve(self, entity):
        # update a VNIC
        if entity.attributes['occi.network.state'] == 'active':
            entity.actions = [self.down_action]
        elif entity.attributes['occi.network.state'] == 'inactive':
            entity.actions = [self.up_action]

    def update(self, old_entity, new_entity):
        # implement if needed :-)
        pass

    def delete(self, entity):
        # and deactivate it
        print 'removing a representation of a VNIC with id:' + entity.identifier

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == self.up_action_cat:
            entity.attributes['occi.network.state'] = 'active'
            # read attributes from action and do something with it :-)
            print 'Starting VNIC with id: ' + entity.identifier
        elif action.kind == self.down_action_cat:
            entity.attributes['occi.network.state'] = 'inactive'
            # read attributes from action and do something with it :-)
            print 'Stoping VNIC with id: ' + entity.identifier

class IPNetworking(Backend):

    mixin = Mixin()
    mixin.actions = []
    mixin.attributes = ['occi.network.address', 'occi.network.gateway', 'occi.network.allocation']
    mixin.location = '/network/ip/'
    mixin.related = []
    mixin.scheme = 'http://schemas.ogf.org/occi/infrastructure/network'
    mixin.term = 'ipnetwork'
    mixin.title = 'An IP network instance'

    def create(self, entity):
        # TODO: check that the kind of the entity is so that this mixin can be added...

        # assign the ip!
        entity.attributes['occi.network.address'] = '10.0.0.11'
        entity.attributes['occi.network.gateway'] = '10.0.0.1'
        entity.attributes['occi.network.allocation'] = 'a'

    def retrieve(self, entity):
        pass

    def update(self, old_entity, new_entity):
        pass

    def delete(self, entity):
        pass

    def action(self, entity, action):
        pass

class Storage(Backend):

    online_action = Action()
    online_action_cat = Category()
    online_action_cat.attributes = []
    online_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/storage/action'
    online_action_cat.term = 'online'
    online_action_cat.title = 'Bring a storage resource online'
    online_action.kind = online_action_cat

    offline_action = Action()
    offline_action_cat = Category()
    offline_action_cat.attributes = []
    offline_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/storage/action'
    offline_action_cat.term = 'offline'
    offline_action_cat.title = 'Bring a storage resource offline'
    offline_action.kind = offline_action_cat

    backup_action = Action()
    backup_action_cat = Category()
    backup_action_cat.attributes = []
    backup_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/storage/action'
    backup_action_cat.term = 'backup'
    backup_action_cat.title = 'Backup a storage resource'
    backup_action.kind = backup_action_cat

    snapshot_action = Action()
    snapshot_action_cat = Category()
    snapshot_action_cat.attributes = []
    snapshot_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/storage/action'
    snapshot_action_cat.term = 'snapshot'
    snapshot_action_cat.title = 'Snapshot a storage resource'
    snapshot_action.kind = snapshot_action_cat

    resize_action = Action()
    resize_action_cat = Category()
    resize_action_cat.attributes = ['size']
    resize_action_cat.scheme = 'http://schemas.ogf.org/occi/infrastructure/storage/action'
    resize_action_cat.term = 'resize'
    resize_action_cat.title = 'Resize a storage resource'
    resize_action.kind = resize_action_cat

    kind = Kind()
    kind.actions = [online_action, offline_action, backup_action, snapshot_action, resize_action]
    kind.attributes = ['occi.storage.size', 'occi.storage.state']
    kind.location = '/storage/'
    kind.related = [Resource.category]
    kind.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    kind.term = 'storage'
    kind.title = 'A storage instance'

    def create(self, entity):
        # create a storage container here!

        entity.attributes['occi.storage.size'] = '1'
        entity.attributes['occi.storage.state'] = 'offline'
        entity.actions = [self.online_action]
        print 'Creating a storage device'

    def retrieve(self, entity):
        # check the state and return it!

        if entity.attributes['occi.storage.state'] == 'offline':
            entity.actions = [self.online_action]
        if entity.attributes['occi.storage.state'] == 'online':
            entity.actions = [self.backup_action, self.snapshot_action, self.resize_action]

    def update(self, old_entity, new_entity):
        # might be needed...
        pass

    def delete(self, entity):
        pass

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == self.online_action_cat:
            entity.attributes['occi.storage.state'] = 'online'
            # read attributes from action and do something with it :-)
            print 'Bringing up storage with id: ' + entity.identifier
        elif action.kind == self.offline_action_cat:
            entity.attributes['occi.storage.state'] = 'offline'
            # read attributes from action and do something with it :-)
            print 'Bringing down storage with id: ' + entity.identifier
        elif action.kind == self.backup_action_cat:
            print 'Backing up...storage resource with id: ' + entity.identifier
        elif action.kind == self.snapshot_action:
            print 'Snapshooting...storage resource with id: ' + entity.identifier
        elif action.kind == self.resize_action:
            print 'Resizing...storage resource with id: ' + entity.identifier

class NetworkInterface(LinkBackend):

    kind = Kind()
    kind.actions = []
    kind.attributes = ['occi.networkinterface.state', 'occi.networkinterface.mac', 'occi.networkinterface.interface']
    kind.location = '/network/link/'
    kind.related = [Link.category]
    kind.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    kind.term = 'networkinterface'
    kind.title = 'A network interface'

    def create(self, link):
        super(NetworkInterface, self).create(link)
        link.attributes['occi.networkinterface.state'] = 'up'
        link.attributes['occi.networkinterface.mac'] = 'aa:bb:cc:dd:ee:ff'
        link.attributes['occi.networkinterface.interface'] = 'eth0'

    def delete(self, link):
        super(NetworkInterface, self).delete(link)
        link.attributes.pop('occi.networkinterface.state')
        link.attributes.pop('occi.networkinterface.mac')
        link.attributes.pop('occi.networkinterface.interface')


class StorageLink(LinkBackend):

    kind = Kind()
    kind.actions = []
    kind.attributes = ['occi.storagelink.deviceid', 'occi.storagelink.mountpoint', 'occi.storagelink.state']
    kind.location = '/storage/link/'
    kind.related = [Link.category]
    kind.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    kind.term = 'storagelink'
    kind.title = 'A storage link'

    def create(self, link):
        super(StorageLink, self).create(link)
        link.attributes['occi.storagelink.deviceid'] = 'sda1'
        link.attributes['occi.storagelink.mountpoint'] = '/'
        link.attributes['occi.storagelink.state'] = 'mounted'

    def delete(self, link):
        super(StorageLink, self).delete(link)
        link.attributes.pop('occi.storagelink.deviceid')
        link.attributes.pop('occi.storagelink.mountpoint')
        link.attributes.pop('occi.storagelink.state')

class IPNetworkingLink(Backend):

    kind = Mixin()
    kind.actions = []
    kind.attributes = ['occi.networkinterface.allocation', 'occi.networkinterface.gateway', 'occi.networkinterface.ip']
    kind.location = '/network/ip/link/'
    kind.related = [Link.category]
    kind.scheme = 'http://schemas.ogf.org/occi/infrastructure'
    kind.term = 'ipnetworkinterface'
    kind.title = 'A ip network interface'

    def create(self, entity):
        # TODO: check is parent resource has the right kind so that thie mixin can be added...

        entity.attributes['occi.networkinterface.allocation'] = 'a'
        entity.attributes['occi.networkinterface.gateway'] = '10.0.0.11'
        entity.attributes['occi.networkinterface.ip'] = '10.0.0.1'

    def retrieve(self, entity):
        pass

    def update(self, old_entity, new_entity):
        pass

    def delete(self, entity):
        entity.attributes.pop('occi.networkinterface.allocation')
        entity.attributes.pop('occi.networkinterface.gateway')
        entity.attributes.pop('occi.networkinterface.ip')

    def action(self, entity, action):
        pass
