#!/usr/bin/env python

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
A module which setups a very simple IaaS based SERVICE.

Created on Jul 5, 2011

@author: tmetsch
'''

from occi.backend import ActionBackend, KindBackend, MixinBackend
from occi.extensions.infrastructure import START, STOP, SUSPEND, RESTART, UP, \
    DOWN, ONLINE, BACKUP, SNAPSHOT, RESIZE, OFFLINE, NETWORK, \
    NETWORKINTERFACE, COMPUTE, STORAGE, IPNETWORK, IPNETWORKINTERFACE, \
    STORAGELINK, RESOURCE_TEMPLATE, OS_TEMPLATE
from occi.wsgi import Application
from wsgiref.simple_server import make_server
from wsgiref.validate import validator


class MyBackend(KindBackend, ActionBackend):
    '''
    An very simple abstract backend which handles update and replace for
    attributes. Support for links and mixins would need to added.
    '''

    def update(self, old, new, extras):
        # here you can check what information from new_entity you wanna bring
        # into old_entity

        # trigger your hypervisor and push most recent information
        print('Updating a resource with id: ' + old.identifier)
        for item in new.attributes.keys():
            old.attributes[item] = new.attributes[item]

    def replace(self, old, new, extras):
        print('Replacing a resource with id: ' + old.identifier)
        old.attributes = {}
        for item in new.attributes.keys():
            old.attributes[item] = new.attributes[item]
        old.attributes['occi.compute.state'] = 'inactive'


class ComputeBackend(MyBackend):
    '''
    A Backend for compute instances.
    '''

    def create(self, entity, extras):
        # e.g. check if all needed attributes are defined...

        # adding some default dummy values:
        if 'occi.compute.hostname' not in entity.attributes:
            entity.attributes['occi.compute.hostname'] = 'dummy'
        if 'occi.compute.memory' not in entity.attributes:
            entity.attributes['occi.compute.memory'] = '2'
        # rest is set by SERVICE provider...
        entity.attributes['occi.compute.architecture'] = 'x86'
        entity.attributes['occi.compute.cores'] = '2'
        entity.attributes['occi.compute.speed'] = '1'

        # trigger your management framework to start the compute instance...
        entity.attributes['occi.compute.state'] = 'inactive'
        entity.actions = [START]

        print('Creating the virtual machine with id: ' + entity.identifier)

    def retrieve(self, entity, extras):
        # trigger your management framework to get most up to date information
        pass

    def delete(self, entity, extras):
        # call the management framework to delete this compute instance...
        print('Removing representation of virtual machine with id: '
              + entity.identifier)

    def action(self, entity, action, attributes, extras):
        print attributes
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action == START:
            entity.attributes['occi.compute.state'] = 'active'
            # read attributes from action and do something with it :-)
            print('Starting virtual machine with id' + entity.identifier)
            entity.actions = [STOP, SUSPEND, RESTART]
        elif action == STOP:
            entity.attributes['occi.compute.state'] = 'inactive'
            # read attributes from action and do something with it :-)
            print('Stopping virtual machine with id' + entity.identifier)
            entity.actions = [START]
        elif action == RESTART:
            entity.attributes['occi.compute.state'] = 'active'
            # read attributes from action and do something with it :-)
            print('Restarting virtual machine with id' + entity.identifier)
            entity.actions = [STOP, SUSPEND, RESTART]
        elif action == SUSPEND:
            entity.attributes['occi.compute.state'] = 'suspended'
            # read attributes from action and do something with it :-)
            print('Suspending virtual machine with id' + entity.identifier)
            entity.actions = [START]


class NetworkBackend(MyBackend):
    '''
    Backend to handle network resources.
    '''

    def create(self, entity, extras):
        # create a VNIC...
        entity.attributes['occi.network.vlan'] = '1'
        entity.attributes['occi.network.label'] = 'dummy interface'
        entity.attributes['occi.network.state'] = 'inactive'
        entity.actions = [UP]
        print('Creating a VNIC')

    def retrieve(self, entity, extras):
        # update a VNIC
        pass

    def delete(self, entity, extras):
        # and deactivate it
        print('Removing representation of a VNIC with id:' + entity.identifier)

    def action(self, entity, action, attributes, extras):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == UP:
            entity.attributes['occi.network.state'] = 'active'
            # read attributes from action and do something with it :-)
            print('Starting VNIC with id: ' + entity.identifier)
            entity.actions = [DOWN]
        elif action.kind == DOWN:
            entity.attributes['occi.network.state'] = 'inactive'
            # read attributes from action and do something with it :-)
            print('Stopping VNIC with id: ' + entity.identifier)
            entity.actions = [UP]


class StorageBackend(MyBackend):
    '''
    Backend to handle storage resources.
    '''

    def create(self, entity, extras):
        # create a storage container here!

        entity.attributes['occi.storage.size'] = '1'
        entity.attributes['occi.storage.state'] = 'offline'
        entity.actions = [ONLINE]
        print('Creating a storage device')

    def retrieve(self, entity, extras):
        # check the state and return it!
        pass

    def delete(self, entity, extras):
        # call the management framework to delete this storage instance...
        print('Removing storage device with id: ' + entity.identifier)

    def action(self, entity, action, attributes, extras):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action == ONLINE:
            entity.attributes['occi.storage.state'] = 'online'
            # read attributes from action and do something with it :-)
            print('Bringing up storage with id: ' + entity.identifier)
            entity.actions = [BACKUP, SNAPSHOT, RESIZE]
        elif action == OFFLINE:
            entity.attributes['occi.storage.state'] = 'offline'
            # read attributes from action and do something with it :-)
            print('Bringing down storage with id: ' + entity.identifier)
            entity.actions = [ONLINE]
        elif action == BACKUP:
            print('Backing up...storage resource with id: '
                  + entity.identifier)
        elif action == SNAPSHOT:
            print('Snapshoting...storage resource with id: '
                  + entity.identifier)
        elif action == RESIZE:
            print('Resizing...storage resource with id: ' + entity.identifier)


class IpNetworkBackend(MixinBackend):
    '''
    A mixin backend for the IPnetworking.
    '''

    def create(self, entity, extras):
        if not entity.kind == NETWORK:
            raise AttributeError('This mixin cannot be applied to this kind.')
        entity.attributes['occi.network.allocation'] = 'dynamic'
        entity.attributes['occi.network.gateway'] = '10.0.0.1'
        entity.attributes['occi.network.address'] = '10.0.0.1/24'

    def delete(self, entity, extras):
        entity.attributes.pop('occi.network.allocation')
        entity.attributes.pop('occi.network.gateway')
        entity.attributes.pop('occi.network.address')


class IpNetworkInterfaceBackend(MixinBackend):
    '''
    A mixin backend for the IPnetowkringinterface.
    '''

    def create(self, entity, extras):
        if not entity.kind == NETWORKINTERFACE:
            raise AttributeError('This mixin cannot be applied to this kind.')
        entity.attributes['occi.networkinterface.address'] = '10.0.0.65'
        entity.attributes['occi.networkinterface.gateway'] = '10.0.0.1'
        entity.attributes['occi.networkinterface.allocation'] = 'dynamic'

    def delete(self, entity, extras):
        entity.attributes.pop('occi.networkinterface.address')
        entity.attributes.pop('occi.networkinterface.gateway')
        entity.attributes.pop('occi.networkinterface.allocation')


class StorageLinkBackend(KindBackend):
    '''
    A backend for the storage links.
    '''

    def create(self, entity, extras):
        entity.attributes['occi.storagelink.deviceid'] = 'sda1'
        entity.attributes['occi.storagelink.mountpoint'] = '/'
        entity.attributes['occi.storagelink.state'] = 'mounted'

    def delete(self, entity, extras):
        entity.attributes.pop('occi.storagelink.deviceid')
        entity.attributes.pop('occi.storagelink.mountpoint')
        entity.attributes.pop('occi.storagelink.state')


class NetworkInterfaceBackend(KindBackend):
    '''
    A backend for the network links.
    '''

    def create(self, link, extras):
        link.attributes['occi.networkinterface.state'] = 'up'
        link.attributes['occi.networkinterface.mac'] = 'aa:bb:cc:dd:ee:ff'
        link.attributes['occi.networkinterface.interface'] = 'eth0'

    def delete(self, link, extras):
        link.attributes.pop('occi.networkinterface.state')
        link.attributes.pop('occi.networkinterface.mac')
        link.attributes.pop('occi.networkinterface.interface')


class MyAPP(Application):
    '''
    An OCCI WSGI application.
    '''

    def __call__(self, environ, response):
        sec_obj = {'username': 'password'}
        return self._call_occi(environ, response, security=sec_obj, foo=None)

if __name__ == '__main__':
# When using own registry and custom HTMLRendering:
#    registry = NonePersistentRegistry()
#    renderings = {'text/html': HTMLRendering(registry)}
    APP = MyAPP()

    COMPUTE_BACKEND = ComputeBackend()
    NETWORK_BACKEND = NetworkBackend()
    STORAGE_BACKEND = StorageBackend()

    IPNETWORK_BACKEND = IpNetworkBackend()
    IPNETWORKINTERFACE_BACKEND = IpNetworkInterfaceBackend()

    STORAGE_LINK_BACKEND = StorageLinkBackend()
    NETWORKINTERFACE_BACKEND = NetworkInterfaceBackend()

    APP.register_backend(COMPUTE, COMPUTE_BACKEND)
    APP.register_backend(START, COMPUTE_BACKEND)
    APP.register_backend(STOP, COMPUTE_BACKEND)
    APP.register_backend(RESTART, COMPUTE_BACKEND)
    APP.register_backend(SUSPEND, COMPUTE_BACKEND)

    APP.register_backend(NETWORK, NETWORK_BACKEND)
    APP.register_backend(UP, NETWORK_BACKEND)
    APP.register_backend(DOWN, NETWORK_BACKEND)

    APP.register_backend(STORAGE, STORAGE_BACKEND)
    APP.register_backend(ONLINE, STORAGE_BACKEND)
    APP.register_backend(OFFLINE, STORAGE_BACKEND)
    APP.register_backend(BACKUP, STORAGE_BACKEND)
    APP.register_backend(SNAPSHOT, STORAGE_BACKEND)
    APP.register_backend(RESIZE, STORAGE_BACKEND)

    APP.register_backend(IPNETWORK, IPNETWORK_BACKEND)
    APP.register_backend(IPNETWORKINTERFACE, IPNETWORKINTERFACE_BACKEND)

    APP.register_backend(STORAGELINK, STORAGE_LINK_BACKEND)
    APP.register_backend(NETWORKINTERFACE, NETWORKINTERFACE_BACKEND)

    APP.register_backend(RESOURCE_TEMPLATE, MixinBackend())
    APP.register_backend(OS_TEMPLATE, MixinBackend())

    VALIDATOR_APP = validator(APP)

    HTTPD = make_server('', 8888, VALIDATOR_APP)

    HTTPD.serve_forever()

# Or when using Tornado:
#    container = tornado.wsgi.WSGIContainer(APP)
#    http_server = tornado.httpserver.HTTPServer(container)
#    http_server.listen(8888)
#    tornado.ioloop.IOLoop.instance().start()
