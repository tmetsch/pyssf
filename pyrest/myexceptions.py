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
Module containing a set of exceptions.

Created on Jul 30, 2010

@author: tmetsch
'''

class MissingCategoriesException(BaseException):
    """
    Raised when a resources has no (well-defined) category!
    """
    pass

class MissingAttributesException(BaseException):
    """
    Raised when a resource has not the right and valid attributes!
    """
    pass

class StateException(BaseException):
    """
    Raised when the resource is in an illegal/unexpected state!
    """
    pass

class MissingActionException(BaseException):
    """
    Raised when a (currently) non existing action is triggered!
    """
    pass

class SecurityException(BaseException):
    """
    Raised if a user could not be authenticated or authorized.
    """
    pass
