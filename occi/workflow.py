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
Python module holding routines for handling resources and collections.

Created on Jun 30, 2011

@author: tmetsch
'''

from occi import registry
from occi.core_model import Resource, Link, Mixin
import uuid

# XXX: a nice storage would be nice --> not so many look ups...

#==============================================================================
# Handling of Resources & Links
#==============================================================================


def create_entity(key, entity):
    '''
    Handles all the model magic during creation of an entity.

    If it's an resource it will verify that all links are created.

    If it's a link it will ensure that source and target are properly set.

    @param key: The key for the entity.
    @param entity: The entity itself - either Link or Resource instance.
    '''
    entity.identifier = key

    # if it is an resource we create make sure we create the links properly
    if isinstance(entity, Resource):
        # if it's a resource - set/create links properly.
        for link in entity.links:
            if link.identifier is None:
                link.identifier = create_id(link.kind)
            elif link.identifier in registry.RESOURCES.keys():
                raise AttributeError('A link with that id is already present')

            for back in registry.get_all_backends(link):
                back.create(link)

            registry.RESOURCES[link.identifier] = link
    elif isinstance(entity, Link):
        entity.source.links.append(entity)

    # call all the backends who are associated with this entity.kind...
    backends = registry.get_all_backends(entity)
    for backend in backends:
        backend.create(entity)

    registry.RESOURCES[key] = entity


def delete_entity(entity):
    '''
    Handles all the model magic during deletion if an entity.

    If it's a link it will remove the link from the entity source links list.

    @param key: The key for the entity.
    @param entity: The entity itself - either Link or Resource instance.
    '''
    if isinstance(entity, Resource):
        # it's an resource - so delete all it's links
        for link in entity.links:
            for back in registry.get_all_backends(link):
                back.delete(link)
            registry.RESOURCES.pop(link.identifier)
    elif isinstance(entity, Link):
        # it's a link so update the source entity...
        # old = entity.source

        entity.source.links.remove(entity)

#        for back in registry.get_all_backends(entity.source):
#            back.update(old, entity)

    # call all the backends who are associated with this entity.kind...
    backends = registry.get_all_backends(entity)
    for backend in backends:
        backend.delete(entity)

    registry.RESOURCES.pop(entity.identifier)


def replace_entity(old, new):
    '''
    Replace an entity - backends decide what is done.

    If it's a link the entities must be replaced.

    @param old: The old entity.
    @param new: The new entity.
    '''
    if isinstance(new, Resource) and len(new.links) is not 0:
        raise AttributeError('It is not recommend to have links in a full'
                             + ' update request')

    # call all the backends who are associated with this entity.kind...
    backends = registry.get_all_backends(old)
    for backend in backends:
        backend.replace(old, new)


def update_entity(old, new):
    '''
    Update an entity - backends decide what is done.

    If it's a link the entities must be updated.

    @param old: The old entity.
    @param new: The new entity.
    '''
    if isinstance(new, Resource) and len(new.links) is not 0:
        raise AttributeError('It is not recommend to have links in a full'
                             + ' update request')

    # call all the backends who are associated with this entity.kind...
    backends = registry.get_all_backends(old)
    for backend in backends:
        backend.update(old, new)


def retrieve_entity(entity):
    '''
    Retrieves/refreshed an entity.

    If it's a link the entities must be retrieved/refreshed.

    @param entity: The entity which is to be retrieved.
    '''
    if isinstance(entity, Resource):
        # if it's a resource - retrieve all links...
        for link in entity.links:
            for back in registry.get_all_backends(link):
                back.retrieve(link)

    # call all the backends who are associated with this entity.kind...
    backends = registry.get_all_backends(entity)
    for backend in backends:
        backend.retrieve(entity)


def action_entity(entity, action):
    '''
    Performs an action on the entity.

    @param entity: The entity on which to perform the operation.
    @param action: The action definition.
    '''
    backend = registry.get_backend(action)
    backend.action(entity, action)


#==============================================================================
# Collections
#==============================================================================


def update_collection(mixin, old_entities, new_entities):
    '''
    Updates a Collection of Mixin. If not present in the current collections
    entities will be added to the collection (aka. assigned the Mixin).

    @param mixin: The mixin which defines the collection.
    @param old_entities: The entities which are in the collection to date.
    @param new_entities: The entities which should be added to the collection.
    '''
    if not isinstance(mixin, Mixin):
        raise AttributeError('This operation is only supported on Collections'
                             + ' of Mixins.')
    for entity in unique(new_entities, old_entities):
        entity.mixins.append(mixin)


def replace_collection(mixin, old_entities, new_entities):
    '''
    Replaces a Collection of Mixin. If not present in the current collections
    entities will be added to the collection (aka. assigned the Mixin). If old
    entities are not present in the new collection the mixin will be removed
    from them.

    @param mixin: The mixin which defines the collection.
    @param old_entities: The entities which are in the collection to date.
    @param new_entities: The new collection of entities.
    '''
    if not isinstance(mixin, Mixin):
        raise AttributeError('This operation is only supported on Collections'
                             + ' of Mixins.')
    for entity in unique(new_entities, old_entities):
        entity.mixins.append(mixin)
    for entity in unique(old_entities, new_entities):
        entity.mixins.remove(mixin)


def get_entities_under_path(path):
    '''
    Return all entities which fall under a path.

    If the path is in locations return all entities of the kind which defines
    the location.

    If the path is just a path return all children.

    @param path: The path under which to look...
    '''
    # TODO: add location case..., check for how deep to go into hierarchy...
    result = []
    for res in registry.RESOURCES.values():
        if res.identifier.find(path) == 0:
            result.append(res)
    return result


def filter_entities(entities, categories, attributes):
    '''
    Filters a set of entities and return those who match the given categories
    and attributes.

    @param entities: The entities which are to be filtered.
    @param categories: Categories which must be present in the entity.
    @param attributes: Attributes which must match with the entity's attrs.
    '''
    result = []
    if len(categories) == 0 and len(attributes.keys()) == 0:
        return entities

    for entity in entities:
        indy = 0
        if entity.kind in categories:
            indy += 1
        if len(intersect(categories, entity.mixins)) != 0:
            indy += 1
        for attr in intersect(attributes.keys(), entity.attributes.keys()):
            if entity.attributes[attr] == attributes[attr]:
                indy += 3

        if len(categories) > 0 and len(attributes.keys()) == 0 and indy >= 1:
            result.append(entity)
        elif len(categories) == 0 and len(attributes.keys()) > 0 and indy == 3:
            result.append(entity)
        elif len(categories) > 0 and len(attributes.keys()) > 0 and indy >= 4:
            result.append(entity)

    return result

#==============================================================================
# Convenient stuff
#==============================================================================


def create_id(kind):
    '''
    Create a key with the hierarchy of the entity encapsulated.

    @param kind: The kind which this id should be created for.
    '''
    if hasattr(kind, 'location'):
        key = kind.location
        key += str(uuid.uuid4())
    return key


def intersect(list_a, list_b):
    '''
    Returns the intersection of two lists.

    @param list_a: The first list.
    @param list_b: Another list.
    '''
    if (len(list_a) > 0 and len(list_b) > 0):
        return list(set(list_a) & set(list_b))
    else:
        return list()


def unique(list_a, list_b):
    '''
    Returns a list of elements which are only in list_a.

    @param list_a: The list to look into for unique elements.
    @param list_b: Ths list the verify against.
    '''
    return [item for item in list_a if item not in list_b]
