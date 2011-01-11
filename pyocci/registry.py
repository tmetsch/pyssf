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
Central registry for the pyocci service.

Created on Nov 11, 2010

@author: tmetsch
'''

from pyocci.backends import Backend
from pyocci.my_exceptions import AlreadyRegisteredException, \
    NoEntryFoundException

#===============================================================================
# Structs
#===============================================================================

RENDERINGS = {}
BACKENDS = {}

HOST = ''

DEFAULT_CONTENT_TYPE = 'text/plain'

#===============================================================================
# Handling of Backends
#===============================================================================

def register_backend(categories, backend):
    '''
    Registers a backend to the service.
    
    @param categories: A set of categories the backend can and will handle.
    @type categories: list
    @param backend: The backend
    @type backend: Backend
    '''
    if not isinstance(backend, Backend):
        raise AttributeError('Second argument needs to derive from Backend'
                           + ' class.')
    else:
        for category in categories:
            if category in BACKENDS.keys():
                raise AttributeError('A backend for this category is already'
                                   + ' registered.')
            else:
                BACKENDS[category] = backend

def unregister_backend(categories):
    '''
    Unregister a set of categories and their corresponding backends.
    
    @param categories: A set of categories
    @type categories: list
    '''
    for category in categories:
        for item in BACKENDS.keys():
            if category == item:
                BACKENDS.pop(item)
                break

def get_backend(category):
    """
    Retrieve a backend which is able to deal with the given category.
    
    category -- The category a backend is needed for.
    """
    for re_cat in BACKENDS.keys():
        if category == re_cat:
            return BACKENDS[re_cat]
    return Backend()

#===============================================================================
# Handling of rendering parsers
#===============================================================================

def register_parser(content_type, parser):
    '''
    Register a rendering parser to the system.
    
    @param content_type: The content type it can handle.
    @type content_type: str
    @param parser: The parser.
    @type parser: Parser
    '''
    if RENDERINGS.has_key(content_type):
        raise AlreadyRegisteredException('A Parser for this'
                                         + ' Content-type has already been'
                                         + ' registered.')
    RENDERINGS[content_type] = parser

def get_parser(content_type):
    '''
    Retrieve a parser for a given content type.
    
    @param content_type: The content type you a looking for
    @type content_type: str (can be: comma separated list)
    '''
    parser = None
    for type_str in content_type.split(','):
        if type_str.find(';q=') > -1:
            # dropping those ;q=x.x values...
            type_str = type_str[:type_str.find(';q=')]

        if RENDERINGS.has_key(type_str):
            parser = RENDERINGS[type_str]
            break
        elif type_str == '*/*':
            parser = RENDERINGS[DEFAULT_CONTENT_TYPE]
            break
    if parser is None:
        raise NoEntryFoundException('This OCCI Service is unable to'
                                    + ' understand the Content-type: '
                                    + repr(content_type))
    else:
        return parser
